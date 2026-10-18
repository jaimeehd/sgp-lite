"""Pruebas del verificador. Ejecutar:  python -m unittest tools/test_sgp_check.py -v"""
import os, subprocess, sys, tempfile, textwrap, unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sgp_check  # noqa: E402

CHECK = str(Path(__file__).with_name("sgp_check.py"))
PY = sys.executable

CONSTITUCION = "# Constitución\n1. **La spec manda**. Verificado por: humano.\n2. **Tests**. Verificado por: tests.\n"
SPEC = textwrap.dedent("""\
    # Spec
    ## Requisitos
    - **EXP-001** CUANDO el usuario exporta, EL SISTEMA generará un JSON (salida 0).
    - **EXP-002** SI falta el título, ENTONCES EL SISTEMA mostrará un error (salida 1).
""")


def change(estado="aplicando", ids="[EXP-001, EXP-002]", tasks=None, extra="", inicio="2026-09-22", apetito=3, carril="normal", diseno=""):
    tasks = tasks if tasks is not None else (
        "- [x] T001 [EXP-001] uno\n  Hecho cuando: pasa\n- [x] T002 [EXP-002] dos\n  Hecho cuando: pasa\n")
    return (f"---\nid: CHG-001\ncarril: {carril}\nestado: {estado}\napetito_dias: {apetito}\ninicio: {inicio}\nrequisitos: {ids}\n---\n"
            f"## Criterios de finalización\n- [ ] x\n\n{diseno}\n## Tareas\n{tasks}\n{extra}")


def sgp_yaml(**cmd):
    lines = ["rutas:", "  tests: tests", "comandos:"]
    for k in ("build", "tests", "lint", "test_por_requisito"):
        lines.append(f'  {k}: "{cmd.get(k, "")}"')
    return "\n".join(lines) + "\n"


class Base(unittest.TestCase):
    def repo(self, files):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        base = {"AGENTS.md": "# a\n", "docs/constitution.md": CONSTITUCION, "specs/catalogo/spec.md": SPEC,
                "sgp.yaml": sgp_yaml(), "changes/CHG-001-x.md": change()}
        base.update(files)
        for rel, text in base.items():
            if text is None:
                continue
            p = Path(d.name) / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        return d.name

    def run_check(self, root, *args, env=None):
        e = dict(os.environ, **(env or {}))
        p = subprocess.run([PY, CHECK, "--root", root, "--today", "2026-09-24", *args], capture_output=True, text=True, env=e)
        return p.returncode, p.stdout + p.stderr


