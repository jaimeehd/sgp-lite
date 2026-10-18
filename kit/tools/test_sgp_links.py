#!/usr/bin/env python3
"""Pruebas de la guarda de enlaces (sgp_links.py).

Cubren: enlace relativo válido/roto, anclas, imágenes, enlaces externos ignorados,
bloques y comillas de código ignorados, plantillas y modo --strict.
Se ejecutan como el resto del kit:

    python -m unittest discover -s tools -p "test_*.py" -v
"""
import tempfile
import unittest
from pathlib import Path

import sgp_links


def escribir(base, rel, texto):
    p = Path(base) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto, encoding="utf-8")
    return p


class EnlacesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def test_enlace_relativo_valido(self):
        escribir(self.base, "docs/uso.md", "# Uso\n")
        escribir(self.base, "README.md", "Ver [uso](docs/uso.md).\n")
        self.assertEqual(sgp_links.revisar(self.base), [])

    def test_enlace_relativo_roto(self):
        escribir(self.base, "README.md", "Ver [uso](docs/no-existe.md).\n")
        hallazgos = sgp_links.revisar(self.base)
        self.assertEqual(len(hallazgos), 1)
        self.assertEqual(hallazgos[0][0], "README.md")
        self.assertEqual(hallazgos[0][1], 1)
        self.assertIn("enlace roto", hallazgos[0][2])

    def test_ancla_valida(self):
        escribir(self.base, "docs/uso.md", "# Guía de uso\n")
        escribir(self.base, "README.md", "Ver [la guía](docs/uso.md#guía-de-uso).\n")
        self.assertEqual(sgp_links.revisar(self.base), [])

    def test_ancla_rota(self):
        escribir(self.base, "docs/uso.md", "# Guía de uso\n")
        escribir(self.base, "README.md", "Ver [otra](docs/uso.md#no-existe).\n")
        hallazgos = sgp_links.revisar(self.base)
        self.assertEqual(len(hallazgos), 1)
        self.assertIn("ancla no encontrada", hallazgos[0][2])

    def test_ancla_en_el_mismo_archivo(self):
        escribir(self.base, "README.md", "# Inicio\n\nIr a [abajo](#detalle).\n\n## Detalle\n")
        self.assertEqual(sgp_links.revisar(self.base), [])

    def test_ignora_externos_y_plantillas(self):
        escribir(self.base, "README.md",
                 "[web](https://example.com) [correo](mailto:x@example.com) [t](tel:123) [p]({{var}})\n")
        self.assertEqual(sgp_links.revisar(self.base), [])

    def test_ignora_bloques_de_codigo(self):
        escribir(self.base, "README.md", "```\n[x](no-existe.md)\n```\n")
        self.assertEqual(sgp_links.revisar(self.base), [])

    def test_ignora_codigo_inline(self):
        escribir(self.base, "README.md", "Así: `[x](no-existe.md)`\n")
        self.assertEqual(sgp_links.revisar(self.base), [])

    def test_imagen_relativa_rota(self):
        escribir(self.base, "README.md", "![logo](assets/logo.png)\n")
        hallazgos = sgp_links.revisar(self.base)
        self.assertEqual(len(hallazgos), 1)
        self.assertIn("enlace roto", hallazgos[0][2])

    def test_modo_strict(self):
        escribir(self.base, "README.md", "[x](no-existe.md)\n")
        self.assertEqual(sgp_links.main(["--root", str(self.base), "--strict"]), 1)
        escribir(self.base, "no-existe.md", "ok\n")
        self.assertEqual(sgp_links.main(["--root", str(self.base), "--strict"]), 0)

    def test_root_inexistente(self):
        self.assertEqual(sgp_links.main(["--root", str(self.base / "no-existe")]), 2)

    def test_no_edita_archivos(self):
        escribir(self.base, "README.md", "[x](no-existe.md)\n")
        escribir(self.base, "docs/uso.md", "# Uso\n")

        def foto():
            return {p.relative_to(self.base).as_posix(): p.read_bytes()
                    for p in sorted(self.base.rglob("*")) if p.is_file()}

        antes = foto()
        sgp_links.revisar(self.base)
        self.assertEqual(antes, foto())
