#!/usr/bin/env python3
"""Pruebas de sincronía entre la presentación y la distribución de la política.

La política de ingeniería y su protocolo viven dos veces en este repositorio: en
`docs/` (lectura, Paso 0 del README) y en `kit/skills/` (lo que instala el kit con
`sgp_kit` y empaqueta `sgp_zip`). Este test falla si las copias divergen.

Es del repositorio del kit, no del kit instalado: por eso no está en `sgp-kit.manifest`.

    python -m unittest tools/test_policy_sync.py -v
"""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

PARES = [
    ("docs/system-engineering-policy.SKILL.md",
     "kit/skills/system-engineering-policy/SKILL.md"),
    ("docs/protocolo-ingenieria-senior.SKILL.md",
     "kit/skills/protocolo-ingenieria-senior/SKILL.md"),
]


class PolicySyncTests(unittest.TestCase):
    def test_copias_byte_a_byte(self):
        for presentacion, distribucion in PARES:
            a = REPO / presentacion
            b = REPO / distribucion
            self.assertTrue(a.exists(), f"falta {presentacion}")
            self.assertTrue(b.exists(), f"falta {distribucion}")
            self.assertEqual(a.read_bytes(), b.read_bytes(),
                             f"divergen {presentacion} y {distribucion}")


if __name__ == "__main__":
    unittest.main()
