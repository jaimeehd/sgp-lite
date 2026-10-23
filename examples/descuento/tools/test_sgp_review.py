#!/usr/bin/env python3
"""Pruebas de `tools/sgp_review.py`: la puerta que impide cerrar una tarea sin su
ronda de revisión (LEC-006: un gate que ninguna puerta ejecuta es una declaración).

Se prueban sobre repositorios temporales con git, para no tocar el del proyecto.
Incluyen los casos negativos que destaparon los falsos verdes del piloto:
  * una fila `pendiente` no cuenta como revisión;
  * una fila con pipes en el texto se lee (no se descarta en silencio);
  * una fila malformada falla, no se ignora;
  * desde `revision.corte_fuente`, una fila sin `subagente <id>` no cuenta.
Y los propios del port al kit:
  * sin log la puerta se declara INACTIVA con aviso (no finge verde);
  * un log sin versionar no vale: la confirmación debe viajar con el commit.
Se ejecutan como el resto del kit:

    python -m unittest discover -s tools -p "test_*.py" -v
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sgp_review  # noqa: E402

SCRIPT = HERE / "sgp_review.py"
LOG = "docs/LOG-PROCESO.md"
CABECERA = ("| Fecha | # | Tipo | Qué | Estado | Referencia |\n"
            "|---|---|---|---|---|---|\n")


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=str(repo), check=True, capture_output=True,
                   text=True, encoding="utf-8", errors="replace")


class PuertaRevisionTests(unittest.TestCase):
    """Casos de extremo a extremo: staged en un repo temporal -> código de salida."""

    def _repo(self):
        """Repo temporal con el cambio CHG-999 y su tarea T001 sin marcar."""
        tmp = tempfile.TemporaryDirectory(prefix="sgp-review-")
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name)
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "pruebas@example.invalid")
        _git(repo, "config", "user.name", "Pruebas")
        (repo / "changes").mkdir()
        (repo / "changes" / "CHG-999-prueba.md").write_text(
            "---\nid: CHG-999\nestado: aplicando\n---\n\n"
            "## Criterios de finalización\n- [ ] Aprobado por el humano\n\n"
            "## Tareas\n- [ ] T001 Primera parte\n",
            encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-qm", "inicial")
        (repo / LOG).parent.mkdir(parents=True, exist_ok=True)
        (repo / LOG).write_text(CABECERA, encoding="utf-8")
        _git(repo, "add", LOG)
        return repo

    def _fila_log(self, repo, que, referencia="CHG-999 T001", estado="cerrada",
                  fecha="2026-10-21", rel=LOG):
        archivo = repo / rel
        if not archivo.exists():
            archivo.parent.mkdir(parents=True, exist_ok=True)
            archivo.write_text(CABECERA, encoding="utf-8")
        with archivo.open("a", encoding="utf-8") as fh:
            fh.write(f"| {fecha} | R01 | revisión | {que} | {estado} | {referencia} |\n")
        _git(repo, "add", rel)

    def _marcar(self, repo, marcada="- [x]"):
        archivo = repo / "changes" / "CHG-999-prueba.md"
        texto = archivo.read_text(encoding="utf-8").replace("- [ ] T001", marcada + " T001")
        archivo.write_text(texto, encoding="utf-8")
        _git(repo, "add", "changes/CHG-999-prueba.md")

    def _validar(self, repo):
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        res = subprocess.run([sys.executable, str(SCRIPT), "--root", str(repo)],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", env=env)
        return res.returncode, res.stdout + res.stderr

    # -- Los falsos verdes del piloto, convertidos en casos negativos --

    def test_sin_fila_de_revision_falla(self):
        repo = self._repo()
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(1, codigo, salida)
        self.assertIn("sin fila", salida)

    def test_con_fila_de_revision_pasa(self):
        repo = self._repo()
        self._fila_log(repo, "revisión de T001 con senior-reviewer, "
                             "independent-verifier y docs-syncer")
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(0, codigo, salida)

    def test_fila_sin_subagente_falla(self):
        repo = self._repo()
        self._fila_log(repo, "revisión hecha a mano, sin subagente")
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(1, codigo, salida)
        self.assertIn("ningún subagente", salida)

    def test_fila_de_otra_tarea_no_sirve(self):
        repo = self._repo()
        self._fila_log(repo, "revisión de T002 con senior-reviewer, "
                             "independent-verifier y docs-syncer",
                       referencia="CHG-999 T002")
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(1, codigo, salida)
        self.assertIn("sin fila", salida)

    def test_fila_pendiente_falla(self):
        repo = self._repo()
        self._fila_log(repo, "revisión de T001 con senior-reviewer, "
                             "independent-verifier y docs-syncer",
                       estado="pendiente")
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(1, codigo, salida)
        self.assertIn("pendiente", salida)

    def test_fila_con_pipes_escapados_se_lee(self):
        repo = self._repo()
        self._fila_log(repo, "revisión de T001 con Gate: ratchet 1/1 \\| tamano 1/500 "
                             "y senior-reviewer, independent-verifier y docs-syncer")
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(0, codigo, salida)

    def test_fila_con_pipes_sin_escapar_falla(self):
        repo = self._repo()
        self._fila_log(repo, "revisión de T001 con Gate: ratchet 1/1 | tamano 1/500 "
                             "y senior-reviewer")
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(1, codigo, salida)
        self.assertIn("FALLA", salida)

    def test_fila_malformada_falla(self):
        repo = self._repo()
        archivo = repo / LOG
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_text(CABECERA + "| 2026-10-21 | R01 | revisión | incompleta |\n",
                           encoding="utf-8")
        _git(repo, "add", LOG)
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(1, codigo, salida)
        self.assertIn("FALLA", salida)
        self.assertIn("línea", salida)  # el fallo señala qué fila está rota

    def test_fecha_invalida_falla(self):
        repo = self._repo()
        self._fila_log(repo, "revisión de T001 con senior-reviewer", fecha="21/10/2026")
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(1, codigo, salida)
        self.assertIn("FALLA", salida)

    def test_fila_nueva_sin_fuente_falla(self):
        repo = self._repo()
        self._fila_log(repo, "revisión de T001 con senior-reviewer, "
                             "independent-verifier y docs-syncer",
                       fecha="2026-10-23")
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(1, codigo, salida)
        self.assertIn("subagente", salida)

    def test_fila_nueva_con_fuente_pasa(self):
        repo = self._repo()
        self._fila_log(repo, "revisión de T001 con senior-reviewer (subagente ses_123), "
                             "independent-verifier y docs-syncer",
                       fecha="2026-10-23")
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(0, codigo, salida)

    def test_tarea_ya_cerrada_no_se_vuelve_a_pedir(self):
        repo = self._repo()
        self._fila_log(repo, "revisión de T001 con senior-reviewer, "
                             "independent-verifier y docs-syncer")
        self._marcar(repo)
        _git(repo, "commit", "-qm", "cierra T001")
        archivo = repo / "changes" / "CHG-999-prueba.md"
        archivo.write_text(archivo.read_text(encoding="utf-8") + "\nNota: detalle.\n",
                           encoding="utf-8")
        _git(repo, "add", "changes/CHG-999-prueba.md")
        codigo, salida = self._validar(repo)
        self.assertEqual(0, codigo, salida)

    # -- Modos propios del port al kit --

    def test_log_ausente_esta_inactiva_con_aviso(self):
        repo = self._repo()
        _git(repo, "rm", "-q", "-f", LOG)  # el proyecto todavía no usa la puerta
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(0, codigo, salida)
        self.assertIn("INACTIVA", salida)

    def test_log_no_indexado_falla(self):
        repo = self._repo()
        self._fila_log(repo, "revisión de T001 con senior-reviewer, "
                             "independent-verifier y docs-syncer")
        _git(repo, "rm", "-q", "--cached", LOG)  # en el árbol, fuera del índice
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(1, codigo, salida)
        self.assertIn("git add", salida)

    def test_config_del_proyecto(self):
        repo = self._repo()
        (repo / "sgp.yaml").write_text(
            "rutas:\n  log_proceso: docs/OTRO-LOG.md\n"
            "revision:\n  subagentes: revisor-a\n", encoding="utf-8")
        self._fila_log(repo, "revisión de T001 con revisor-a", rel="docs/OTRO-LOG.md")
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(0, codigo, salida)

    def test_baseline_exime(self):
        repo = self._repo()
        (repo / LOG).parent.mkdir(parents=True, exist_ok=True)
        (repo / LOG).write_text(CABECERA, encoding="utf-8")
        _git(repo, "add", LOG)
        self._marcar(repo)
        codigo, salida = self._validar(repo)
        self.assertEqual(1, codigo, salida)  # sin la exención, falla
        (repo / "tools").mkdir(exist_ok=True)
        (repo / "tools" / "revisiones-baseline.txt").write_text(
            "# Tareas cerradas antes de la puerta\nCHG-999 T001\n", encoding="utf-8")
        codigo, salida = self._validar(repo)
        self.assertEqual(0, codigo, salida)

    def test_commit_sin_changes_ok(self):
        repo = self._repo()
        codigo, salida = self._validar(repo)
        self.assertEqual(0, codigo, salida)
        self.assertIn("no toca changes", salida)


class ParserFilaLogTests(unittest.TestCase):
    """Unidad del parser estricto de filas (las columnas y los pipes escapados)."""

    def test_fila_valida_y_pipes_escapados(self):
        fila = sgp_review.parse_fila_log(
            "| 2026-10-21 | R01 | revisión | Gate \\| ratchet | cerrada | CHG-001 T001 |")
        self.assertEqual("cerrada", fila["estado"])
        self.assertIn("|", fila["que"])  # el pipe escapado vuelve a ser pipe
        self.assertIsNone(sgp_review.parse_fila_log("texto sin tabla"))

    def test_columnas_de_mas_falla(self):
        for linea in ("| 2026-10-21 | R01 | revisión | a | b | cerrada | CHG-001 T001 |",
                      "| 2026-10-21 | R01 | revisión | incompleta |"):
            with self.subTest(linea=linea):
                with self.assertRaises(sgp_review.FilaMalformada):
                    sgp_review.parse_fila_log(linea)

    def test_fecha_invalida_falla(self):
        with self.assertRaises(sgp_review.FilaMalformada):
            sgp_review.parse_fila_log("| 21/10/2026 | R01 | revisión | a | cerrada | r |")

    def test_cierre_y_fuente(self):
        self.assertTrue(sgp_review.es_cierre("Cerrada"))
        self.assertFalse(sgp_review.es_cierre("pendiente"))
        corte = "2026-10-23"
        vieja = {"fecha": "2026-10-21", "que": "x", "ref": "y"}
        nueva_sin = {"fecha": "2026-10-23", "que": "x", "ref": "y"}
        nueva_con = {"fecha": "2026-10-23", "que": "subagente ses_1", "ref": "y"}
        self.assertTrue(sgp_review.fuente_ok(vieja, corte))
        self.assertFalse(sgp_review.fuente_ok(nueva_sin, corte))
        self.assertTrue(sgp_review.fuente_ok(nueva_con, corte))


if __name__ == "__main__":
    unittest.main()
