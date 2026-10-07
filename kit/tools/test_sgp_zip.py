#!/usr/bin/env python3
"""Pruebas de tools/sgp_zip.py (zip de instalación manual). Solo stdlib.

    python -m unittest tools/test_sgp_zip.py -v
"""
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sgp_zip  # noqa: E402
from test_sgp_kit import make_kit  # noqa: E402


class SgpZipTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.kit = self.base / "kit"
        self.kit.mkdir()
        make_kit(self.kit)

    def tearDown(self):
        self._tmp.cleanup()

    def test_zip_incluye_managed_y_seeded_con_su_contenido(self):
        dest = self.base / "sgp-lite.zip"
        self.assertEqual(0, sgp_zip.make_zip(self.kit, dest))
        with zipfile.ZipFile(dest) as z:
            self.assertEqual(
                {"tools/a.py", "skills/s1/SKILL.md", "changes/_plantilla.md",
                 "docs/constitution.md", "AGENTS.md"},
                set(z.namelist()))
            self.assertEqual(b"A1", z.read("tools/a.py"))
            self.assertEqual(b"C-kit", z.read("docs/constitution.md"))

    def test_falla_sin_manifest(self):
        self.assertEqual(2, sgp_zip.make_zip(self.base, self.base / "x.zip"))


if __name__ == "__main__":
    unittest.main()
