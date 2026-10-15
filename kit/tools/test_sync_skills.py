#!/usr/bin/env python3
"""Pruebas de sync_skills.py: protección por hash de las skills instaladas.

Es del repositorio del kit, no del kit instalado: por eso no está en sgp-kit.manifest.

    python tools/test_sync_skills.py -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_skills  # noqa: E402


def escribir_skill(root: Path, contenido: str) -> None:
    skill = root / "skills" / "demo"
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(contenido, encoding="utf-8")


def destino(root: Path) -> Path:
    return root / ".agents" / "skills" / "demo"


def estado(root: Path) -> dict:
    p = root / ".agents" / "skills" / sync_skills.STATE
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def correr(root: Path, *extra: str) -> None:
    argv = ["sync_skills.py", "--agent", "generico", "--root", str(root), *extra]
    old = sys.argv
    try:
        sys.argv = argv
        sync_skills.main()
    finally:
        sys.argv = old


class SyncSkillsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        escribir_skill(self.root, "v1")

    def tearDown(self):
        self._tmp.cleanup()

    def test_instala_la_que_falta(self):
        correr(self.root)
        self.assertEqual(destino(self.root).joinpath("SKILL.md").read_text(encoding="utf-8"), "v1")
        self.assertIn("demo", estado(self.root))

    def test_actualiza_sola_la_intacta_sin_force(self):
        correr(self.root)
        escribir_skill(self.root, "v2")
        correr(self.root)
        self.assertEqual(destino(self.root).joinpath("SKILL.md").read_text(encoding="utf-8"), "v2")

    def test_protege_la_editada_a_mano(self):
        correr(self.root)
        (destino(self.root) / "SKILL.md").write_text("edicion local", encoding="utf-8")
        escribir_skill(self.root, "v2")
        correr(self.root)
        self.assertEqual(destino(self.root).joinpath("SKILL.md").read_text(encoding="utf-8"), "edicion local")
        correr(self.root, "--force")
        self.assertEqual(destino(self.root).joinpath("SKILL.md").read_text(encoding="utf-8"), "v2")

    def test_sin_registro_se_protege(self):
        correr(self.root)
        (root_state := self.root / ".agents" / "skills" / sync_skills.STATE).write_text("{}", encoding="utf-8")
        escribir_skill(self.root, "v2")
        correr(self.root)
        self.assertEqual(destino(self.root).joinpath("SKILL.md").read_text(encoding="utf-8"), "v1")
        self.assertTrue(root_state.exists())

    def test_re_ejecucion_sin_cambios_no_toca_nada(self):
        correr(self.root)
        antes = destino(self.root).joinpath("SKILL.md").read_bytes()
        correr(self.root)
        self.assertEqual(destino(self.root).joinpath("SKILL.md").read_bytes(), antes)


if __name__ == "__main__":
    unittest.main()
