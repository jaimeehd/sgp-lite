#!/usr/bin/env python3
"""sgp_docs.py — auditor de documentación del cambio en curso (aviso, no veredicto).

Descubre con git y búsquedas reales qué documentos del proyecto mencionan lo que la
tarea cambió, y clasifica cada documento para no tocar historia ni guías. No edita
nada: solo lista. Su salida alimenta el cierre (política §2.4 y §16.5).

    python tools/sgp_docs.py
    python tools/sgp_docs.py --root <proyecto> --base HEAD

Secciones de salida:
  1) cambios detectados (git diff + archivos nuevos sin seguimiento);
  2) menciones por término, con archivo:línea y tipo de documento;
  3) plantilla de la tabla de cierre prellenada.
Sin git: imprime el guion de inventario manual de §16.5 punto 5.

Solo librería estándar (Python 3.8+). Código de salida: 0 si se pudo leer el
proyecto (es un aviso, no bloquea); 2 si la carpeta no existe.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

MAX_TERMINOS = 40
MAX_MENCIONES = 5
EXT_TEXTO = {".py", ".js", ".ts", ".cs", ".java", ".go", ".rs", ".rb", ".php", ".md",
             ".yml", ".yaml", ".json", ".sh", ".ps1", ".vb", ".sql", ".html", ".css"}
DOCS_RAIZ = ("README.md", "CHANGELOG.md", "AGENTS.md")
DIRECTORIOS_DOCS = ("docs", ".clean", "specs", "changes", "skills", "kit")
PATRON_DEF = re.compile(r"\b(?:def|class|function|func|fn)\s+([A-Za-z_][A-Za-z0-9_]{2,})")
PATRON_ID = re.compile(r"\b[A-Z]{2,5}-\d{3}\b")
DOCS_GUIA = ("METODOLOGIA.MD", "ADOPCION.MD", "PROMPTS.MD")
TERMINOS_GENERICOS = {"main", "init", "setup", "test", "tests", "run", "get", "set",
                      "add", "new", "update", "commit", "crear", "escribir", "leer",
                      "guardar"}


def ejecutar_git(root, *args):
    """Ejecuta git de solo lectura; devuelve stdout o None si git falla."""
    try:
        r = subprocess.run(["git", "-C", str(root)] + list(args),
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def cambios(root, base="HEAD"):
    """Rutas cambiadas (árbol de trabajo + índice + nuevos) o None si no hay git."""
    if ejecutar_git(root, "rev-parse", "--is-inside-work-tree") is None:
        return None
    rutas = []
    salida = ejecutar_git(root, "diff", "--name-only", base) or ""
    for linea in salida.splitlines():
        if linea.strip():
            rutas.append(linea.strip())
    otros = ejecutar_git(root, "ls-files", "--others", "--exclude-standard") or ""
    for linea in otros.splitlines():
        if linea.strip() and linea.strip() not in rutas:
            rutas.append(linea.strip())
    return sorted(rutas)


def terminos(root, rutas):
    """Nombres de archivo y símbolos nuevos que merecen buscarse en la documentación."""
    vistos, encontrados = set(), []

    def anadir(t):
        t = t.strip()
        if len(t) >= 4 and t.lower() not in vistos and t.lower() not in TERMINOS_GENERICOS:
            vistos.add(t.lower())
            encontrados.append(t)

    for rel in rutas:
        ruta = root / rel
        anadir(ruta.stem)
        anadir(ruta.name)
        if ruta.suffix.lower() in EXT_TEXTO and ruta.is_file():
            try:
                if ruta.stat().st_size > 400_000:
                    continue
                texto = ruta.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in PATRON_DEF.finditer(texto):
                anadir(m.group(1))
            for m in PATRON_ID.finditer(texto):
                anadir(m.group(0))
        if len(encontrados) >= MAX_TERMINOS:
            break
    return encontrados[:MAX_TERMINOS]


def documentos(root):
    """Documentos que se revisan (rutas relativas con «/»), ordenados."""
    docs = []
    for nombre in DOCS_RAIZ:
        if (root / nombre).is_file():
            docs.append(nombre)
    for carpeta in DIRECTORIOS_DOCS:
        base = root / carpeta
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            try:
                rel = p.relative_to(root).as_posix()
            except ValueError:
                continue
            if rel not in docs:
                docs.append(rel)
    return docs


def etiqueta(rel):
    """VIGENTE = comportamiento actual; HISTORIA = no se toca; GUIA = plantilla o skill."""
    p = rel.replace("\\", "/")
    nombre = p.rsplit("/", 1)[-1].upper()
    if ("CHANGELOG" in nombre or p.startswith(".clean/") or p.startswith("changes/")
            or p.startswith("docs/plan-") or p.startswith("docs/adr/") or "/adr/" in p):
        return "HISTORIA"
    if p.startswith("skills/") or p.startswith("kit/") or nombre in DOCS_GUIA:
        return "GUIA"
    return "VIGENTE"


def menciones(root, terms, docs):
    """{termino: [(documento, linea, etiqueta, texto)]} con tope por término."""
    resultado = {}
    for t in terms:
        hallados = []
        for rel in docs:
            try:
                lineas = (root / rel).read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for i, linea in enumerate(lineas, 1):
                if t in linea:
                    hallados.append((rel, i, etiqueta(rel), linea.strip()))
                    if len(hallados) >= MAX_MENCIONES:
                        break
            if len(hallados) >= MAX_MENCIONES:
                break
        if hallados:
            resultado[t] = hallados
    return resultado


def render(root, base="HEAD"):
    """Texto completo del auditor."""
    lineas = []
    cams = cambios(root, base)
    if cams is None:
        lineas.append("SIN GIT — inventario por diff no disponible (política §16.5, punto 5).")
        lineas.append("Guion manual: lista los archivos que tocó la tarea y busca sus nombres con grep en")
        lineas.append("README.md, CHANGELOG.md, AGENTS.md, docs/**, .clean/**, specs/**, changes/** y skills/**.")
        return "\n".join(lineas)
    if not cams:
        return "Sin cambios pendientes: git diff " + base + " está vacío."
    lineas.append("== 1) Cambios detectados (git diff " + base + " + nuevos sin seguimiento) ==")
    for rel in cams:
        lineas.append("- " + rel)
    terms = terminos(root, cams)
    docs = documentos(root)
    mapa = menciones(root, terms, docs) if terms else {}
    lineas.append("")
    lineas.append("== 2) Menciones en documentación (universo: {} documentos) ==".format(len(docs)))
    if not terms:
        lineas.append("(sin términos buscables en los cambios)")
    elif not mapa:
        lineas.append("(sin apariciones: ningún documento menciona lo cambiado)")
    vivos = []
    for t in terms:
        if t not in mapa:
            continue
        lineas.append("- «" + t + "»")
        for rel, i, tipo, texto in mapa[t]:
            recorte = texto if len(texto) <= 100 else texto[:97] + "..."
            lineas.append("    {}:{} [{}] {}".format(rel, i, tipo, recorte))
            if tipo == "VIGENTE" and rel not in vivos:
                vivos.append(rel)
    lineas.append("")
    lineas.append("Leyenda: VIGENTE = describe el comportamiento actual (revisar y actualizar);")
    lineas.append("         HISTORIA = no se toca (solo entrada NUEVA en el CHANGELOG o decisión nueva);")
    lineas.append("         GUIA = plantilla o skill: no se toca salvo que el cambio lo exija por diseño.")
    lineas.append("")
    lineas.append("== 3) Plantilla de cierre (política §2.4 / §16.5) ==")
    lineas.append("| Archivo | Sección | Qué cambió | Cómo lo verificaste |")
    lineas.append("|---|---|---|---|")
    if vivos:
        for rel in vivos:
            lineas.append("| {} | <completar> | <completar> | <completar> |".format(rel))
    else:
        lineas.append("| (revisado, sin cambios necesarios) | — | — | — |")
    return "\n".join(lineas)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Auditor de documentación del cambio en curso")
    ap.add_argument("--root", default=".")
    ap.add_argument("--base", default="HEAD", help="referencia git para comparar (por defecto HEAD)")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if not root.is_dir():
        print("No existe la carpeta: " + str(root))
        return 2
    try:  # consolas Windows cp1252: un árbol del README no debe abortar el aviso
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    print(render(root, a.base))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
