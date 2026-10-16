#!/usr/bin/env python3
"""Pruebas de las citas del runbook: cada § que cita debe existir en la política.

El protocolo (`protocolo-ingenieria-senior`) es un runbook que NO define reglas: cita
secciones de la política. Este test falla si una cita apunta a una sección que no existe
(por ejemplo, tras renumerar la política) o si el runbook deja de citar.

Es del repositorio del kit, no del kit instalado: por eso no está en `sgp-kit.manifest`.

    python tools/test_protocolo_citas.py -v
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
POLITICA = REPO / "kit/skills/system-engineering-policy/SKILL.md"
RUNBOOK = REPO / "kit/skills/protocolo-ingenieria-senior/SKILL.md"

CITA = re.compile(r"§(\d+(?:\.\d+)?)")


def secciones_de_la_politica(texto: str) -> set:
    """Identificadores §N y §N.M declarados como encabezado en la política."""
    return {m.group(1) for l in texto.splitlines() if l.startswith("#")
            for m in [CITA.search(l)] if m}


class CitasDelRunbookTests(unittest.TestCase):
    def test_toda_cita_apunta_a_una_seccion_existente(self):
        politica = secciones_de_la_politica(POLITICA.read_text(encoding="utf-8"))
        self.assertTrue(politica, "no se detectó ninguna sección en la política")
        citas = set(CITA.findall(RUNBOOK.read_text(encoding="utf-8")))
        huerfanas = sorted(c for c in citas if c not in politica)
        self.assertEqual([], huerfanas,
                         f"el runbook cita secciones que no existen en la política: {huerfanas}")

    def test_el_runbook_cita_y_no_redefine(self):
        texto = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn("no define reglas", texto.lower(),
                      "el runbook debe declarar que no define reglas")
        self.assertGreaterEqual(len(CITA.findall(texto)), 15,
                                "el runbook debe citar las secciones que aplica")


if __name__ == "__main__":
    unittest.main()
