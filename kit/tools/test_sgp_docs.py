#!/usr/bin/env python3
"""Pruebas del auditor de documentación (sgp_docs.py).

Cubren: clasificación de documentos, extracción de términos, búsqueda con
archivo:línea, fallback sin git, detección de cambios y que el auditor NO edita.
Se ejecutan como el resto del kit:

    python -m unittest discover -s tools -p "test_*.py" -v
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import sgp_docs


def git(base, *args):
    return subprocess.run(["git", "-C", str(base)] + list(args), check=True,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def crear_repo(base):
    git(base, "init", "-q")
    git(base, "config", "user.email", "pruebas@example.invalid")
    git(base, "config", "user.name", "Pruebas")


def escribir(base, rel, texto):
    p = Path(base) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto, encoding="utf-8")
    return p


def commit(base, mensaje="inicial"):
    git(base, "add", "-A")
    git(base, "commit", "-q", "-m", mensaje)


class EtiquetaTests(unittest.TestCase):
    def test_vigente_historia_y_guia(self):
        self.assertEqual(sgp_docs.etiqueta("README.md"), "VIGENTE")
        self.assertEqual(sgp_docs.etiqueta("docs/uso.md"), "VIGENTE")
        self.assertEqual(sgp_docs.etiqueta("CHANGELOG.md"), "HISTORIA")
        self.assertEqual(sgp_docs.etiqueta(".clean/decisions.md"), "HISTORIA")
        self.assertEqual(sgp_docs.etiqueta("changes/CHG-001-x.md"), "HISTORIA")
        self.assertEqual(sgp_docs.etiqueta("docs/adr/ADR-001.md"), "HISTORIA")
        self.assertEqual(sgp_docs.etiqueta("docs/plan-produccion.md"), "HISTORIA")
        self.assertEqual(sgp_docs.etiqueta("skills/x/SKILL.md"), "GUIA")
        self.assertEqual(sgp_docs.etiqueta("kit/AGENTS.md"), "GUIA")


class TerminosTests(unittest.TestCase):
    def test_nombres_y_simbolos(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir(tmp, "saludo.py", "def calcular_total(x):\n    return x\n")
            terms = sgp_docs.terminos(Path(tmp), ["saludo.py"])
            self.assertIn("saludo", terms)
            self.assertIn("calcular_total", terms)

    def test_ignora_cadenas_cortas(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir(tmp, "ab.py", "x = 1\n")
            terms = sgp_docs.terminos(Path(tmp), ["ab.py"])
            self.assertNotIn("ab", terms)

    def test_ignora_genericos(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir(tmp, "util.py", "def main():\n    pass\n")
            terms = sgp_docs.terminos(Path(tmp), ["util.py"])
            self.assertNotIn("main", terms)
            self.assertIn("util", terms)


class MencionesTests(unittest.TestCase):
    def test_archivo_y_linea(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir(tmp, "README.md", "linea uno\nusa calcular_total aqui\n")
            mapa = sgp_docs.menciones(Path(tmp), ["calcular_total"], ["README.md"])
            self.assertIn("calcular_total", mapa)
            rel, linea, tipo, _ = mapa["calcular_total"][0]
            self.assertEqual(rel, "README.md")
            self.assertEqual(linea, 2)
            self.assertEqual(tipo, "VIGENTE")


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def test_sin_git(self):
        out = sgp_docs.render(self.base)
        self.assertIn("SIN GIT", out)

    def test_sin_cambios(self):
        crear_repo(self.base)
        escribir(self.base, "README.md", "hola\n")
        commit(self.base)
        out = sgp_docs.render(self.base)
        self.assertIn("Sin cambios pendientes", out)

    def test_cambio_con_mencion_y_plantilla(self):
        crear_repo(self.base)
        escribir(self.base, "code.py", "def calcular_total(x):\n    return x\n")
        escribir(self.base, "README.md", "uno\nusa calcular_total aqui\n")
        commit(self.base)
        escribir(self.base, "code.py", "def calcular_total(x):\n    return x + 1\n")
        out = sgp_docs.render(self.base)
        self.assertIn("- code.py", out)
        self.assertIn("README.md:2 [VIGENTE]", out)
        self.assertIn("| Archivo | Sección | Qué cambió | Cómo lo verificaste |", out)
        self.assertIn("| README.md |", out)

    def test_historia_no_entra_en_la_plantilla(self):
        crear_repo(self.base)
        escribir(self.base, "code.py", "def calcular_total(x):\n    return x\n")
        escribir(self.base, "CHANGELOG.md", "uno\ndos\nmenciona calcular_total\n")
        commit(self.base)
        escribir(self.base, "code.py", "def calcular_total(x):\n    return x + 1\n")
        out = sgp_docs.render(self.base)
        self.assertIn("[HISTORIA]", out)
        self.assertIn("| (revisado, sin cambios necesarios) |", out)
        self.assertNotIn("| CHANGELOG.md |", out)

    def test_nuevos_sin_seguimiento(self):
        crear_repo(self.base)
        escribir(self.base, "README.md", "hola\n")
        commit(self.base)
        escribir(self.base, "nuevo.py", "def funcion_nueva(x):\n    return x\n")
        out = sgp_docs.render(self.base)
        self.assertIn("- nuevo.py", out)
        self.assertIn("(sin apariciones: ningún documento menciona lo cambiado)", out)

    def test_no_edita_archivos(self):
        crear_repo(self.base)
        escribir(self.base, "code.py", "def calcular_total(x):\n    return x\n")
        escribir(self.base, "README.md", "usa calcular_total\n")
        commit(self.base)
        escribir(self.base, "code.py", "def calcular_total(x):\n    return x + 1\n")

        def foto():
            return {p.relative_to(self.base).as_posix(): p.read_bytes()
                    for p in sorted(self.base.rglob("*")) if p.is_file()
                    and ".git" not in p.parts}

        antes = foto()
        sgp_docs.render(self.base)
        self.assertEqual(antes, foto())

    def test_root_inexistente(self):
        self.assertEqual(sgp_docs.main(["--root", str(self.base / "no-existe")]), 2)

    def test_consola_cp1252_no_crashea(self):
        # En Windows la consola puede ser cp1252 y el árbol de un README contiene «│»:
        # el auditor debe avisar igual, sin UnicodeEncodeError.
        crear_repo(self.base)
        escribir(self.base, "code.py", "def calcular_total(x):\n    return x\n")
        escribir(self.base, "README.md", "| arbol |\n│ usa calcular_total\n")
        commit(self.base)
        escribir(self.base, "code.py", "def calcular_total(x):\n    return x + 1\n")
        entorno = dict(os.environ, PYTHONIOENCODING="cp1252")
        r = subprocess.run([sys.executable, str(Path(sgp_docs.__file__)), "--root", str(self.base)],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=entorno)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("UnicodeEncodeError", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
