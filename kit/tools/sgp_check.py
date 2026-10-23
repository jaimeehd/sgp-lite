#!/usr/bin/env python3
"""sgp_check.py — sensores de la metodología SGP Lite (solo librería estándar, Python 3.8+).

    python tools/sgp_check.py                     # estructura y trazabilidad (rápido)
    python tools/sgp_check.py --run               # además build/tests/lint de sgp.yaml
    python tools/sgp_check.py --stage pre-merge   # estricto: ejecuta todo + trazabilidad por requisito
    python tools/sgp_check.py --ratchet           # bloquea borrar/debilitar pruebas (git, staged)
    python tools/sgp_check.py --commit-msg FICHERO  # valida y sella el mensaje (hook commit-msg)
    python tools/sgp_check.py --nuevo mi-cambio   # crea changes/CHG-00N-mi-cambio.md desde la plantilla

Mensajes escritos para que un agente sepa QUÉ falta y CÓMO corregirlo. Salida 0 = sin errores.
El ratchet vigila las rutas de `rutas.ratchet` (por defecto, `rutas.tests`): un renombrado que
saque una prueba de la ruta vigilada cuenta como retirada. `--commit-msg` valida la convención
del asunto y que se cite un solo `CHG-NNN`, re-ejecuta las tres puertas y sella el mensaje.
`estado: hecho` exige consistencia de cierre (criterios y tareas marcados); sus cruces externos
con specs/ y carril se omiten a propósito, porque pueden cambiar después de cerrado el cambio.
La política de commit (tope de tamaño, token de autorización y campos del sello) se configura en
`sgp.yaml` bajo `commit:` (`max_lineas`, `autorizacion`, `sello`).
"""
import argparse, datetime, fnmatch, os, re, subprocess, sys, tempfile
from pathlib import Path

ESTADOS = ["propuesta", "aplicando", "revision", "hecho", "cancelado"]
ACTIVOS = ("propuesta", "aplicando", "revision")
CARRILES = {"rapido", "normal", "mayor"}  # rapido: <1d, sin requisitos nuevos | normal: 1 dominio | mayor: cruza dominios/arquitectura/dependencias -> exige diseño y ADR
ID = r"[A-Z]{2,5}-\d{3}"
REQ_RE = re.compile(rf"^\s*-\s*\*\*({ID})\*\*\s*(.*)$")
TASK_RE = re.compile(r"^\s*-\s*\[( |x|X)\]\s+(T\d+)\b(.*)$")
TAG_RE = re.compile(rf"\[({ID}(?:\s*,\s*{ID})*)\]")
PENDING = "[POR-ACLARAR]"
VAGAS = ("adecuad", "rápid", "rapid", "intuitiv", "fácil", "facil", "robust", "eficien", "amigabl")  # raíces
SIN_PRUEBAS = re.compile(r"Ran 0 tests|no tests ran|collected 0 items|0 tests? (found|ran)|Total tests: 0"
                         r"|No test matches|Ninguna prueba coincide", re.I)  # las dos últimas: dotnet test con filtro sin coincidencias (código 0)
DEFAULTS = {"max_iteraciones_por_tarea": "5", "max_lineas_constitucion": "20",
            "specs": "specs", "cambios": "changes", "tests": "tests",
            "max_lineas": "0", "autorizacion": "Tamano-OK", "sello": "sgp_check, revision, ratchet"}


def read_version(kit_dir):
    v = kit_dir / "VERSION"
    return v.read_text(encoding="utf-8").strip() if v.exists() else "(sin VERSION)"


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, where, msg, fix=""):
        self.errors.append((where, msg, fix))

    def warn(self, where, msg, fix=""):
        self.warnings.append((where, msg, fix))

    def print(self):
        for tag, items in (("ERROR", self.errors), ("AVISO", self.warnings)):
            for where, msg, fix in items:
                print(f"[{tag}] {where}: {msg}" + (f"\n        Cómo corregirlo: {fix}" if fix else ""))
        print(f"\nResumen: {len(self.errors)} error(es), {len(self.warnings)} aviso(s).")


def strip_comment(v):
    out, quote = [], None
    for i, ch in enumerate(v):
        if quote is not None:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or v[i - 1].isspace()):
            break
        else:
            out.append(ch)
    v = "".join(out).strip()
    if len(v) >= 2 and v[0] == v[-1] == '"':
        v = v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    elif len(v) >= 2 and v[0] == v[-1] == "'":
        v = v[1:-1]
    return v.strip()


