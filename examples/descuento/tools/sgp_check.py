#!/usr/bin/env python3
"""sgp_check.py — sensores de la metodología SGP Lite (solo librería estándar, Python 3.8+).

    python tools/sgp_check.py                     # estructura y trazabilidad (rápido)
    python tools/sgp_check.py --run               # además build/tests/lint de sgp.yaml
    python tools/sgp_check.py --stage pre-merge   # estricto: ejecuta todo + trazabilidad por requisito
    python tools/sgp_check.py --ratchet           # bloquea borrar/debilitar pruebas (git, staged)
    python tools/sgp_check.py --nuevo mi-cambio   # crea changes/CHG-00N-mi-cambio.md desde la plantilla

Mensajes escritos para que un agente sepa QUÉ falta y CÓMO corregirlo. Salida 0 = sin errores.
"""
import argparse, datetime, os, re, subprocess, sys
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
            "specs": "specs", "cambios": "changes", "tests": "tests"}


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
    v = re.sub(r"\s+#.*$", "", v).strip()
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
    if estado in ("hecho", "cancelado"):
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


def ratchet(root, cfg):
    if os.environ.get("SGP_TESTS_APPROVED") == "1":
        print("Ratchet omitido: SGP_TESTS_APPROVED=1 (aprobación humana explícita).")
        return 0
    tdir = cfg["tests"]
    proc = subprocess.run(["git", "diff", "--cached", "--numstat", "--", tdir], cwd=root, capture_output=True, text=True)
    if proc.returncode != 0:
        print("[AVISO] ratchet: no se pudo ejecutar git; se omite.")
        return 0
    bad = [(p[2], int(p[1])) for p in (l.split("\t") for l in proc.stdout.splitlines())
           if len(p) == 3 and p[1].isdigit() and int(p[1]) > 0]
    if not bad:
        return 0
    print(f"[ERROR] ratchet de pruebas: el commit elimina o modifica líneas existentes en {tdir}/")
    for path, n in bad:
        print(f"        - {path}: {n} línea(s)")
    print("        Cómo corregirlo: no borres ni debilites pruebas para hacer pasar el trabajo. "
          "Si es legítimo, pide aprobación humana y repite con SGP_TESTS_APPROVED=1.")
    return 1


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


def main():
    ap = argparse.ArgumentParser(description="Sensores SGP Lite")
    ap.add_argument("--root", default=".")
    ap.add_argument("--stage", choices=["task", "pre-merge"], default="task")
    ap.add_argument("--run", action="store_true", help="ejecuta build/tests/lint de sgp.yaml")
    ap.add_argument("--ratchet", action="store_true")
    ap.add_argument("--nuevo", metavar="NOMBRE")
    ap.add_argument("--today", help="AAAA-MM-DD (pruebas)")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    cfg, cmds = read_config(root)
    if a.ratchet:
        return ratchet(root, cfg)
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