class Estructura(Base):
    def test_repo_valido_pasa(self):
        rc, out = self.run_check(self.repo({}))
        self.assertEqual(rc, 0, out)

    def test_cli_version(self):
        p = subprocess.run([PY, CHECK, "--version"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertTrue(p.stdout.strip())

    def test_run_en_consola_cp1252_no_crashea(self):
        # En Windows la consola puede ser cp1252: un carácter no codificable (p. ej. →) en un
        # print lanza UnicodeEncodeError y aborta con traceback en vez de informar el resultado.
        y = sgp_yaml(build=f"{PY} -c pass", tests=f"{PY} -c pass", lint=f"{PY} -c pass")
        r = self.repo({"sgp.yaml": y})
        rc, out = self.run_check(r, "--run", env={"PYTHONIOENCODING": "cp1252"})
        self.assertEqual(rc, 0, out)
        self.assertNotIn("UnicodeEncodeError", out)

    def test_yaml_con_estructura_no_soportada_no_crashea(self):
        # listas y anidamiento se ignoran; un valor entre comillas se acepta
        y = ("rutas:\n  tests: tests\nlistas:\n  - uno\n  - dos\n"
             "comandos:\n"
             f"  build: \"{PY} -c pass\"\n"
             "  tests: \"\"\n"
             "  lint: \"\"\n"
             "  test_por_requisito: \"\"\n")
        rc, out = self.run_check(self.repo({"sgp.yaml": y}), "--run")
        self.assertEqual(rc, 0, out)

    def test_tarea_sin_hecho_cuando(self):
        r = self.repo({"changes/CHG-001-x.md": change(tasks="- [x] T001 [EXP-001] uno\n- [x] T002 [EXP-002] dos\n  Hecho cuando: ok\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("T001 no tiene «Hecho cuando:»", out)

    def test_tarea_sin_requisito(self):
        r = self.repo({"changes/CHG-001-x.md": change(tasks="- [x] T001 uno\n  Hecho cuando: ok\n- [x] T002 [EXP-002] d\n  Hecho cuando: ok\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("no enlaza a ningún requisito", out)

    def test_requisito_inexistente_en_spec(self):
        r = self.repo({"changes/CHG-001-x.md": change(ids="[EXP-001, EXP-009]")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("EXP-009 no existe en specs/", out)

    def test_requisito_sin_tarea(self):
        r = self.repo({"changes/CHG-001-x.md": change(tasks="- [x] T001 [EXP-001] uno\n  Hecho cuando: ok\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("EXP-002 no está cubierto por ninguna tarea", out)

    def test_presupuesto_agotado(self):
        r = self.repo({"changes/CHG-001-x.md": change(inicio="2026-09-10")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("presupuesto agotado", out); self.assertIn("NO extender", out)

    def test_revision_con_tareas_pendientes(self):
        r = self.repo({"changes/CHG-001-x.md": change(estado="revision", tasks="- [ ] T001 [EXP-001] uno\n  Hecho cuando: ok\n- [x] T002 [EXP-002] d\n  Hecho cuando: ok\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("tareas pendientes (T001)", out)

    def test_marca_por_aclarar_con_cambio_aplicando(self):
        r = self.repo({"specs/catalogo/spec.md": SPEC + "\n- [POR-ACLARAR] duda\n"})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("[POR-ACLARAR]", out)

    def test_id_duplicado_en_specs(self):
        r = self.repo({"specs/otro/spec.md": "- **EXP-001** EL SISTEMA hace algo.\n"})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("ID de requisito duplicado EXP-001", out)

    def test_requisito_vago_avisa(self):
        r = self.repo({"specs/catalogo/spec.md": SPEC + "- **EXP-003** EL SISTEMA responderá de forma rápida.\n"})
        rc, out = self.run_check(r)
        self.assertIn("no verificables", out)

    def test_carril_rapido_no_exige_requisitos(self):
        r = self.repo({"changes/CHG-001-x.md": change(carril="rapido", ids="[]", tasks="- [x] T001 arreglo\n  Hecho cuando: test de regresión pasa\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 0, out)

    def test_constitucion_sin_verificado_por(self):
        r = self.repo({"docs/constitution.md": "# C\n1. **Spec manda**: sin verificación declarada.\n"})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 0); self.assertIn("no declara «Verificado por:»", out)
        rc, out = self.run_check(r, "--stage", "pre-merge")
        self.assertEqual(rc, 1)


class PreMerge(Base):
    TESTS_OK = textwrap.dedent("""\
        import unittest
        class T(unittest.TestCase):
            def test_EXP_001_exporta(self): self.assertTrue(True)
            def test_EXP_002_error(self): self.assertTrue(True)
    """)
    TPL = f"{PY} -m unittest discover -s tests -t . -k {{id_py}}"

    def pm(self, tests=None, cmds=None, ch=None):
        yaml = sgp_yaml(build=f"{PY} -c pass", tests=f"{PY} -m unittest discover -s tests -t .", lint=f"{PY} -c pass",
                        test_por_requisito=self.TPL)
        files = {"sgp.yaml": cmds or yaml, "changes/CHG-001-x.md": ch or change(estado="revision"),
                 "tests/__init__.py": "", "tests/test_x.py": tests if tests is not None else self.TESTS_OK}
        return self.repo(files)

    def test_pasa_con_pruebas_reales(self):
        rc, out = self.run_check(self.pm(), "--stage", "pre-merge")
        self.assertEqual(rc, 0, out); self.assertIn("EXP-001", out)

    def test_filtro_dotnet_sin_coincidencias_no_es_ok(self):
        # dotnet test con un filtro sin coincidencias termina con código 0 y solo escribe un mensaje
        # (visto en la práctica en español; el inglés es el texto documentado del mismo mensaje).
        mensajes = ["Ninguna prueba coincide con el filtro de casos de prueba proporcionado",
                    "No test matches the given testcase filter"]
        for msg in mensajes:
            with self.subTest(msg=msg):
                tpl = f"{PY} -c \\\"print('{msg}')\\\""
                y = sgp_yaml(build=f"{PY} -c pass", tests=f"{PY} -c pass", lint=f"{PY} -c pass", test_por_requisito=tpl)
                rc, out = self.run_check(self.pm(cmds=y), "--stage", "pre-merge")
                self.assertEqual(rc, 1, out)
                self.assertIn("sin pruebas", out)

    def test_falso_verde_por_comentario(self):
        rc, out = self.run_check(self.pm(tests="# EXP-001 EXP-002\nimport unittest\nclass T(unittest.TestCase):\n    def test_algo(self): pass\n"),
                                 "--stage", "pre-merge")
        self.assertEqual(rc, 1); self.assertIn("sin pruebas", out)

    def test_prueba_que_falla(self):
        bad = self.TESTS_OK.replace("test_EXP_002_error(self): self.assertTrue(True)", "test_EXP_002_error(self): self.fail('x')")
        rc, out = self.run_check(self.pm(tests=bad), "--stage", "pre-merge")
        self.assertEqual(rc, 1); self.assertIn("EXP-002", out); self.assertIn("falla", out)

    def test_verificacion_manual_ok_cubre(self):
        ch = change(estado="revision", extra="## Verificación manual\n| Requisito | Pasos | Esperado | Resultado |\n|---|---|---|---|\n| EXP-002 | abrir | error | OK |\n")
        t = self.TESTS_OK.replace("    def test_EXP_002_error(self): self.assertTrue(True)\n", "")
        rc, out = self.run_check(self.pm(tests=t, ch=ch), "--stage", "pre-merge")
        self.assertEqual(rc, 0, out); self.assertIn("manual OK", out)

    def test_sensor_sin_configurar_es_error(self):
        rc, out = self.run_check(self.pm(cmds=sgp_yaml()), "--stage", "pre-merge")
        self.assertEqual(rc, 1); self.assertIn("sensor 'build' sin configurar", out)

    def test_comando_que_falla(self):
        y = sgp_yaml(build=f"{PY} -c \\\"import sys; sys.exit(3)\\\"", tests=f"{PY} -c pass", lint=f"{PY} -c pass", test_por_requisito=self.TPL)
        rc, out = self.run_check(self.pm(cmds=y), "--stage", "pre-merge")
        self.assertEqual(rc, 1); self.assertIn("comando:build", out)


class Git(Base):
    def git(self, root, *a):
        return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True)

    def setup_repo(self):
        r = self.repo({"tests/test_core.py": "def test_a():\n    assert 1 == 1\n"})
        self.git(r, "init", "-q"); self.git(r, "config", "user.email", "a@b.c"); self.git(r, "config", "user.name", "t")
        self.git(r, "add", "-A"); self.git(r, "commit", "-qm", "base")
        return r

    def test_ratchet_bloquea_debilitar(self):
        r = self.setup_repo()
        (Path(r) / "tests/test_core.py").write_text("def test_a():\n    pass\n")
        self.git(r, "add", "-A")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 1); self.assertIn("SGP_TESTS_APPROVED=1", out)

    def test_ratchet_permite_añadir(self):
        r = self.setup_repo()
        with open(Path(r) / "tests/test_core.py", "a") as f:
            f.write("def test_b():\n    assert True\n")
        self.git(r, "add", "-A")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 0, out)

    def test_ratchet_con_aprobacion(self):
        r = self.setup_repo()
        (Path(r) / "tests/test_core.py").write_text("def test_a():\n    pass\n")
        self.git(r, "add", "-A")
        rc, out = self.run_check(r, "--ratchet", env={"SGP_TESTS_APPROVED": "1"})
        self.assertEqual(rc, 0, out)


class Borrador(Base):
    def test_cambio_recien_creado_no_bloquea(self):
        tpl = (Path(__file__).parent.parent / "changes" / "_plantilla.md").read_text(encoding="utf-8")
        r = self.repo({"changes/_plantilla.md": tpl, "changes/CHG-001-x.md": None})
        self.assertEqual(self.run_check(r, "--nuevo", "algo")[0], 0)
        rc, out = self.run_check(r)
        self.assertEqual(rc, 0, out); self.assertIn("(borrador)", out)


class Mayor(Base):
    DISENO_OK = "## Diseño\n**Enfoque:** x\n**Alternativa considerada:** y, descartada por z\n"

    def test_mayor_sin_diseno_falla(self):
        r = self.repo({"changes/CHG-001-x.md": change(carril="mayor")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("sin sección «## Diseño» con una alternativa descartada", out)

    def test_mayor_con_diseno_pasa(self):
        r = self.repo({"changes/CHG-001-x.md": change(carril="mayor", diseno=self.DISENO_OK)})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 0, out)

    def test_mayor_sin_adr_solo_avisa(self):
        r = self.repo({"changes/CHG-001-x.md": change(carril="mayor", diseno=self.DISENO_OK)})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 0); self.assertIn("sin referencia a un ADR", out)

    def test_normal_multidominio_avisa_no_bloquea(self):
        r = self.repo({"specs/otro/spec.md": "- **OTR-001** EL SISTEMA hace otra cosa.\n",
                        "changes/CHG-001-x.md": change(ids="[EXP-001, OTR-001]",
                            tasks="- [x] T001 [EXP-001] uno\n  Hecho cuando: ok\n- [x] T002 [OTR-001] dos\n  Hecho cuando: ok\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 0); self.assertIn("toca 2 dominios", out); self.assertIn("sube a carril 'mayor'", out)


class Nuevo(Base):
    def test_nuevo_numera_correlativamente(self):
        tpl = "---\nid: CHG-000\nestado: propuesta\n---\n"
        r = self.repo({"changes/_plantilla.md": tpl, "changes/CHG-001-x.md": None})
        self.assertEqual(self.run_check(r, "--nuevo", "Mi Cambio")[0], 0)
        self.assertEqual(self.run_check(r, "--nuevo", "otro")[0], 0)
        names = sorted(p.name for p in (Path(r) / "changes").glob("CHG-*.md"))
        self.assertEqual(names, ["CHG-001-mi-cambio.md", "CHG-002-otro.md"])
        self.assertIn("id: CHG-002", (Path(r) / "changes" / names[1]).read_text())


class StripComment(unittest.TestCase):
    def test_comentario_y_comillas(self):
        self.assertEqual(sgp_check.strip_comment('a # b'), 'a')
        self.assertEqual(sgp_check.strip_comment('# inicio'), '')
        self.assertEqual(sgp_check.strip_comment('a#b'), 'a#b')
        self.assertEqual(sgp_check.strip_comment('"a # b"'), 'a # b')
        self.assertEqual(sgp_check.strip_comment("'a # b'"), 'a # b')
        self.assertEqual(sgp_check.strip_comment('"echo #x"  # fuera'), 'echo #x')


if __name__ == "__main__":
    unittest.main()