def read_config(root):
    cfg, cmds, section = dict(DEFAULTS), {}, None
    path = root / "sgp.yaml"
    if not path.exists():
        return cfg, cmds
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = re.match(r"^(\S[^:]*):\s*(#.*)?$", raw)
        if m:
            section = m.group(1).strip()
            continue
        m = re.match(r"^\s+([\w-]+):\s*(.*)$", raw)
        if m and section:
            (cmds if section == "comandos" else cfg)[m.group(1)] = strip_comment(m.group(2))
    return cfg, cmds


def frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text, re.S)
    data = {}
    for line in (m.group(1).splitlines() if m else []):
        km = re.match(r"^([\w-]+):\s*(.*)$", line)
        if km:
            data[km.group(1)] = strip_comment(km.group(2))
    return data


def as_int(v, default=None):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def spec_requirements(root, cfg, rep):
    """Devuelve {id: texto}. Valida formato EARS mínimo y duplicados."""
    reqs, base = {}, root / cfg["specs"]
    pending_files = []
    if not base.exists():
        rep.warn("specs", f"no existe {cfg['specs']}/", "crea specs/<dominio>/spec.md con tus requisitos")
        return reqs, pending_files
    for p in sorted(base.rglob("*.md")):
        if any(part.startswith("_") for part in p.relative_to(base).parts):
            continue
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8")
        if PENDING in text:
            pending_files.append(rel)
        for line in text.splitlines():
            m = REQ_RE.match(line)
            if not m:
                continue
            rid, body = m.group(1), m.group(2)
            if rid in reqs:
                rep.error(rel, f"ID de requisito duplicado {rid}", "cada requisito necesita un ID único en todo specs/")
            reqs[rid] = body
            if not re.search(r"EL SISTEMA", body, re.I):
                rep.warn(rel, f"{rid} no sigue el patrón EARS (falta «EL SISTEMA <respuesta>»)",
                         "reescríbelo: CUANDO/SI/MIENTRAS <condición>, EL SISTEMA <respuesta observable>")
            vague = [w + "…" for w in VAGAS if re.search(rf"\b{w}\w*", body, re.I)]
            if vague:
                rep.warn(rel, f"{rid} usa términos no verificables ({', '.join(vague)})",
                         "sustitúyelos por algo medible u observable (cifra, mensaje, código de salida)")
    return reqs, pending_files


def parse_change(path):
    text = path.read_text(encoding="utf-8")
    fm = frontmatter(text)
    ids = re.findall(ID, fm.get("requisitos", ""))
    tasks, cur = [], None
    for line in text.splitlines():
        tm = TASK_RE.match(line)
        if tm:
            cur = {"n": tm.group(2), "done": tm.group(1).lower() == "x", "tags": [], "block": line}
            for g in TAG_RE.findall(tm.group(3)):
                cur["tags"] += re.findall(ID, g)
            tasks.append(cur)
        elif cur is not None and (line.startswith("##") or not line.strip()):
            if line.startswith("##"):
                cur = None
        elif cur is not None:
            cur["block"] += "\n" + line
    manual = ""
    mm = re.search(r"^##\s+Verificación manual\s*\n(.*?)(?=^##\s|\Z)", text, re.S | re.M)
    if mm:
        manual = mm.group(1)
    return text, fm, ids, tasks, manual


