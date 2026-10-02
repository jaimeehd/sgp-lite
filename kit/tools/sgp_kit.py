#!/usr/bin/env python3
"""sgp_kit.py — instala y ACTUALIZA el kit SGP Lite en un proyecto (solo stdlib, Python 3.8+).

Resuelve el problema de "copiar una vez y desactualizarse": guarda en el proyecto un
marcador (`.sgp-kit.json`) con la versión del kit y el hash de cada archivo gestionado.
En cada `update` sabe distinguir entre:
  - archivo gestionado intacto  -> se actualiza con la versión nueva del kit,
  - archivo gestionado editado  -> si el kit no cambió, se respeta; si el kit cambió,
                                   se respalda tu versión y se aplica la del kit (conflicto).

Uso:
    python tools/sgp_kit.py init   --source <ruta-al-kit> --dest <proyecto>
    python tools/sgp_kit.py update --source <ruta-al-kit> --dest <proyecto>
    python tools/sgp_kit.py status --source <ruta-al-kit> --dest <proyecto>

`managed` = se instalan y actualizan. `seeded` = se copian solo si faltan; nunca se pisan.
El manifiesto vive en el kit: `sgp-kit.manifest`.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
import sys
from pathlib import Path

MARKER = ".sgp-kit.json"
BACKUP = ".sgp-kit-backup"
MANIFEST = "sgp-kit.manifest"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_version(source: Path) -> str:
    v = source / "VERSION"
    return v.read_text(encoding="utf-8").strip() if v.exists() else "0.0.0"


def load_manifest(source: Path):
    managed, seeded = [], []
    path = source / MANIFEST
    if not path.exists():
        raise SystemExit(f"No existe {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        kind, _, entry = line.partition(" ")
        entry = entry.strip()
        if kind == "managed":
            managed.append(entry)
        elif kind == "seeded":
            seeded.append(entry)
    return managed, seeded


def expand(source: Path, entry: str):
    """Devuelve rutas relativas (posix) de ficheros para una entrada (archivo o carpeta)."""
    full = source / entry
    if full.is_dir():
        return [p.relative_to(source).as_posix()
                for p in sorted(full.rglob("*")) if p.is_file()]
    return [entry]


def read_marker(dest: Path) -> dict:
    path = dest / MARKER
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            return {}
    return {}


def write_marker(dest: Path, data: dict) -> None:
    (dest / MARKER).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def backup(dest: Path, rel: str, stamp: str) -> Path:
    src = dest / rel
    dst = dest / BACKUP / stamp / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst.relative_to(dest)


def apply(source: Path, dest: Path):
    """init/update: aplica managed (con protección por hash) y seeded (si faltan)."""
    managed, seeded = load_manifest(source)
    version = read_version(source)
    marker = read_marker(dest)
    recorded = dict(marker.get("managed", {}))
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    added = updated = kept = conflicted = 0
    notes = []

    for entry in managed:
        for rel in expand(source, entry):
            src = source / rel
            dst = dest / rel
            src_hash = sha256(src)
            cur_hash = sha256(dst) if dst.exists() else None
            old = recorded.get(rel)
            dst.parent.mkdir(parents=True, exist_ok=True)

            if cur_hash is None:
                shutil.copy2(src, dst)
                recorded[rel] = src_hash
                added += 1
            elif cur_hash == old:                 # intacto desde la última aplicación
                if cur_hash != src_hash:
                    shutil.copy2(src, dst)
                    recorded[rel] = src_hash
                    updated += 1
                else:
                    kept += 1
            elif src_hash == old:                 # el kit no cambió: manda tu edición
                notes.append(f"  [local]  {rel} (editado; el kit no cambió, se conserva)")
                kept += 1
            else:                                 # ambos cambiaron: conflicto
                rel_backup = backup(dest, rel, stamp)
                shutil.copy2(src, dst)
                recorded[rel] = src_hash
                conflicted += 1
                notes.append(f"  [conflicto] {rel}: tu versión guardada en {rel_backup}")

    seeded_added = []
    for rel in seeded:
        dst = dest / rel
        if not dst.exists():
            src = source / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            seeded_added.append(rel)

    write_marker(dest, {
        "source": str(source),
        "version": version,
        "applied": datetime.date.today().isoformat(),
        "managed": recorded,
    })

    for n in notes:
        print(n)
    for rel in seeded_added:
        print(f"  [sembrado] {rel} (plantilla inicial; edítalo para tu proyecto)")
    print(f"\nKit {version} -> {dest}")
    print(f"managed: {added} nuevos, {updated} actualizados, {kept} al día, {conflicted} con conflicto")
    return 0


def status(source: Path, dest: Path):
    managed, seeded = load_manifest(source)
    version = read_version(source)
    marker = read_marker(dest)
    recorded = marker.get("managed", {})
    print(f"Kit origen: {source} (versión {version})")
    print(f"Proyecto:   {dest}")
    print(f"Aplicado:   {marker.get('version', '(sin marcador: no inicializado)')}")
    pending = missing = modified = 0
    for entry in managed:
        for rel in expand(source, entry):
            src_hash = sha256(source / rel)
            dst = dest / rel
            if not dst.exists():
                print(f"  [falta]      {rel}")
                missing += 1
                continue
            cur = sha256(dst)
            old = recorded.get(rel)
            if cur == src_hash:
                state = "al día"
            elif old is None or cur == old:
                state = "actualización disponible"
                pending += 1
            else:
                state = "editado localmente (kit cambió)"
                modified += 1
            print(f"  [{state}] {rel}")
    print(f"\n{missing} faltan, {pending} con actualización, {modified} editados (conflicto potencial).")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="Instala/actualiza el kit SGP Lite en un proyecto.")
    ap.add_argument("accion", choices=["init", "update", "status"])
    ap.add_argument("--source", required=True, help="ruta de la carpeta del kit (con sgp-kit.manifest)")
    ap.add_argument("--dest", default=".", help="raíz del proyecto destino")
    ap.add_argument("--version", action="store_true", help="muestra la versión del kit y sale")
    a = ap.parse_args(argv)
    source = Path(a.source).resolve()
    dest = Path(a.dest).resolve()
    if a.version:
        print(read_version(source))
        return 0
    if not (source / MANIFEST).exists():
        print(f"'{source}' no parece el kit: falta {MANIFEST}")
        return 2
    dest.mkdir(parents=True, exist_ok=True)
    if a.accion == "status":
        return status(source, dest)
    return apply(source, dest)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
