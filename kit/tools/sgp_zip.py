#!/usr/bin/env python3
"""sgp_zip.py — genera el zip de instalación manual del kit (misma lista de archivos que
instala tools/sgp_kit.py: managed + seeded). Sin marcador: se descomprime en la raíz del
proyecto y no se actualiza solo.

Uso (desde la raíz del repositorio del kit):
    python kit/tools/sgp_zip.py --source kit --dest sgp-lite.zip
"""
import argparse
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sgp_kit  # noqa: E402


def make_zip(source: Path, dest: Path) -> int:
    if not (source / sgp_kit.MANIFEST).exists():
        print(f"'{source}' no parece el kit: falta {sgp_kit.MANIFEST}")
        return 2
    managed, seeded = sgp_kit.load_manifest(source)
    files = []
    for entry in managed + seeded:
        files += sgp_kit.expand(source, entry)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            z.write(source / rel, rel)
    print(f"Creado {dest} ({len(files)} archivos, kit {sgp_kit.read_version(source)})")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="Genera el zip de instalación manual del kit SGP Lite")
    ap.add_argument("--source", default=".", help="carpeta del kit (con sgp-kit.manifest)")
    ap.add_argument("--dest", default="sgp-lite.zip", help="ruta del zip a generar")
    a = ap.parse_args(argv)
    return make_zip(Path(a.source).resolve(), Path(a.dest))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