def check_change(path, reqs, rep_main, today, cfg):
    name = path.stem
    rep = rep_main
    text, fm, ids, tasks, manual = parse_change(path)
    carril, estado = fm.get("carril", "normal"), fm.get("estado", "")
    if carril not in CARRILES:
        rep.error(name, f"carril inválido '{carril}'", "usa rapido, normal o mayor")
        return None
    if estado not in ESTADOS:
        rep.error(name, f"estado inválido '{estado}'", "usa: " + ", ".join(ESTADOS))
        return None
    if estado == "cancelado":
        return None
    if estado == "hecho":
        # Cierre duro: un cambio 'hecho' ya no se verifica entero (los cruces con
        # specs/ pueden cambiar después de cerrado), pero su CONSISTENCIA de cierre
        # sí se exige: sin esto, 'hecho' apagaba los sensores sin comprobar nada.
        mm = re.search(r"^##\s+Criterios de finalización[^\n]*\n(.*?)(?=^##\s|\Z)", text, re.S | re.M)
        if not mm:
            rep.error(name, "estado 'hecho' sin sección «## Criterios de finalización»",
                      "recupera la sección y márcala con [x], o vuelve a 'aplicando'")
        else:
            criterios = re.findall(r"^\s*[-*+]\s*\[([ xX])\]\s*(.*)$", mm.group(1), re.M)
            abiertos = [txt for marca, txt in criterios if marca == " "]
            if not criterios:
                rep.error(name, "estado 'hecho' sin criterios de finalización",
                          "escribe al menos un criterio verificable y márcalo [x]")
            elif abiertos:
                rep.error(name, f"estado 'hecho' con {len(abiertos)} criterio(s) sin marcar: "
                                f"{'; '.join((a or '(sin texto)')[:60] for a in abiertos[:3])}",
                          "marca con [x] solo lo que de verdad se cumple, o vuelve a 'aplicando'")
        if not tasks:
            rep.error(name, "estado 'hecho' sin tareas", "añade las tareas que se ejecutaron o vuelve a 'aplicando'")
        pend = [t["n"] for t in tasks if not t["done"]]
        if pend:
            rep.error(name, f"estado 'hecho' con tareas pendientes ({', '.join(pend)})",
                      "termina las tareas o vuelve a 'aplicando'")
        sin_hc = [t["n"] for t in tasks if "hecho cuando" not in t["block"].lower()]
        if sin_hc:
            rep.error(name, f"tarea(s) de un cambio hecho sin «Hecho cuando:» ({', '.join(sin_hc)})",
                      "añade la condición verificable que se cumplió")
        if PENDING in text:
            rep.error(name, f"contiene marcas {PENDING} sin resolver", "resuélvelas con el humano y elimina la marca")
        return None
    if estado == "propuesta":          # un borrador no bloquea: sus errores se degradan a avisos
        rep = Report()
    apetito = as_int(fm.get("apetito_dias"))
    if not apetito or apetito < 1:
        rep.error(name, "apetito_dias ausente o inválido", "define apetito_dias (entero >= 1) en el frontmatter")
    if PENDING in text and estado != "propuesta":
        rep.error(name, f"contiene marcas {PENDING} sin resolver", "resuélvelas con el humano y elimina la marca")
    if "## Criterios de finalización" not in text:
        rep.error(name, "falta la sección «## Criterios de finalización»", "copia la sección de changes/_plantilla.md")
    if carril == "mayor":
        if "## Diseño" not in text or not re.search(r"##\s*Diseño.{0,400}Alternativa", text, re.S | re.I):
            rep.error(name, "carril 'mayor' sin sección «## Diseño» con una alternativa descartada",
                      "añade ## Diseño con: enfoque, alternativa considerada y por qué se descarta, y contratos/datos afectados")
        if not re.search(r"ADR-\d{4}", text) and not (Path(path).parent.parent / "docs" / "adr").exists():
            rep.warn(name, "carril 'mayor' sin referencia a un ADR", "si hay una decisión estructural, créalo en docs/adr/ y enlázalo (ADR-NNNN)")
    dominios_tocados = {rid.split("-")[0] for rid in re.findall(ID, fm.get("requisitos", ""))}
    if carril == "normal" and len(dominios_tocados) > 1:
        rep.warn(name, f"toca {len(dominios_tocados)} dominios ({', '.join(sorted(dominios_tocados))}) en carril 'normal'",
                 "si hay una decisión de arquitectura o contrato entre dominios, sube a carril 'mayor' (más seguro subir de más que de menos)")
    if estado != "propuesta" or tasks:
        if not tasks:
            rep.error(name, "no hay tareas", "añade tareas `- [ ] T001 [ID] descripción` con «Hecho cuando:»")
    for t in tasks:
        if "hecho cuando" not in t["block"].lower():
            rep.error(name, f"la tarea {t['n']} no tiene «Hecho cuando:»",
                      "añade una línea `Hecho cuando: <condición verificable>` bajo la tarea")
        if carril == "normal" and not t["tags"]:
            rep.error(name, f"la tarea {t['n']} no enlaza a ningún requisito",
                      f"añade el ID entre corchetes, p. ej. `- [ ] {t['n']} [DOM-001] descripción`")
    if carril == "normal" and estado != "propuesta" and not ids:
        rep.error(name, "carril normal sin requisitos", "lista los IDs afectados en `requisitos: [DOM-001]` (primero en specs/) o usa carril rapido")
    for rid in ids:
        if rid not in reqs:
            rep.error(name, f"el requisito {rid} no existe en specs/",
                      "la spec manda: escríbelo primero en specs/<dominio>/spec.md (y apruébalo) antes de tareas o código")
    tagged = {i for t in tasks for i in t["tags"]}
    for tid in sorted(tagged - set(ids)):
        rep.error(name, f"una tarea cita {tid}, que no está en `requisitos:`", "añádelo a `requisitos:` o corrige el ID")
    if carril == "normal" and tasks:
        for rid in ids:
            if rid not in tagged:
                rep.error(name, f"el requisito {rid} no está cubierto por ninguna tarea", f"añade una tarea con [{rid}]")
    if estado == "aplicando":
        try:
            start = datetime.date.fromisoformat(fm.get("inicio", ""))
        except ValueError:
            start = None
        if start is None:
            rep.error(name, "estado 'aplicando' sin `inicio: AAAA-MM-DD`", "rellena la fecha de inicio")
        elif apetito and (today - start).days > apetito:
            rep.error(name, f"presupuesto agotado: {(today - start).days} d transcurridos, apetito {apetito} d",
                      "NO extender. Decide: reformular (cambio nuevo y más pequeño) o cancelar (estado: cancelado)")
    if estado == "revision" and any(not t["done"] for t in tasks):
        pend = ", ".join(t["n"] for t in tasks if not t["done"])
        rep.error(name, f"estado 'revision' con tareas pendientes ({pend})", "termina las tareas o vuelve a 'aplicando'")
    if rep is not rep_main:
        for where, msg, fix in rep.errors + rep.warnings:
            rep_main.warn(where, msg + " (borrador)", fix)
    return {"name": name, "estado": estado, "ids": ids, "manual": manual, "carril": carril}


