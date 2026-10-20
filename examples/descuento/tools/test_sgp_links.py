#!/usr/bin/env python3
"""Pruebas de la guarda de enlaces (sgp_links.py).

Cubren: enlace relativo válido/roto, anclas, imágenes, enlaces externos ignorados,
bloques y comillas de código ignorados, plantillas y modo --strict.
Se ejecutan como el resto del kit:

    python -m unittest discover -s tools -p "test_*.py" -v
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sgp_links  # noqa: E402


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


class GitignoreTests(unittest.TestCase):
    """Con repositorio git, la guarda revisa lo que git considera del proyecto."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.git("init")

    def git(self, *args):
        r = subprocess.run(["git", "-C", str(self.base)] + list(args),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_ignora_lo_que_esta_en_el_gitignore(self):
        escribir(self.base, ".gitignore", "ignorado.md\n")
        escribir(self.base, "ignorado.md", "[x](no-existe.md)\n")
        escribir(self.base, "README.md", "sin enlaces\n")
        self.git("add", ".gitignore", "README.md")
        self.assertEqual(sgp_links.revisar(self.base), [])

    def test_revisa_lo_no_ignorado_todavia_no_seguido(self):
        escribir(self.base, ".gitignore", "ignorado.md\n")
        escribir(self.base, "ignorado.md", "[x](no-existe.md)\n")
        escribir(self.base, "nuevo.md", "[x](no-existe.md)\n")
        self.git("add", ".gitignore")
        hallazgos = sgp_links.revisar(self.base)
        self.assertEqual(len(hallazgos), 1)
        self.assertEqual(hallazgos[0][0], "nuevo.md")

    def test_ignora_venv_aunque_no_este_ignorado(self):
        escribir(self.base, "venv/Lib/site-packages/x/Privacy.md", "[x](no-existe.md)\n")
        escribir(self.base, "README.md", "sin enlaces\n")
        self.git("add", "README.md")
        self.assertEqual(sgp_links.revisar(self.base), [])

    def test_sin_git_recorre_el_arbol(self):
        """Sin repositorio, la guarda sigue funcionando sobre el árbol."""
        escribir(self.base, "README.md", "[x](no-existe.md)\n")
        self.assertEqual(len(sgp_links.revisar(self.base)), 1)

    def test_revisa_rutas_con_caracteres_no_ascii(self):
        """Un .md versionado con acento o ñ se revisa igual.

        `git ls-files` entrecomilla en octal las rutas no ASCII si no se pide
        la salida con `-z`; con ese entrecomillado el fichero se salía del
        universo en silencio y sus enlaces rotos no se detectaban.
        """
        escribir(self.base, "Índice.md", "[x](no-existe.md)\n")
        escribir(self.base, "carpeta ñ/guía.md", "[x](tampoco-existe.md)\n")
        self.git("add", "Índice.md", "carpeta ñ/guía.md")
        hallazgos = sgp_links.revisar(self.base)
        self.assertEqual(len(hallazgos), 2)
        self.assertEqual(sorted(h[0] for h in hallazgos),
                         ["carpeta ñ/guía.md", "Índice.md"])


if __name__ == "__main__":
    unittest.main()

