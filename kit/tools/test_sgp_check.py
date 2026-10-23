"""Pruebas del verificador. Ejecutar:  python -m unittest tools/test_sgp_check.py -v"""
import datetime, os, shutil, subprocess, sys, tempfile, textwrap, unittest
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


def change(estado="aplicando", ids="[EXP-001, EXP-002]", tasks=None, extra="", inicio="2026-09-22", apetito=3, carril="normal", diseno="", criterios="- [ ] x"):
    tasks = tasks if tasks is not None else (
        "- [x] T001 [EXP-001] uno\n  Hecho cuando: pasa\n- [x] T002 [EXP-002] dos\n  Hecho cuando: pasa\n")
    return (f"---\nid: CHG-001\ncarril: {carril}\nestado: {estado}\napetito_dias: {apetito}\ninicio: {inicio}\nrequisitos: {ids}\n---\n"
            f"## Criterios de finalización\n{criterios}\n\n{diseno}\n## Tareas\n{tasks}\n{extra}")


def sgp_yaml(ratchet=None, **cmd):
    lines = ["rutas:", "  tests: tests"]
    if ratchet:
        lines.append(f"  ratchet: {ratchet}")
    lines.append("comandos:")
    for k in ("build", "tests", "lint", "test_por_requisito"):
        lines.append(f'  {k}: "{cmd.get(k, "")}"')
    return "\n".join(lines) + "\n"


def _env(extra=None):
    """Entorno de las pruebas: hermético frente a SGP_TESTS_APPROVED del shell (el escape del
    ratchet se pasa explícito en cada prueba) y con salida UTF-8 fija (el padre decodifica
    UTF-8; si el shell exporta PYTHONIOENCODING=cp1252, el hijo escribe en UTF-8 igualmente)."""
    e = {k: v for k, v in os.environ.items() if k != "SGP_TESTS_APPROVED"}
    e["PYTHONIOENCODING"] = "utf-8"
    e.update(extra or {})
    return e


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
        p = subprocess.run([PY, CHECK, "--root", root, "--today", "2026-09-24", *args],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=_env(env))
        return p.returncode, p.stdout + p.stderr

    def git(self, root, *a):
        return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True)


