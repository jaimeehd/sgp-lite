#!/usr/bin/env python3
"""Pruebas de la guarda de frescura (sgp_fresh.py).

Cubren: marcador vigente, envejecido, ausente (requerido y no requerido), mal
formado, fecha futura, marcador dentro de un bloque de código, --strict y errores
de carpeta. Se ejecutan como el resto del kit:

    python -m unittest discover -s tools -p "test_*.py" -v
"""
import tempfile
import unittest
from datetime import date
from pathlib import Path

import sgp_fresh

HOY = date(2026, 10, 18)


def escribir(base, rel, texto):
    p = Path(base) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto, encoding="utf-8")
    return p


class FrescuraTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def test_marcador_vigente(self):
        escribir(self.base, "README.md",
                 "# Doc\n\n<!-- freshness: owner=@equipo reviewed=2026-10-01 -->\n")
        self.assertEqual(sgp_fresh.revisar(self.base, hoy=HOY), [])

    def test_marcador_envejecido(self):
        escribir(self.base, "README.md",
                 "# Doc\n\n<!-- freshness: owner=@equipo reviewed=2025-01-01 -->\n")
        hallazgos = sgp_fresh.revisar(self.base, max_dias=180, hoy=HOY)
        self.assertEqual(len(hallazgos), 1)
        self.assertIn("revisado hace", hallazgos[0][1])

    def test_sin_marcador_no_requerido(self):
        escribir(self.base, "docs/notas.md", "# Notas\n")
        self.assertEqual(sgp_fresh.revisar(self.base, hoy=HOY), [])

    def test_sin_marcador_requerido(self):
        escribir(self.base, "README.md", "# Doc\n")
        hallazgos = sgp_fresh.revisar(self.base, requeridos=["README.md"], hoy=HOY)
        self.assertEqual(len(hallazgos), 1)
        self.assertIn("sin marcador", hallazgos[0][1])

    def test_marcador_mal_formado(self):
        escribir(self.base, "README.md", "# Doc\n\n<!-- freshness: reviewed=2026-10-01 -->\n")
        hallazgos = sgp_fresh.revisar(self.base, hoy=HOY)
        self.assertEqual(len(hallazgos), 1)
        self.assertIn("mal formado", hallazgos[0][1])

    def test_fecha_futura(self):
        escribir(self.base, "README.md",
                 "<!-- freshness: owner=@equipo reviewed=2027-01-01 -->\n")
        hallazgos = sgp_fresh.revisar(self.base, hoy=HOY)
        self.assertEqual(len(hallazgos), 1)
        self.assertIn("futura", hallazgos[0][1])

    def test_marcador_en_bloque_de_codigo_se_ignora(self):
        escribir(self.base, "README.md",
                 "# Doc\n\n```\n<!-- freshness: owner=@equipo reviewed=2020-01-01 -->\n```\n")
        self.assertEqual(sgp_fresh.revisar(self.base, hoy=HOY), [])

    def test_varios_archivos_solo_avisa_del_envejecido(self):
        escribir(self.base, "README.md",
                 "<!-- freshness: owner=@equipo reviewed=2026-10-01 -->\n")
        escribir(self.base, "docs/viejo.md",
                 "<!-- freshness: owner=@equipo reviewed=2024-01-01 -->\n")
        hallazgos = sgp_fresh.revisar(self.base, hoy=HOY)
        self.assertEqual(len(hallazgos), 1)
        self.assertEqual(hallazgos[0][0], "docs/viejo.md")

    def test_modo_strict(self):
        escribir(self.base, "README.md", "# Doc\n")
        self.assertEqual(sgp_fresh.main(["--root", str(self.base), "--require", "README.md",
                                         "--strict", "--today", "2026-10-18"]), 1)
        escribir(self.base, "README.md",
                 "<!-- freshness: owner=@equipo reviewed=2026-10-18 -->\n")
        self.assertEqual(sgp_fresh.main(["--root", str(self.base), "--require", "README.md",
                                         "--strict", "--today", "2026-10-18"]), 0)

    def test_root_inexistente(self):
        self.assertEqual(sgp_fresh.main(["--root", str(self.base / "no-existe")]), 2)


if __name__ == "__main__":
    unittest.main()
