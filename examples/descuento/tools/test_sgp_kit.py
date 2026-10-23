#!/usr/bin/env python3
"""Pruebas de tools/sgp_kit.py (init/update/status). Solo stdlib.

    python -m unittest tools/test_sgp_kit.py -v
"""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sgp_kit  # noqa: E402


def make_kit(root: Path) -> None:
    (root / "VERSION").write_text("9.9.9\n", encoding="utf-8")
    (root / "tools").mkdir(parents=True, exist_ok=True)
    (root / "tools" / "a.py").write_text("A1", encoding="utf-8")
    (root / "skills" / "s1").mkdir(parents=True, exist_ok=True)
    (root / "skills" / "s1" / "SKILL.md").write_text("S1", encoding="utf-8")
    (root / "changes").mkdir(parents=True, exist_ok=True)
    (root / "changes" / "_plantilla.md").write_text("T1", encoding="utf-8")
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "constitution.md").write_text("C-kit", encoding="utf-8")
    (root / "AGENTS.md").write_text("AG-kit", encoding="utf-8")
    (root / "sgp-kit.manifest").write_text(
        "managed tools/a.py\n"
        "managed skills\n"
        "managed changes/_plantilla.md\n"
        "seeded docs/constitution.md\n"
        "seeded AGENTS.md\n",
        encoding="utf-8")


class SgpKitTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.kit = self.base / "kit"
        self.dest = self.base / "proj"
        self.kit.mkdir()
        self.dest.mkdir()
        make_kit(self.kit)

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_copies_managed_and_seeded_and_writes_marker(self):
        sgp_kit.apply(self.kit, self.dest)
        self.assertTrue((self.dest / "tools" / "a.py").exists())
        self.assertTrue((self.dest / "skills" / "s1" / "SKILL.md").exists())
        self.assertTrue((self.dest / "changes" / "_plantilla.md").exists())
        self.assertTrue((self.dest / "docs" / "constitution.md").exists())
        self.assertTrue((self.dest / ".sgp-kit.json").exists())
        marker = sgp_kit.read_marker(self.dest)
        self.assertEqual("9.9.9", marker["version"])
        self.assertIn("tools/a.py", marker["managed"])
        self.assertIn("skills/s1/SKILL.md", marker["managed"])

    def test_seeded_not_overwritten(self):
        (self.dest / "docs").mkdir()
        (self.dest / "docs" / "constitution.md").write_text("MIA", encoding="utf-8")
        sgp_kit.apply(self.kit, self.dest)
        self.assertEqual("MIA", (self.dest / "docs" / "constitution.md").read_text(encoding="utf-8"))

    def test_update_applies_kit_change_when_untouched(self):
        sgp_kit.apply(self.kit, self.dest)
        (self.kit / "tools" / "a.py").write_text("A2", encoding="utf-8")
        sgp_kit.apply(self.kit, self.dest)
        self.assertEqual("A2", (self.dest / "tools" / "a.py").read_text(encoding="utf-8"))

    def test_update_preserves_local_edit_when_kit_unchanged(self):
        sgp_kit.apply(self.kit, self.dest)
        (self.dest / "tools" / "a.py").write_text("MIA", encoding="utf-8")
        sgp_kit.apply(self.kit, self.dest)
        self.assertEqual("MIA", (self.dest / "tools" / "a.py").read_text(encoding="utf-8"))

    def test_update_conflict_backs_up_and_takes_kit(self):
        sgp_kit.apply(self.kit, self.dest)
        (self.dest / "tools" / "a.py").write_text("MIA", encoding="utf-8")
        (self.kit / "tools" / "a.py").write_text("A2", encoding="utf-8")
        sgp_kit.apply(self.kit, self.dest)
        self.assertEqual("A2", (self.dest / "tools" / "a.py").read_text(encoding="utf-8"))
        backups = list((self.dest / sgp_kit.BACKUP).rglob("a.py"))
        self.assertEqual(1, len(backups))
        self.assertEqual("MIA", backups[0].read_text(encoding="utf-8"))

    def test_hash_normaliza_finales_de_linea(self):
        # Windows + core.autocrlf: CRLF en el árbol no debe parecer una edición
        a = self.base / "lf.txt"
        b = self.base / "crlf.txt"
        a.write_bytes(b"uno\ndos\n")
        b.write_bytes(b"uno\r\ndos\r\n")
        self.assertEqual(sgp_kit.sha256(a), sgp_kit.sha256(b))

    def test_update_no_conflicta_si_ya_coincide_con_el_kit(self):
        # Registro obsoleto pero el archivo ya tiene el contenido del kit: al día, sin
        # respaldo ni conflicto (antes se respaldaba y copiaba lo mismo: ruido).
        sgp_kit.apply(self.kit, self.dest)
        marker = sgp_kit.read_marker(self.dest)
        marker["managed"]["tools/a.py"] = "hash-viejo"
        sgp_kit.write_marker(self.dest, marker)
        with redirect_stdout(io.StringIO()):
            sgp_kit.apply(self.kit, self.dest)
        self.assertFalse((self.dest / sgp_kit.BACKUP).exists())

    def test_cli_version_sin_accion_ni_source(self):
        # --version funciona solo: informa la versión del kit sin exigir acción ni --source
        rc = sgp_kit.main(["--version"])
        self.assertEqual(0, rc)

    def test_cli_sin_accion_falla_ruidoso(self):
        # --source sin verbo no ejecuta nada en silencio: usage + exit 2
        with self.assertRaises(SystemExit) as cm:
            sgp_kit.main(["--source", str(self.kit)])
        self.assertEqual(2, cm.exception.code)

    def test_status_reports_version_and_pending(self):
        sgp_kit.apply(self.kit, self.dest)
        (self.kit / "tools" / "a.py").write_text("A2", encoding="utf-8")
        marker = sgp_kit.read_marker(self.dest)
        self.assertEqual("9.9.9", marker["version"])
        # status no debe fallar ni modificar el proyecto
        rc = sgp_kit.status(self.kit, self.dest)
        self.assertEqual(0, rc)
        self.assertEqual("A1", (self.dest / "tools" / "a.py").read_text(encoding="utf-8"))

    def test_status_reporta_conflicto_si_el_archivo_no_esta_registrado(self):
        # Fichero gestionado que existe pero no consta en el marcador (un hook propio del
        # proyecto): `apply` lo respalda y lo sustituye, y `status` debe anunciarlo así.
        (self.dest / "tools").mkdir()
        (self.dest / "tools" / "a.py").write_text("MIO", encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            rc = sgp_kit.status(self.kit, self.dest)
        self.assertEqual(0, rc)
        self.assertIn("conflicto", out.getvalue())
        self.assertIn("sin registrar", out.getvalue())
        self.assertNotIn("actualización disponible", out.getvalue())

    def test_status_y_update_coinciden_para_archivo_no_registrado(self):
        (self.dest / "tools").mkdir()
        (self.dest / "tools" / "a.py").write_text("MIO", encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out):
            sgp_kit.status(self.kit, self.dest)
        self.assertIn("conflicto", out.getvalue())
        with redirect_stdout(io.StringIO()):
            sgp_kit.apply(self.kit, self.dest)
        self.assertEqual("A1", (self.dest / "tools" / "a.py").read_text(encoding="utf-8"))
        backups = list((self.dest / sgp_kit.BACKUP).rglob("a.py"))
        self.assertEqual(1, len(backups))
        self.assertEqual("MIO", backups[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
