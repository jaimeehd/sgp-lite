#!/usr/bin/env python3
"""sgp_links.py — guarda de enlaces relativos y anclas de la documentación (aviso).

Recorre los `*.md` del proyecto y comprueba los enlaces inline `[texto](destino)` y
las imágenes `![alt](destino)`:
  - enlaces relativos: que el archivo destino exista;
  - anclas `#...`: que exista un encabezado con ese slug en el destino (o en el
    propio archivo si el enlace es solo `#ancla`);
  - se ignoran `http(s)://`, `mailto:`, `tel:`, plantillas `{{...}}` y el contenido
    dentro de bloques de código o de comillas invertidas.

No edita nada. Aviso por defecto; `--strict` devuelve 1 si hay hallazgos (para CI).
Solo librería estándar (Python 3.8+). Los enlaces externos no se comprueban: para
eso usa una herramienta de CI (p. ej. lychee).

El universo de ficheros es el que git considera del proyecto: `git ls-files`
(seguidos y no seguidos) respeta el `.gitignore`, así que `venv/`, `dist/` o un
fichero local de pruebas no generan avisos. Sin git, se recorre el árbol como
antes, menos los directorios de `DIRS_IGNORADOS`.

    python tools/sgp_links.py
    python tools/sgp_links.py --root . --strict
"""
import argparse
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

DIRS_IGNORADOS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".sgp-kit-backup"}
EXT = ".md"
PATRON_ENLACE = re.compile(r"!?\[[^\]]*\]\(\s*([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\s*\)")
PATRON_CODIGO = re.compile(r"`[^`]*`")
PATRON_ENCABEZADO = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def _ejecutar_git(root, *args):
    """Ejecuta git de solo lectura; devuelve stdout o None si git falla."""
    try:
        r = subprocess.run(["git", "-C", str(root)] + list(args),
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def _archivos_md(root):
    """Ficheros .md del proyecto.

    Con git: los que git conoce (seguidos y no seguidos, excluyendo lo que el
    `.gitignore` marca), de modo que lo ignorado no se revisa. Sin git: el
    árbol entero. En ambos casos se descartan los directorios de
    `DIRS_IGNORADOS` (por ejemplo un `venv/` que git no llega a ignorar).

    `ls-files` se invoca con `-z` porque, sin él, git entrecomilla las rutas
    con caracteres no ASCII (en octal) y esos ficheros se quedarían fuera del
    universo sin avisar.
    """
    if _ejecutar_git(root, "rev-parse", "--is-inside-work-tree") is not None:
        salida = _ejecutar_git(root, "ls-files", "-z", "--cached", "--others",
                               "--exclude-standard", "--", "*" + EXT) or ""
        rutas = [r for r in salida.split("\0") if r]
        candidatos = [root / r for r in rutas if (root / r).is_file()]
    else:
        candidatos = sorted(root.rglob("*" + EXT))
    # La exclusión se evalúa sobre la ruta RELATIVA al root: así se descarta
    # un `venv/` dentro del proyecto sin descartar el proyecto entero cuando
    # vive bajo un directorio padre que se llama `venv`.
    return [p for p in candidatos
            if not any(parte in DIRS_IGNORADOS
                       for parte in p.relative_to(root).parts)]


def _slug(texto):
    """Slug estilo GitHub: minúsculas, sin puntuación salvo guiones y guion bajo."""
    texto = texto.strip().lower()
    texto = re.sub(r"[^\w\- ]", "", texto, flags=re.UNICODE)
    return texto.replace(" ", "-")


def _texto_sin_bloques(lineas):
    """Devuelve [(n, texto)] sin líneas dentro de cercas ``` o ~~~ ni código inline."""
    dentro, salida = False, []
    for n, linea in enumerate(lineas, 1):
        limpia = linea.strip()
        if limpia.startswith("```") or limpia.startswith("~~~"):
            dentro = not dentro
            continue
        if dentro:
            continue
        salida.append((n, PATRON_CODIGO.sub("", linea)))
    return salida


def _anclas(ruta):
    try:
        lineas = ruta.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return set()
    anclas = set()
    for n, texto in _texto_sin_bloques(lineas):
        m = PATRON_ENCABEZADO.match(texto)
        if m:
            anclas.add(_slug(m.group(2)))
    return anclas


def revisar(root):
    """Devuelve [(archivo, linea, mensaje)] con los enlaces rotos encontrados."""
    root = Path(root)
    hallazgos = []
    for archivo in _archivos_md(root):
        rel = archivo.relative_to(root).as_posix()
        try:
            lineas = archivo.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for n, texto in _texto_sin_bloques(lineas):
            for destino in PATRON_ENLACE.findall(texto):
                if destino.startswith(("http://", "https://", "mailto:", "tel:")):
                    continue
                if "{{" in destino:
                    continue
                ruta_parte, _, ancla = destino.partition("#")
                ruta_parte = unquote(ruta_parte)
                if not ruta_parte:
                    objetivo = archivo
                else:
                    objetivo = (archivo.parent / ruta_parte).resolve()
                if not objetivo.exists():
                    hallazgos.append((rel, n, "enlace roto: " + destino))
                    continue
                if ancla and objetivo.is_file() and objetivo.suffix.lower() == EXT:
                    if ancla not in _anclas(objetivo):
                        hallazgos.append((rel, n, "ancla no encontrada: " + destino))
    return hallazgos


def main(argv=None):
    ap = argparse.ArgumentParser(description="Guarda de enlaces relativos y anclas de la documentación")
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true", help="devuelve 1 si hay hallazgos (para CI)")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if not root.is_dir():
        print("No existe la carpeta: " + str(root))
        return 2
    hallazgos = revisar(root)
    for rel, n, mensaje in hallazgos:
        print("[AVISO] {}:{} {}".format(rel, n, mensaje))
    print("\nResumen: {} hallazgo(s) de enlaces.".format(len(hallazgos)))
    if a.strict and hallazgos:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