def run_shell(cmd, root):
    return subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True)


def trace(root, cmds, info, rep):
    """Ejecuta las pruebas de cada requisito del cambio y devuelve filas (id, estado)."""
    tpl = cmds.get("test_por_requisito", "")
    rows = []
    for rid in info["ids"]:
        manual_ok = any(rid in ln and re.search(r"\bOK\b", ln) for ln in info["manual"].splitlines())
        if tpl:
            proc = run_shell(tpl.replace("{id_py}", rid.replace("-", "_")).replace("{id}", rid), root)
            out = proc.stdout + proc.stderr
            if proc.returncode == 5 or (proc.returncode == 0 and SIN_PRUEBAS.search(out)):
                status = "sin pruebas"
            elif proc.returncode == 0:
                status = "ok"
            else:
                status = "falla"
        else:
            status = "no configurado"
        if status != "ok" and manual_ok:
            status = "manual OK"
        rows.append((rid, status))
        if status not in ("ok", "manual OK"):
            fix = {"sin pruebas": f"escribe una prueba cuyo nombre incluya {rid.replace('-', '_')} (o una fila OK en «Verificación manual»)",
                   "falla": f"corrige la causa; ejecuta a mano: {tpl.replace('{id_py}', rid.replace('-', '_')).replace('{id}', rid)}",
                   "no configurado": "define comandos.test_por_requisito en sgp.yaml o verifica manualmente con una fila OK"}[status]
            rep.error(f"{info['name']}/{rid}", f"requisito sin cobertura comprobada ({status})", fix)
    return rows


def run_commands(root, cmds, rep, strict):
    for name in ("build", "tests", "lint"):
        cmd = cmds.get(name, "")
        if not cmd:
            fix = f"define comandos.{name} en sgp.yaml (un sensor sin comprobación real no cuenta como 'pasó')"
            (rep.error if strict and name != "lint" else rep.warn)("sgp.yaml", f"sensor '{name}' sin configurar", fix)
            continue
        print(f"-> {name}: {cmd}")
        proc = run_shell(cmd, root)
        if proc.returncode != 0:
            tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-30:])
            rep.error(f"comando:{name}", f"falló con código {proc.returncode}\n{tail}",
                      "corrige la causa; no borres ni debilites pruebas para hacerlo pasar")


def check_constitution(root, cfg, rep, strict):
    p = root / "docs" / "constitution.md"
    lvl = rep.error if strict else rep.warn
    if not p.exists():
        lvl("constitución", "falta docs/constitution.md", "copia la plantilla y adapta los principios")
        return
    lines = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    mx = as_int(cfg["max_lineas_constitucion"], 20)
    if len(lines) > mx:
        rep.warn("constitución", f"{len(lines)} líneas (máx. {mx})", "recórtala: solo principios innegociables y verificables")
    blocks, cur = [], None
    for l in lines:
        if re.match(r"^\d+\.\s", l):
            cur = [l]
            blocks.append(cur)
        elif cur is not None:
            cur.append(l)
    if not blocks:
        rep.warn("constitución", "no hay principios numerados", "escribe principios como `1. **Nombre**: regla. Verificado por: …`")
    for b in blocks:
        if "verificado por" not in " ".join(b).lower():
            lvl("constitución", f"el principio «{b[0][:50]}…» no declara «Verificado por:»",
                "indica el sensor (tests, ratchet, estructura, lint) o «humano»")