class Estructura(Base):
    def test_repo_valido_pasa(self):
        rc, out = self.run_check(self.repo({}))
        self.assertEqual(rc, 0, out)

    def test_cli_version(self):
        p = subprocess.run([PY, CHECK, "--version"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=_env())
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
    def setup_repo(self):
        r = self.repo({"tests/test_core.py": "def test_a():\n    assert 1 == 1\n"})
        self.git(r, "init", "-q"); self.git(r, "config", "user.email", "a@b.c"); self.git(r, "config", "user.name", "t")
        self.git(r, "add", "-A")
        p = self.git(r, "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        self.assertEqual(p.returncode, 0, p.stderr)
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

    def repo_git(self, files):
        r = self.repo(files)
        self.git(r, "init", "-q"); self.git(r, "config", "user.email", "a@b.c"); self.git(r, "config", "user.name", "t")
        self.git(r, "add", "-A")
        p = self.git(r, "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        self.assertEqual(p.returncode, 0, p.stderr)
        return r

    def test_ratchet_sin_git_falla_cerrado(self):
        # Guarda que no pudo verificar ≠ verde: sin git no hay forma de saber qué se borra.
        r = self.repo({})
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 1); self.assertIn("falla cerrado", out)

    def test_ratchet_nada_que_vigilar_avisa_en_voz_alta(self):
        # Sin pruebas vigiladas el ratchet NO se calla: avisa y explica cómo configurarlo.
        r = self.repo_git({})
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 0); self.assertIn("nada que vigilar", out); self.assertIn("ratchet:", out)

    def test_ratchet_glob_configurada_detecta_modificacion(self):
        r = self.repo_git({"sgp.yaml": sgp_yaml(ratchet="tools/test_*.py"),
                           "tools/test_kit.py": "def test_a():\n    assert 1 == 1\n"})
        (Path(r) / "tools/test_kit.py").write_text("def test_a():\n    pass\n")
        self.git(r, "add", "-A")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 1); self.assertIn("tools/test_kit.py", out)

    def test_ratchet_bloquea_borrar_la_ultima_prueba(self):
        # Borrar TODO el conjunto vigilado (git rm del único fichero): el índice queda sin
        # pruebas y antes se respondía «nada que vigilar» (verde). El universo suma HEAD.
        r = self.repo_git({"tests/test_unica.py": "def test_a():\n    assert 1 == 1\n"})
        self.git(r, "rm", "-q", "tests/test_unica.py")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 1); self.assertIn("tests/test_unica.py", out)

    def test_ratchet_glob_bloquea_borrado(self):
        r = self.repo_git({"sgp.yaml": sgp_yaml(ratchet="tools/test_*.py"),
                           "tools/test_kit.py": "def test_a():\n    assert 1 == 1\n",
                           "tools/test_otra.py": "def test_b():\n    assert 1 == 1\n"})
        self.git(r, "rm", "-q", "tools/test_kit.py")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 1); self.assertIn("tools/test_kit.py", out)

    def test_ratchet_bloquea_renombrar_fuera_de_la_ruta(self):
        # `git mv` fuera de la ruta vigilada retira cobertura: no puede pasar en verde.
        r = self.repo_git({"tests/test_a.py": "def test_a():\n    assert 1 == 1\n"})
        self.git(r, "mv", "tests/test_a.py", "notas.txt")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 1); self.assertIn("notas.txt", out)

    def test_ratchet_permite_renombrar_dentro(self):
        r = self.repo_git({"tests/test_a.py": "def test_a():\n    assert 1 == 1\n"})
        self.git(r, "mv", "tests/test_a.py", "tests/test_b.py")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 0, out)

    def test_ratchet_bloquea_renombrar_y_debilitar(self):
        original = "".join(f"def test_{i}():\n    assert {i} == {i}\n\n" for i in range(5))
        r = self.repo_git({"tests/test_a.py": original})
        (Path(r) / "tests/test_a.py").write_text(original.replace("assert 0 == 0", "pass", 1))
        self.git(r, "add", "-A")
        self.git(r, "mv", "tests/test_a.py", "tests/test_b.py")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 1); self.assertIn("renombrada y modificada", out)

    def test_ratchet_bloquea_binario_modificado(self):
        # Binario vigilado: `--numstat` da `-\t-` (sin líneas que contar). Si ya existía en
        # HEAD, modificarlo o borrarlo es retirar cobertura y no puede pasar en verde.
        r = self.repo({"tests/test_core.py": "def test_a():\n    assert 1 == 1\n"})
        (Path(r) / "tests/fixture.bin").write_bytes(b"\x00\x01\x02")
        self.git(r, "init", "-q"); self.git(r, "config", "user.email", "a@b.c"); self.git(r, "config", "user.name", "t")
        self.git(r, "add", "-A")
        p = self.git(r, "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        self.assertEqual(p.returncode, 0, p.stderr)
        (Path(r) / "tests/fixture.bin").write_bytes(b"\x00\x03")
        self.git(r, "add", "-A")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 1); self.assertIn("binario vigilado", out)

    def test_ratchet_permite_binario_nuevo(self):
        r = self.repo_git({"tests/test_core.py": "def test_a():\n    assert 1 == 1\n"})
        (Path(r) / "tests/fixture.bin").write_bytes(b"\x00\x01")
        self.git(r, "add", "-A")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 0, out)

    def test_ratchet_varias_rutas_por_coma(self):
        r = self.repo_git({"sgp.yaml": sgp_yaml(ratchet="tests, extras"),
                           "tests/test_core.py": "def test_a():\n    assert 1 == 1\n",
                           "extras/test_extra.py": "def test_b():\n    assert 1 == 1\n"})
        (Path(r) / "extras/test_extra.py").write_text("def test_b():\n    pass\n")
        self.git(r, "add", "-A")
        rc, out = self.run_check(r, "--ratchet")
        self.assertEqual(rc, 1); self.assertIn("extras/test_extra.py", out)


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


