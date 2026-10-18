#!/usr/bin/env python3
"""sgp_fresh.py — guarda de frescura de la documentación crítica (aviso).

Busca en los `*.md` del proyecto el marcador de frescura:

    <!-- freshness: owner=@usuario reviewed=2026-10-18 -->

y avisa cuando:
  - la revisión supera `--max-days` días (por defecto 180);
  - un documento de `--require` no tiene marcador;
  - el marcador está mal formado o la fecha es futura.

No edita nada. Aviso por defecto; `--strict` devuelve 1 si hay hallazgos (para CI).
Solo librería estándar (Python 3.8+). Inspirado en las «freshness dates» de Google
y en los gates de frescura de CI (dueño + última revisión).

    python tools/sgp_fresh.py
    python tools/sgp_fresh.py --max-days 180 --require README.md,docs/manual.md --strict
"""
import argparse
import re
from datetime import date
from pathlib import Path

DIRS_IGNORADOS = {".git", "node_modules", ".venv", "__pycache__", ".sgp-kit-backup"}
PATRON = re.compile(r"<!--\s*freshness:\s*owner=(\S+)\s+reviewed=(\d{4}-\d{2}-\d{2})\s*-->")
PATRON_PARCIAL = re.compile(r"<!--\s*freshness:")
EXT = ".md"


def _sin_cercas(lineas):
    """Rinde (n, texto) sin las líneas dentro de cercas ``` o ~~~."""
    dentro = False
    for n, linea in enumerate(lineas, 1):
        limpia = linea.strip()
        if limpia.startswith("```") or limpia.startswith("~~~"):
            dentro = not dentro
            continue
        if not dentro:
            yield n, linea


def revisar(root, max_dias=180, requeridos=(), hoy=None):
    """Devuelve [(archivo, mensaje)] con los problemas de frescura encontrados."""
    root = Path(root)
    hoy = hoy or date.today()
    hallazgos, marcados = [], set()
    for archivo in sorted(root.rglob("*" + EXT)):
        if any(parte in DIRS_IGNORADOS for parte in archivo.parts):
            continue
        rel = archivo.relative_to(root).as_posix()
        try:
            lineas = archivo.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        encontrado = None
        for _n, linea in _sin_cercas(lineas):
            m = PATRON.search(linea)
            if m:
                encontrado = m
                break
            if PATRON_PARCIAL.search(linea):
                hallazgos.append((rel, "marcador de frescura mal formado (falta owner o reviewed)"))
                encontrado = "malformado"
                break
        if not encontrado:
            continue
        marcados.add(rel)
        if encontrado == "malformado":
            continue
        revisado_txt = encontrado.group(2)
        try:
            revisado = date.fromisoformat(revisado_txt)
        except ValueError:
            hallazgos.append((rel, "fecha de revisión inválida: " + revisado_txt))
            continue
        dias = (hoy - revisado).days
        if dias < 0:
            hallazgos.append((rel, "fecha de revisión futura: " + revisado_txt))
        elif dias > max_dias:
            hallazgos.append((rel, "revisado hace {} días (máximo {})".format(dias, max_dias)))
    for rel in requeridos:
        if rel not in marcados:
            hallazgos.append((rel, "sin marcador de frescura (requerido con --require)"))
    return hallazgos


def main(argv=None):
    ap = argparse.ArgumentParser(description="Guarda de frescura de la documentación crítica")
    ap.add_argument("--root", default=".")
    ap.add_argument("--max-days", type=int, default=180, dest="max_dias")
    ap.add_argument("--require", default="", help="rutas separadas por coma que deben tener marcador")
    ap.add_argument("--today", help="AAAA-MM-DD (pruebas)")
    ap.add_argument("--strict", action="store_true", help="devuelve 1 si hay hallazgos (para CI)")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if not root.is_dir():
        print("No existe la carpeta: " + str(root))
        return 2
    hoy = date.fromisoformat(a.today) if a.today else None
    requeridos = [x.strip().replace("\\", "/") for x in a.require.split(",") if x.strip()]
    hallazgos = revisar(root, a.max_dias, requeridos, hoy)
    for rel, mensaje in hallazgos:
        print("[AVISO] {}: {}".format(rel, mensaje))
    print("\nResumen: {} hallazgo(s) de frescura.".format(len(hallazgos)))
    if a.strict and hallazgos:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