def _patrones_ratchet(cfg):
    """Rutas vigiladas por el ratchet: `rutas.ratchet` (varias, separadas por coma, admite
    comodines) y, si no está, `rutas.tests` por compatibilidad con proyectos existentes."""
    crudo = cfg.get("ratchet") or cfg.get("tests") or "tests"
    return [p.strip() for p in crudo.split(",") if p.strip()]


def _cubierto(ruta, patron):
    if any(ch in patron for ch in "*?["):
        return fnmatch.fnmatch(ruta, patron)
    base = patron.rstrip("/")
    return ruta == base or ruta.startswith(base + "/")


def _universo_versionado(root, env):
    """Rutas versionadas: índice + árbol de HEAD. Un borrado staged sale del índice pero sigue
    en HEAD; sin sumar HEAD, borrar TODA la suite vigilada parecía «nada que vigilar» y pasaba
    en verde (el caso que el ratchet existe para impedir). None = git no responde."""
    rutas = set()
    ls = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True,
                        encoding="utf-8", errors="replace", env=env)
    if ls.returncode != 0:
        return None
    rutas.update(f for f in ls.stdout.split("\0") if f)
    he = subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", "HEAD"], cwd=root,
                        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if he.returncode == 0:              # sin HEAD (primer commit) no hay árbol que sumar
        rutas.update(f for f in he.stdout.split("\0") if f)
    return rutas


