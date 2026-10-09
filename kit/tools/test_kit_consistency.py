#!/usr/bin/env python3
"""Pruebas de consistencia del repositorio del kit (no viajan en el zip).

1. Cada entrada de sgp-kit.manifest existe en kit/.
2. El zip versionado coincide con el manifiesto: mismos archivos y mismo contenido.

El contenido se compara con finales de línea normalizados (LF), para que la guarda no
dependa de `core.autocrlf` ni del sistema donde se generó el zip.

Es del repositorio del kit: por eso no está en sgp-kit.manifest.

    python -m unittest tools/test_kit_consistency.py -v
"""
import os
import sys
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sgp_kit  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
KIT = REPO / "kit"
EJEMPLO = REPO / "examples" / "descuento"
ZIP = REPO / "sgp-lite.zip"


def expandidos():
    """Rutas relativas de todos los archivos managed + seeded del manifiesto."""
    managed, seeded = sgp_kit.load_manifest(KIT)
    files = []
    for entry in managed + seeded:
        files += sgp_kit.expand(KIT, entry)
    return files


def normalizado(b):
    """Normaliza CRLF -> LF para comparar sin depender de autocrlf."""
    return b.replace(b"\r\n", b"\n")


class ManifiestoTests(unittest.TestCase):
    def test_entradas_del_manifiesto_existen(self):
        for rel in expandidos():
            self.assertTrue((KIT / rel).exists(), f"el manifiesto referencia {rel}, que no existe")


class ZipTests(unittest.TestCase):
    def test_zip_versionado_coincide_con_el_manifiesto(self):
        if not ZIP.exists():
            self.skipTest("sgp-lite.zip no está versionado")
        esperados = set(expandidos())
        with zipfile.ZipFile(ZIP) as z:
            self.assertEqual(esperados, set(z.namelist()),
                             "el zip no tiene exactamente los archivos del manifiesto")
            for rel in sorted(esperados):
                self.assertEqual(normalizado((KIT / rel).read_bytes()), normalizado(z.read(rel)),
                                 f"contenido desactualizado en el zip: {rel}")


class EjemploTests(unittest.TestCase):
    def test_skills_del_ejemplo_iguales_al_kit(self):
        kit_skills = sorted(p.name for p in (KIT / "skills").iterdir() if p.is_dir())
        ej_skills = sorted(p.name for p in (EJEMPLO / "skills").iterdir() if p.is_dir())
        self.assertEqual(kit_skills, ej_skills, "el ejemplo debe tener las mismas skills que el kit")
        for name in kit_skills:
            self.assertEqual(
                normalizado((KIT / "skills" / name / "SKILL.md").read_bytes()),
                normalizado((EJEMPLO / "skills" / name / "SKILL.md").read_bytes()),
                f"examples/descuento/skills/{name}/SKILL.md difiere del kit",
            )

    def test_tools_del_ejemplo_iguales_al_kit(self):
        for rel in ("sgp_check.py", "sync_skills.py"):
            self.assertEqual(
                normalizado((KIT / "tools" / rel).read_bytes()),
                normalizado((EJEMPLO / "tools" / rel).read_bytes()),
                f"examples/descuento/tools/{rel} difiere del kit",
            )

    def test_agents_del_ejemplo_lista_las_skills_del_kit(self):
        texto = (EJEMPLO / "AGENTS.md").read_text(encoding="utf-8")
        for name in sorted(p.name for p in (KIT / "skills").iterdir() if p.is_dir()):
            self.assertIn(name, texto, f"AGENTS.md del ejemplo no menciona {name}")


if __name__ == "__main__":
    unittest.main()