class CommitMsg(Base):
    """--commit-msg: falla cerrado, valida la convención y sella con las tres puertas re-ejecutadas."""

    def repo_msg(self, files=None):
        r = self.repo({"changes/CHG-001-x.md": change(), **(files or {})})
        self.git(r, "init", "-q"); self.git(r, "config", "user.email", "a@b.c"); self.git(r, "config", "user.name", "t")
        self.git(r, "add", "-A")
        p = self.git(r, "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        self.assertEqual(p.returncode, 0, p.stderr)
        return r

    def run_msg(self, root, texto):
        f = Path(root) / "_msg.tmp"
        f.write_text(texto, encoding="utf-8")
        p = subprocess.run([PY, CHECK, "--root", root, "--today", "2026-09-24", "--commit-msg", str(f)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=_env({"PYTHONIOENCODING": "utf-8"}))
        return p.returncode, p.stdout + p.stderr, f.read_text(encoding="utf-8")

    def test_sin_fichero_falla_cerrado(self):
        p = subprocess.run([PY, CHECK, "--root", self.repo({}), "--commit-msg", ""], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", env=_env())
        self.assertEqual(p.returncode, 1)
        self.assertIn("fichero del mensaje", p.stdout + p.stderr)

    def test_mensaje_vacio_falla(self):
        rc, out, _ = self.run_msg(self.repo_msg(), "\n  \n")
        self.assertEqual(rc, 1); self.assertIn("vacío", out)

    def test_asunto_sin_convencion_falla(self):
        rc, out, _ = self.run_msg(self.repo_msg(), "arreglar cosas varias\n")
        self.assertEqual(rc, 1); self.assertIn("convención", out)

    def test_dos_cambios_en_un_commit_falla(self):
        rc, out, _ = self.run_msg(self.repo_msg(), "feat: migración CHG-001 y CHG-002\n")
        self.assertEqual(rc, 1); self.assertIn("CHG-001, CHG-002", out)

    def test_sella_con_tres_puertas(self):
        rc, out, texto = self.run_msg(self.repo_msg(), "feat(tools): añade la guarda\n\nCuerpo del cambio.\n")
        self.assertEqual(rc, 0, out)
        self.assertIn("Gate: sgp_check 0 err | sgp_review OK | ratchet sin-tests", texto)

    def test_ignora_comentarios_y_tijera_de_git(self):
        # COMMIT_EDITMSG real de `git commit -v`: comentarios del índice y diff tras la tijera.
        # Solo cuenta el mensaje: ni el diff ni los comentarios lo rechazan, y el fichero final
        # queda con el mensaje limpio + sello (antes de la tijera, que Git descarta al limpiar).
        bruto = ("feat: cierra CHG-001\n\n# Changes to be committed:\n"
                 "#\tmodified:   changes/CHG-002-y.md\n"
                 "# ------------------------ >8 ------------------------\n"
                 "# Everything below it will be ignored.\n"
                 "diff --git a/changes/CHG-002-y.md b/changes/CHG-002-y.md\n+CHG-003\n")
        rc, out, texto = self.run_msg(self.repo_msg(), bruto)
        self.assertEqual(rc, 0, out)
        self.assertIn("Gate: ", texto)
        self.assertNotIn("# Changes to be committed", texto)
        self.assertNotIn("diff --git", texto)

    def test_solo_comentarios_es_mensaje_vacio(self):
        rc, out, _ = self.run_msg(self.repo_msg(), "# Changes to be committed:\n#\tmodified: x\n")
        self.assertEqual(rc, 1); self.assertIn("vacío", out)

    def test_estructura_valida_el_indice_no_el_arbol(self):
        # El índice pierde sgp.yaml pero el árbol lo conserva: el sello debe hablar del commit.
        r = self.repo_msg()
        self.git(r, "rm", "--cached", "-q", "sgp.yaml")
        self.assertTrue((Path(r) / "sgp.yaml").is_file())
        rc, out, texto = self.run_msg(r, "feat: x\n")
        self.assertEqual(rc, 1); self.assertIn("falta sgp.yaml", out); self.assertNotIn("Gate:", texto)

    def test_revision_en_rojo_rechaza_sin_sello(self):
        pendiente = ("- [ ] T001 [EXP-001] uno\n  Hecho cuando: pasa\n"
                     "- [x] T002 [EXP-002] dos\n  Hecho cuando: pasa\n")
        r = self.repo_msg({"changes/CHG-001-x.md": change(tasks=pendiente),
                           "docs/LOG-PROCESO.md": "| Fecha | # | Tipo | Qué | Estado | Referencia |\n"
                                                  "|---|---|---|---|---|---|\n"})
        (Path(r) / "changes/CHG-001-x.md").write_text(
            change(tasks=pendiente.replace("- [ ] T001", "- [x] T001")), encoding="utf-8")
        self.git(r, "add", "-A")
        rc, out, texto = self.run_msg(r, "feat: cierra la tarea\n")
        self.assertEqual(rc, 1); self.assertIn("ronda de revisión", out); self.assertNotIn("Gate:", texto)

    def test_sello_idempotente(self):
        r = self.repo_msg()
        rc, out, texto = self.run_msg(r, "feat: x\n")
        self.assertEqual(rc, 0, out)
        rc, out, texto2 = self.run_msg(r, texto)
        self.assertEqual(rc, 0, out)
        self.assertEqual(texto2.count("Gate:"), 1)

    def test_merge_sin_sello(self):
        rc, _, texto = self.run_msg(self.repo_msg(), "Merge branch 'algo' en main\n")
        self.assertEqual(rc, 0); self.assertNotIn("Gate:", texto)

    def test_estructura_en_rojo_rechaza_sin_sello(self):
        r = self.repo_msg({"sgp.yaml": None})
        rc, out, texto = self.run_msg(r, "feat: x\n")
        self.assertEqual(rc, 1); self.assertIn("falta sgp.yaml", out); self.assertNotIn("Gate:", texto)

    def test_ratchet_en_rojo_rechaza_sin_sello(self):
        r = self.repo_msg({"tests/test_core.py": "def test_a():\n    assert 1 == 1\n"})
        (Path(r) / "tests/test_core.py").write_text("def test_a():\n    pass\n")
        self.git(r, "add", "-A")
        rc, out, texto = self.run_msg(r, "feat: toca pruebas\n")
        self.assertEqual(rc, 1); self.assertIn("SGP_TESTS_APPROVED=1", out); self.assertNotIn("Gate:", texto)


class HookSh(Base):
    """El wrapper `tools/commit-msg` (sh), de extremo a extremo donde hay sh (Git Bash/CI)."""

    @unittest.skipUnless(shutil.which("sh"), "sin sh en PATH: se omite el wrapper")
    def test_wrapper_valida_y_sella(self):
        # La puerta de estructura corre sin --today: el cambio empieza hoy para no agotar apetito.
        r = self.repo({"changes/CHG-001-x.md": change(inicio=datetime.date.today().isoformat())})
        tools = Path(r) / "tools"
        tools.mkdir()
        for n in ("sgp_check.py", "sgp_review.py", "commit-msg"):
            shutil.copy2(Path(__file__).with_name(n), tools / n)
        self.git(r, "init", "-q"); self.git(r, "config", "user.email", "a@b.c"); self.git(r, "config", "user.name", "t")
        self.git(r, "add", "-A")
        p = self.git(r, "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        self.assertEqual(p.returncode, 0, p.stderr)
        msg = Path(r) / "_msg.tmp"
        msg.write_text("feat: x\n", encoding="utf-8")
        p = subprocess.run(["sh", "tools/commit-msg", str(msg)], cwd=r, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env=_env({"PYTHONIOENCODING": "utf-8"}))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("Gate: sgp_check 0 err", msg.read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("sh"), "sin sh en PATH: se omite el wrapper")
    def test_wrapper_avisa_si_las_herramientas_son_viejas(self):
        # Hook nuevo sobre tools/ viejo: falla cerrado, pero con instrucción de actualización.
        r = self.repo({"changes/CHG-001-x.md": change()})
        tools = Path(r) / "tools"
        tools.mkdir()
        (tools / "sgp_check.py").write_text("print('usage: sgp_check.py')\n", encoding="utf-8")
        shutil.copy2(Path(__file__).with_name("commit-msg"), tools / "commit-msg")
        self.git(r, "init", "-q"); self.git(r, "config", "user.email", "a@b.c"); self.git(r, "config", "user.name", "t")
        self.git(r, "add", "-A")
        p = self.git(r, "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        self.assertEqual(p.returncode, 0, p.stderr)
        msg = Path(r) / "_msg.tmp"
        msg.write_text("feat: x\n", encoding="utf-8")
        p = subprocess.run(["sh", "tools/commit-msg", str(msg)], cwd=r, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=_env())
        self.assertEqual(p.returncode, 1)
        self.assertIn("actualiza tools/ del kit", p.stdout + p.stderr)


class Hecho(Base):
    """Cierre duro: 'hecho' exige consistencia de cierre (antes: ningún test cubría el salto)."""
    CRIT_OK = "- [x] todo cubierto con prueba en verde\n- [x] demo del flujo pasó\n"

    def test_hecho_consistente_pasa(self):
        r = self.repo({"changes/CHG-001-x.md": change(estado="hecho", criterios=self.CRIT_OK)})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 0, out)

    def test_hecho_criterio_sin_marcar_falla(self):
        r = self.repo({"changes/CHG-001-x.md": change(estado="hecho", criterios="- [x] uno\n- [ ] dos sin marcar\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("criterio(s) sin marcar", out); self.assertIn("dos sin marcar", out)

    def test_hecho_tarea_pendiente_falla(self):
        r = self.repo({"changes/CHG-001-x.md": change(estado="hecho", criterios=self.CRIT_OK,
                        tasks="- [ ] T001 [EXP-001] uno\n  Hecho cuando: pasa\n- [x] T002 [EXP-002] dos\n  Hecho cuando: pasa\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("tareas pendientes (T001)", out)

    def test_hecho_sin_seccion_criterios_falla(self):
        ch = change(estado="hecho", criterios=self.CRIT_OK).replace("## Criterios de finalización\n", "")
        rc, out = self.run_check(self.repo({"changes/CHG-001-x.md": ch}))
        self.assertEqual(rc, 1); self.assertIn("sin sección «## Criterios de finalización»", out)

    def test_hecho_sin_tareas_falla(self):
        r = self.repo({"changes/CHG-001-x.md": change(estado="hecho", criterios=self.CRIT_OK, tasks="")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("'hecho' sin tareas", out)

    def test_hecho_tarea_sin_hecho_cuando_falla(self):
        r = self.repo({"changes/CHG-001-x.md": change(estado="hecho", criterios=self.CRIT_OK,
                        tasks="- [x] T001 [EXP-001] uno\n- [x] T002 [EXP-002] dos\n  Hecho cuando: pasa\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("sin «Hecho cuando:»", out)

    def test_hecho_con_marca_por_aclarar_falla(self):
        r = self.repo({"changes/CHG-001-x.md": change(estado="hecho", criterios=self.CRIT_OK, extra="\n[POR-ACLARAR] duda\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("[POR-ACLARAR]", out)

    def test_hecho_sin_criterios_falla(self):
        r = self.repo({"changes/CHG-001-x.md": change(estado="hecho", criterios="")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("sin criterios de finalización", out)

    def test_hecho_criterio_con_asterisco_sin_marcar_falla(self):
        r = self.repo({"changes/CHG-001-x.md": change(estado="hecho", criterios="- [x] uno\n* [ ] otro\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 1); self.assertIn("1 criterio(s) sin marcar", out)

    def test_hecho_no_deriva_con_specs(self):
        # Los cruces externos (specs/, carril) se saltan: pueden cambiar después de cerrado el cambio.
        r = self.repo({"changes/CHG-001-x.md": change(estado="hecho", ids="[EXP-001, EXP-009]", criterios=self.CRIT_OK)})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 0, out)

    def test_cancelado_sigue_saltandose(self):
        r = self.repo({"changes/CHG-001-x.md": change(estado="cancelado",
                        tasks="- [ ] T001 [EXP-001] uno\n  Hecho cuando: pasa\n")})
        rc, out = self.run_check(r)
        self.assertEqual(rc, 0, out)


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