def _rutas_head(root, env):
    """Rutas del árbol de HEAD: un binario borrado o modificado no aparece como líneas en
    `--numstat`, hay que saber si ya existía para no confundir un alta con una retirada."""
    p = subprocess.run(["git", "ls-tree", "-r", "-z", "--name-only", "HEAD"], cwd=root,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return set(f for f in p.stdout.split("\0") if f) if p.returncode == 0 else set()


def ratchet(root, cfg):
    """Devuelve (rc, detalle): el detalle alimenta el sello del commit-msg. Si no hay
    pruebas vigiladas NO se calla: avisa y lo deja escrito en el sello (nunca verde silencioso)."""
    if os.environ.get("SGP_TESTS_APPROVED") == "1":
        print("Ratchet omitido: SGP_TESTS_APPROVED=1 (aprobación humana explícita).")
        return 0, "omitido"
    patrones = _patrones_ratchet(cfg)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    universo = _universo_versionado(root, env)
    if universo is None:
        print("[ERROR] ratchet: no se pudo ejecutar git; no se puede verificar el staged (falla cerrado).")
        return 1, "sin-git"
    vigilados = [f for f in universo if any(_cubierto(f, p) for p in patrones)]
    en_head = _rutas_head(root, env)
    if not vigilados:
        print(f"[AVISO] ratchet: nada que vigilar; ningún fichero versionado sigue la ruta "
              f"'{', '.join(patrones)}'.")
        print("        Cómo corregirlo: crea tus pruebas (p. ej. tests/) o define la ruta real "
              "con `ratchet:` en la sección `rutas:` de sgp.yaml.")
        return 0, "sin-tests"
    pr = subprocess.run(["git", "diff", "--cached", "--numstat", "-z"], cwd=root, capture_output=True,
                        text=True, encoding="utf-8", errors="replace", env=env)
    if pr.returncode != 0:
        print("[ERROR] ratchet: no se pudo ejecutar git diff; no se puede verificar el staged (falla cerrado).")
        return 1, "sin-git"
    bad = []
    regs = [r for r in pr.stdout.split("\0") if r]
    i = 0
    while i < len(regs):
        p = regs[i].split("\t", 2)
        if len(p) == 3 and p[2] == "" and i + 2 < len(regs):
            # renombrado (`-z`: add\tdel\t\0vieja\0nueva\0): retirar una prueba de la ruta
            # vigilada no puede pasar en verde, y renombrar debilitando tampoco.
            vieja, nueva = regs[i + 1], regs[i + 2]
            i += 3
            if not any(_cubierto(vieja, q) for q in patrones):
                continue                           # no era una prueba vigilada
            borradas = int(p[1]) if p[1].isdigit() else (1 if p[1] == "-" else 0)
            if borradas > 0:
                bad.append((f"{vieja} (renombrada y modificada)", borradas))
            elif not any(_cubierto(nueva, q) for q in patrones):
                bad.append((f"{vieja} -> {nueva} (fuera de la ruta vigilada)", 0))
            continue
        i += 1
        if len(p) != 3:
            continue
        cubierto = any(_cubierto(p[2], q) for q in patrones)
        if p[1].isdigit() and int(p[1]) > 0 and cubierto:
            bad.append((p[2], int(p[1])))
        elif p[1] == "-" and cubierto and p[2] in en_head:
            # binario vigilado modificado o borrado: no hay líneas que contar (un alta no cuenta)
            bad.append((f"{p[2]} (binario vigilado modificado o borrado)", 0))
    if not bad:
        return 0, "0 bloq"
    print(f"[ERROR] ratchet de pruebas: el commit elimina o modifica líneas existentes en "
          f"{', '.join(patrones)}")
    for path, n in bad:
        print(f"        - {path}: {n} línea(s)" if n else f"        - {path}")
    print("        Cómo corregirlo: no borres ni debilites pruebas para hacer pasar el trabajo. "
          "Si es legítimo, pide aprobación humana y repite con SGP_TESTS_APPROVED=1.")
    return 1, f"{len(bad)} bloq"


def nuevo(root, cfg, slug):
    cdir = root / cfg["cambios"]
    tpl = cdir / "_plantilla.md"
    if not tpl.exists():
        print(f"No existe {tpl}"); return 1
    nums = [int(m.group(1)) for p in cdir.glob("CHG-*.md") if (m := re.match(r"CHG-(\d+)", p.name))]
    n = max(nums, default=0) + 1
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
    dest = cdir / f"CHG-{n:03d}-{slug}.md"
    dest.write_text(tpl.read_text(encoding="utf-8").replace("CHG-000", f"CHG-{n:03d}", 1), encoding="utf-8")
    print(f"Creado {dest.relative_to(root).as_posix()}")
    return 0


CONVENCIONAL = re.compile(r"^(feat|fix|docs|test|refactor|perf|style|build|ci|chore|revert)"
                          r"(\([A-Za-z0-9._/-]+\))?!?: \S")
SIN_SELLO = ("Merge ", "Revert ", "amend! ", "fixup! ", "squash! ")
TIJERA = "# ------------------------ >8 ------------------------"


def _limpiar_mensaje(texto):
    """Deja solo el mensaje: corta en la tijera de `git commit -v` y descarta las líneas de
    comentario que Git añade al fichero (estado, ficheros, diff). Sin esto, el diff podía citar
    otros CHG y rechazar un mensaje correcto, y el sello quedaba tras la tijera: Git lo
    descartaba al limpiar el mensaje y el hook decía haberlo añadido."""
    lineas = []
    for l in texto.splitlines():
        if l.startswith(TIJERA):
            break
        if l.startswith("#"):
            continue
        lineas.append(l)
    limpio = "\n".join(lineas).strip("\n")
    return (limpio + "\n") if limpio.strip() else ""


def _sin_sello(texto):
    """Quita los sellos `Gate:` finales: un reintento o un rebase no duplica la línea."""
    lineas = texto.splitlines()
    while lineas and (not lineas[-1].strip() or lineas[-1].startswith("Gate: ")):
        lineas.pop()
    return ("\n".join(lineas).rstrip() + "\n") if lineas else ""


def _puerta_estructura(root, today=None):
    """Sensores de estructura sobre el ÍNDICE (lo que se va a commitear), materializado en un
    temporal: el árbol de trabajo puede diferir de lo staged y el sello debe hablar del commit,
    no de una versión que no se está confirmando. Devuelve N errores o None si está en rojo."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        idx = subprocess.run(["git", "checkout-index", "-a", "-f", f"--prefix={Path(tmp).as_posix()}/"],
                             cwd=root, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", env=env)
        if idx.returncode != 0:
            print("[ERROR] commit-msg: no se pudo materializar el índice para validar la estructura:")
            print(idx.stdout + idx.stderr)
            return None
        cmd = [sys.executable, str(Path(__file__).resolve()), "--root", tmp]
        if today:
            cmd += ["--today", today]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    salida = p.stdout + p.stderr
    if p.returncode != 0:
        print("[ERROR] commit-msg: los sensores de estructura están en rojo:")
        print(salida)
        return None
    m = re.search(r"Resumen: (\d+) error", salida)
    return int(m.group(1)) if m else 0


def _puerta_revision(root):
    """Puerta de revisión contra el staged. Devuelve (veredicto, rc)."""
    script = Path(__file__).with_name("sgp_review.py")
    if not script.is_file():
        print(f"[ERROR] commit-msg: falta {script.name} junto a sgp_check.py; "
              "reinstala las herramientas del kit y el hook.")
        return "ausente", 1
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, str(script), "--root", str(root)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if p.returncode != 0:
        print("[ERROR] commit-msg: la puerta de revisión está en rojo:")
        print(p.stdout + p.stderr)
        return "FALLA", 1
    return ("INACTIVA" if "INACTIVA" in p.stdout else "OK"), 0


CAMPOS_SELLO = ("sgp_check", "revision", "ratchet", "tamano", "ficheros")


def _campos_sello(cfg):
    """Campos del sello configurados en `commit.sello` (por defecto, los tres clásicos)."""
    crudo = cfg.get("sello") or "sgp_check, revision, ratchet"
    return [c.strip() for c in crudo.split(",") if c.strip()]


def _tamano_staged(root, env):
    """(líneas cambiadas, ficheros) del índice. `--numstat` da `-` en binarios: cuentan 1."""
    p = subprocess.run(["git", "diff", "--cached", "--numstat", "-z"], cwd=root, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env)
    if p.returncode != 0:
        return None
    lineas = ficheros = 0
    regs = [r for r in p.stdout.split("\0") if r]
    i = 0
    while i < len(regs):
        parts = regs[i].split("\t", 2)
        i += 1
        if len(parts) != 3:
            continue
        if parts[2] == "" and i + 1 < len(regs):   # renombrado: `-z` añade vieja y nueva
            i += 2
        ficheros += 1
        if parts[0] == "-" or parts[1] == "-":     # binario
            lineas += 1
        else:
            lineas += int(parts[0] or 0) + int(parts[1] or 0)
    return lineas, ficheros


def _sello(campos, n_err, verd, detalle, lineas, ficheros, max_lineas):
    piezas = []
    for c in campos:
        if c == "sgp_check":
            piezas.append(f"sgp_check {n_err} err")
        elif c == "revision":
            piezas.append(f"sgp_review {verd}")
        elif c == "ratchet":
            piezas.append(f"ratchet {detalle}")
        elif c == "tamano":
            piezas.append(f"tamano {lineas}/{max_lineas if max_lineas > 0 else '-'}")
        elif c == "ficheros":
            piezas.append(f"ficheros {ficheros}")
    return "Gate: " + " | ".join(piezas)


def commit_msg(fichero, root, cfg, today=None):
    """Puerta del mensaje de commit (hook commit-msg): valida el mensaje, mide el tamaño del
    staged, re-ejecuta las tres puertas (estructura sobre el índice, revisión y ratchet) y SELLA
    el resultado (Gate: ...) con los campos de `commit.sello`. Falla cerrado."""
    if not fichero or not Path(fichero).is_file():
        print("[ERROR] commit-msg: no llega el fichero del mensaje; sin mensaje no se puede validar ni sellar.")
        print("        Cómo corregirlo: reinstala el hook (cp tools/commit-msg .git/hooks/commit-msg).")
        return 1
    try:
        bruto = Path(fichero).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print("[ERROR] commit-msg: el mensaje no está en UTF-8 (revisa i18n.commitEncoding); "
              "conviértelo y repite, o usa `git commit --no-verify` si es imprescindible.")
        return 1
    except OSError as exc:
        print(f"[ERROR] commit-msg: no se puede leer el mensaje: {exc}")
        return 1
    texto = _limpiar_mensaje(bruto)
    if not texto.strip():
        print("[ERROR] commit-msg: el mensaje está vacío (solo comentarios o en blanco).")
        return 1
    asunto = next(l for l in texto.splitlines() if l.strip())
    if asunto.startswith(SIN_SELLO):
        return 0                     # merge/revert/fixup/squash/amend: sin sello (no aportan alcance)
    if not CONVENCIONAL.match(asunto):
        print(f"[ERROR] commit-msg: el asunto no sigue la convención (tipo[alcance]: asunto): {asunto}")
        print('        Cómo corregirlo: p. ej. "feat(tools): añade la guarda X" o "docs: corrige Y".')
        return 1
    chgs = sorted(set(re.findall(r"CHG-\d{3}", texto)))
    if len(chgs) > 1:
        print(f"[ERROR] commit-msg: el mensaje menciona {len(chgs)} cambios distintos ({', '.join(chgs)});")
        print("        Un commit = un alcance. Divide el trabajo en commits separados.")
        return 1
    campos = _campos_sello(cfg)
    desconocidos = [c for c in campos if c not in CAMPOS_SELLO]
    if desconocidos:
        print(f"[ERROR] commit-msg: campo(s) de sello desconocido(s) en `commit.sello`: "
              f"{', '.join(desconocidos)}; usa: {', '.join(CAMPOS_SELLO)}.")
        return 1
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    max_lineas = as_int(cfg.get("max_lineas"), 0) or 0
    token = (cfg.get("autorizacion") or "Tamano-OK").strip() or "Tamano-OK"
    tam = _tamano_staged(root, env)
    if tam is None:
        print("[ERROR] commit-msg: no se pudo medir el staged (git diff); no se puede verificar "
              "el tamaño (falla cerrado).")
        return 1
    lineas, ficheros = tam
    if max_lineas > 0 and lineas > max_lineas and not re.search(rf"^{re.escape(token)}:\s*\S", texto, re.M):
        print(f"[ERROR] commit-msg: el commit cambia {lineas} línea(s) y el tope es {max_lineas}.")
        print(f"        Cómo corregirlo: divide el commit, o autorízalo con una línea "
              f"«{token}: autorizado por <quien> · <motivo>».")
        return 1
    n_err = _puerta_estructura(root, today)
    if n_err is None:
        return 1
    verd, rc = _puerta_revision(root)
    if rc != 0:
        return 1
    rc, detalle = ratchet(root, cfg)
    if rc != 0:
        return 1
    sello = _sello(campos, n_err, verd, detalle, lineas, ficheros, max_lineas)
    try:
        Path(fichero).write_text(_sin_sello(texto) + "\n" + sello + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"[ERROR] commit-msg: no se puede escribir el sello en el mensaje: {exc}")
        return 1
    print(f"[commit-msg] puertas en verde; sello añadido al mensaje: {sello}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Sensores SGP Lite")
    ap.add_argument("--root", default=".")
    ap.add_argument("--stage", choices=["task", "pre-merge"], default="task")
    ap.add_argument("--run", action="store_true", help="ejecuta build/tests/lint de sgp.yaml")
    ap.add_argument("--ratchet", action="store_true")
    ap.add_argument("--commit-msg", metavar="FICHERO", dest="commit_msg",
                    help="valida y sella el mensaje de commit (uso interno del hook: Git pasa .git/COMMIT_EDITMSG)")
    ap.add_argument("--nuevo", metavar="NOMBRE")
    ap.add_argument("--today", help="AAAA-MM-DD (pruebas)")
    ap.add_argument("--version", action="store_true", help="muestra la versión del kit y sale")
    a = ap.parse_args()
    if a.version:
        print(read_version(Path(__file__).resolve().parent.parent))
        return 0
    root = Path(a.root).resolve()
    cfg, cmds = read_config(root)
    if a.commit_msg is not None:      # "" llega vacío: commit_msg falla cerrado
        if a.ratchet or a.nuevo:
            print("[ERROR] --commit-msg no se combina con --ratchet ni --nuevo.")
            return 1
        return commit_msg(a.commit_msg, root, cfg, a.today)
    if a.ratchet:
        rc, _ = ratchet(root, cfg)
        return rc
    if a.nuevo:
        return nuevo(root, cfg, a.nuevo)
    today = datetime.date.fromisoformat(a.today) if a.today else datetime.date.today()
    strict = a.stage == "pre-merge"
    rep = Report()
    if not (root / "AGENTS.md").exists():
        rep.error("proyecto", "falta AGENTS.md", "copia la plantilla y completa comandos y reglas")
    if not (root / "sgp.yaml").exists():
        rep.error("proyecto", "falta sgp.yaml", "copia la plantilla y define los comandos")
    check_constitution(root, cfg, rep, strict)
    reqs, pending = spec_requirements(root, cfg, rep)
    cdir = root / cfg["cambios"]
    infos = []
    if cdir.exists():
        for p in sorted(cdir.glob("CHG-*.md")):
            info = check_change(p, reqs, rep, today, cfg)
            if info:
                infos.append(info)
    else:
        rep.warn("proyecto", f"no existe {cfg['cambios']}/", "créala y copia changes/_plantilla.md")
    if pending:
        any_active = any(i["estado"] in ("aplicando", "revision") for i in infos)
        (rep.error if (strict or any_active) else rep.warn)(
            ", ".join(pending), f"contiene marcas {PENDING} sin resolver", "resuélvelas antes de implementar (prompt de QA de spec)")
    if a.run or strict:
        run_commands(root, cmds, rep, strict)
    if strict:
        en_revision = [i for i in infos if i["estado"] == "revision"]
        targets = [i for i in en_revision if i["carril"] in ("normal", "mayor")]
        if not en_revision:
            rep.warn("pre-merge", "no hay cambios en estado 'revision'", "pasa el cambio a 'revision' cuando todas sus tareas estén hechas")
        elif not targets:
            print(f"(cambios en revisión sin trazabilidad por requisito, carril rapido: {', '.join(i['name'] for i in en_revision)})")
        for info in targets:
            rows = trace(root, cmds, info, rep)
            print(f"\nTrazabilidad {info['name']}:")
            for rid, st in rows:
                print(f"  {rid:<9} {st}")
            print()
    rep.print()
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
