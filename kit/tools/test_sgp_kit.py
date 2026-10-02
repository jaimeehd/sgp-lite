#!/usr/bin/env python3
"""Pruebas de tools/sgp_kit.py (init/update/status). Solo stdlib.

    python -m unittest tools/test_sgp_kit.py -v
"""
import os
import sys
import tempfile
import unittest
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

    def test_status_reports_version_and_pending(self):
        sgp_kit.apply(self.kit, self.dest)
        (self.kit / "tools" / "a.py").write_text("A2", encoding="utf-8")
        marker = sgp_kit.read_marker(self.dest)
        self.assertEqual("9.9.9", marker["version"])
        # status no debe fallar ni modificar el proyecto
        rc = sgp_kit.status(self.kit, self.dest)
        self.assertEqual(0, rc)
        self.assertEqual("A1", (self.dest / "tools" / "a.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
