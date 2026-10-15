#!/usr/bin/env python3
"""Pruebas de sincronía entre la presentación y la distribución de la política.

La política de ingeniería y su protocolo viven dos veces en este repositorio: en
`docs/` (lectura, Paso 0 del README) y en `kit/skills/` (lo que instala el kit con
`sgp_kit` y empaqueta `sgp_zip`). Este test falla si las copias divergen.

Es del repositorio del kit, no del kit instalado: por eso no está en `sgp-kit.manifest`.

    python -m unittest tools/test_policy_sync.py -v

Chequeo local opcional contra la canónica viva de esta máquina (no puede vivir en un test
del repo porque `~/.config` no está en git): define SGP_POLICY_CANONICAL con la ruta de la
política canónica y el test añade la comparación; sin la variable, ese caso se omite.

    SGP_POLICY_CANONICAL="~/.config/opencode/system_prompt.md" python tools/test_policy_sync.py
"""
import os
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

PARES = [
    ("docs/system-engineering-policy.SKILL.md",
     "kit/skills/system-engineering-policy/SKILL.md"),
    ("docs/protocolo-ingenieria-senior.SKILL.md",
     "kit/skills/protocolo-ingenieria-senior/SKILL.md"),
]


def cuerpo_sin_frontmatter(texto: str) -> list:
    """Líneas del SKILL.md sin el bloque de frontmatter (la canónica no lo lleva).

    Ignora las líneas en blanco sobrantes al inicio y al fin: no son divergencia real.
    """
    lineas = texto.splitlines()
    if lineas and lineas[0].strip() == "---":
        for i, linea in enumerate(lineas[1:], start=1):
            if linea.strip() == "---":
                lineas = lineas[i + 1:]
                break
    while lineas and not lineas[0].strip():
        lineas.pop(0)
    while lineas and not lineas[-1].strip():
        lineas.pop()
    return lineas


class PolicySyncTests(unittest.TestCase):
    def test_copias_byte_a_byte(self):
        for presentacion, distribucion in PARES:
            a = REPO / presentacion
            b = REPO / distribucion
            self.assertTrue(a.exists(), f"falta {presentacion}")
            self.assertTrue(b.exists(), f"falta {distribucion}")
            self.assertEqual(a.read_bytes(), b.read_bytes(),
                             f"divergen {presentacion} y {distribucion}")

    def test_canonica_externa_opcional(self):
        ruta = os.environ.get("SGP_POLICY_CANONICAL")
        if not ruta:
            self.skipTest("SGP_POLICY_CANONICAL sin definir: chequeo local opcional de la canónica")
        canon = Path(ruta).expanduser()
        self.assertTrue(canon.exists(), f"no existe la canónica {canon}")
        kit = REPO / "kit" / "skills" / "system-engineering-policy" / "SKILL.md"
        self.assertEqual(canon.read_text(encoding="utf-8").splitlines(),
                         cuerpo_sin_frontmatter(kit.read_text(encoding="utf-8")),
                         f"{kit} diverge de la canónica {canon}")


if __name__ == "__main__":
    unittest.main()
