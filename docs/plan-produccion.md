# Plan hacia producción — ia-sdlc (SGP Lite + política de ingeniería)

> **Versión del plan:** 1 · **Fecha:** 2026-10-09 · **Base:** rama `master`, `kit/VERSION` = `1.4.0`
> **Objetivo:** cerrar los huecos que impiden publicar este repositorio como producto mantenible
> (CI, artefacto de distribución versionado, gobernanza, coherencia del ejemplo, licencia),
> **sin cambiar la metodología**.
> **Diagnóstico de origen:** análisis del 2026-10-09 contrastado con GitHub Spec Kit, OpenSpec,
> BMAD-METHOD y Kiro (ver §9).

## Índice

- [0. Cómo ejecutar este plan (reglas para el agente)](#0-cómo-ejecutar-este-plan-reglas-para-el-agente)
- [1. Estado de partida (verificado)](#1-estado-de-partida-verificado)
- [2. Decisiones humanas (D1–D3)](#2-decisiones-humanas-d1d3)
- [3. Fases y tareas](#3-fases-y-tareas)
  - [Fase P0 — Publicación mínima](#fase-p0--publicación-mínima)
  - [Fase P1 — Coherencia y robustez](#fase-p1--coherencia-y-robustez)
  - [Fase P2 — Producto (priorizado)](#fase-p2--producto-priorizado)
- [4. Matriz de verificación final](#4-matriz-de-verificación-final)
- [5. Orden de commits sugerido](#5-orden-de-commits-sugerido)
- [6. Rollback](#6-rollback)
- [7. Registro de ejecución](#7-registro-de-ejecución)
- [8. Hallazgos fuera de alcance](#8-hallazgos-fuera-de-alcance)
- [9. Referencias del contraste](#9-referencias-del-contraste)

---

## 0. Cómo ejecutar este plan (reglas para el agente)

1. **Fases en orden** (P0 → P1 → P2). Dentro de una fase, **una tarea a la vez**; no empezar una
   tarea mientras la anterior no esté `[x]`.
2. **Evidencia antes de editar**: antes de tocar un archivo, leerlo y registrar en §7 los archivos
   leídos (con líneas) y el hallazgo relevante, junto con la salida real de cada comando. Sin esa
   evidencia, la única acción permitida es leer.
3. **"Hecho cuando" es el criterio de aceptación**: no se marca `[x]` sin la **salida real** de los
   comandos (no vale "debería pasar"). La evidencia se pega en §7.
4. **Convenciones del repo**: documentación en español; finales de línea LF (`.gitattributes`:
   `* text=auto`); mensajes de commit en imperativo español; los tools del kit son **solo stdlib**
   (Python 3.8+); **ninguna dependencia nueva** sin ADR.
5. **Ley de la casa**: `docs/system-engineering-policy.SKILL.md` (norma) y
   `docs/protocolo-ingenieria-senior.SKILL.md` (procedimiento). Si algo de este plan las
   contradice, manda la política — y se anota en §8.
6. Comandos desde la raíz del repo (`<ruta-del-repo>`) salvo que se indique `workdir` en el bloque.
7. Todo lo que aparezca fuera de las tareas se anota en §8, **no se ejecuta**.
8. A medida que se completa una tarea: marcar `[x]` aquí, dejar la evidencia en §7 y commitear con
   el mensaje indicado en cada tarea.

**Verificación transversal** (se repite al cierre de cada fase; resultados esperados hoy):

| Comando | Esperado |
|---|---|
| `cd kit; python -m unittest discover -s tools -p "test_*.py" -v` | termina en `OK` (hoy: 40 tests) |
| `python kit/tools/sgp_check.py --root examples/descuento --run` | `Resumen: 0 error(es), 0 aviso(s).` |

---

## 1. Estado de partida (verificado)

| Hecho verificado | Evidencia (2026-10-09) |
|---|---|
| 40 tests del kit en verde | `python -m unittest discover -s tools -p "test_*.py"` → `Ran 40 tests ... OK` |
| Ejemplo ejecutable en verde | `sgp_check --root examples/descuento --run` → `0 error(es), 0 aviso(s)` |
| Sin CI | no existe `.github/` |
| Sin releases ni remoto | `git tag` vacío; `git remote -v` vacío; 17 commits, rama `master` |
| `sgp-lite.zip` **untracked** | `git ls-files -- sgp-lite.zip` vacío; sin embargo `README.md` (árbol, línea 55) y `docs/manual-usuario.md` lo referencian |
| Ejemplo desincronizado | `examples/descuento/skills/` tiene **5** de las **8** skills del kit (faltan `sgp-documento-requerimientos`, `protocolo-ingenieria-senior`, `system-engineering-policy`); `examples/descuento/AGENTS.md` lista 5 |
| Copias del ejemplo íntegras | `examples/descuento/tools/{sgp_check,sync_skills}.py` y las 5 skills comunes: **byte a byte iguales** al kit |
| Licencia sin titular | `LICENSE`: `Copyright (c) 2026` (sin nombre) |
| Frontera de confianza sin documentar | `kit/tools/sgp_check.py:222` ejecuta `sgp.yaml` con `shell=True`; `kit/tools/pre-commit` ejecuta scripts del repo |
| Parser YAML casero sin documentar | `kit/tools/sgp_check.py:56-71` (`read_config`) soporta un subconjunto propio |

---

## 2. Decisiones humanas (D1–D3)

| # | Decisión | Estado | Default adoptado |
|---|---|---|---|
| **D1** | URL del remoto GitHub | **PENDIENTE** (la provee el humano antes de P0.4) | — |
| **D2** | Titular de la licencia | Abierta | `the ia-sdlc authors` (P1.2 lo aplica; el humano puede reemplazarlo) |
| **D3** | Distribución del zip | Abierta | **Versionar `sgp-lite.zip` en el repo** + guarda de consistencia (P0.2). Alternativa documentada: asset de Release (P0.4, opcional) |

**Regla**: si una decisión pendiente bloquea una tarea, marcarla `BLOQUEADA (D#)` en §7 y continuar con la siguiente tarea de la misma fase que no dependa de ella.

---

## 3. Fases y tareas

### Fase P0 — Publicación mínima

#### [x] Tarea P0.1 — CI en GitHub Actions

- **Objetivo**: que cada push/PR corra los tests del kit y el verificador sobre el ejemplo en una matriz multi-OS/multi-Python.
- **Depende de**: nada.
- **Archivos**: `.github/workflows/ci.yml` **(nuevo)**.
- **Pasos**:
  1. Crear el directorio `.github/workflows/`.
  2. Crear `.github/workflows/ci.yml` con este contenido **exacto**:

```yaml
name: CI

on:
  push:
  pull_request:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  tests:
    name: tests · ${{ matrix.os }} · py${{ matrix.python }}
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            python: "3.8"
          - os: ubuntu-latest
            python: "3.12"
          - os: windows-latest
            python: "3.12"
    defaults:
      run:
        working-directory: kit
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - name: Pruebas del kit
        run: python -m unittest discover -s tools -p "test_*.py" -v

  ejemplo:
    name: ejemplo descuento · sgp_check --run
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Verificador sobre el ejemplo
        run: python kit/tools/sgp_check.py --root examples/descuento --run
```

  3. **Nota 3.8**: si `setup-python` no consigue Python 3.8 para `ubuntu-latest`, cambiar **solo esa
     entrada** a `os: ubuntu-22.04`. No eliminar la leg 3.8: el kit promete Python 3.8+.
- **Verificación (local, antes de publicar)**:
  - `cd kit; python -m unittest discover -s tools -p "test_*.py" -v` → `OK`.
  - `python kit/tools/sgp_check.py --root examples/descuento --run` → `Resumen: 0 error(es), 0 aviso(s).`
- **Verificación (en GitHub)**: el workflow aparece y termina **verde** en las 3 combinaciones (tras P0.4).
- **Evidencia a registrar**: salidas locales de los comandos + URL del run verde.
- **Hecho cuando**: `.github/workflows/ci.yml` existe, los comandos locales dan lo esperado y, tras P0.4, los 3 jobs están verdes.
- **Commit**: `Añadir CI: tests del kit y ejemplo en matriz Linux/Windows y Python 3.8/3.12`

#### [x] Tarea P0.2 — Zip versionado, guarda de consistencia y tag

- **Objetivo**: que un `git clone` traiga `sgp-lite.zip` y que sea imposible que el zip y el kit diverjan sin que los tests fallen.
- **Depende de**: nada (aplica D3 default).
- **Archivos**: `sgp-lite.zip` (pasa a versionado), `.gitattributes` (1 línea), `kit/tools/test_kit_consistency.py` **(nuevo, repo-only)**.
- **Pasos**:
  1. Regenerar el zip (debe decir "Creado sgp-lite.zip (N archivos, kit 1.4.0)"):
     `python kit/tools/sgp_zip.py --source kit --dest sgp-lite.zip`
  2. Añadir al final de `.gitattributes`:
     `sgp-lite.zip binary`
  3. Crear `kit/tools/test_kit_consistency.py` con las clases **Manifiesto** y **Zip** de este contenido (la clase **Ejemplo** se añade en P1.1; ver el código completo allí):

```python
#!/usr/bin/env python3
"""Pruebas de consistencia del repositorio del kit (no viajan en el zip).

1. Cada entrada de sgp-kit.manifest existe en kit/.
2. El zip versionado coincide con el manifiesto: mismos archivos y mismo contenido
   (comparado con finales de linea normalizados CRLF->LF, para no depender de core.autocrlf).

Es del repositorio del kit: por eso no está en sgp-kit.manifest.

    python -m unittest tools/test_kit_consistency.py -v
"""
import os
import sys
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sgp_kit  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
KIT = REPO / "kit"
EJEMPLO = REPO / "examples" / "descuento"
ZIP = REPO / "sgp-lite.zip"


def expandidos():
    """Rutas relativas de todos los archivos managed + seeded del manifiesto."""
    managed, seeded = sgp_kit.load_manifest(KIT)
    files = []
    for entry in managed + seeded:
        files += sgp_kit.expand(KIT, entry)
    return files


class ManifiestoTests(unittest.TestCase):
    def test_entradas_del_manifiesto_existen(self):
        for rel in expandidos():
            self.assertTrue((KIT / rel).exists(), f"el manifiesto referencia {rel}, que no existe")


class ZipTests(unittest.TestCase):
    def test_zip_versionado_coincide_con_el_manifiesto(self):
        if not ZIP.exists():
            self.skipTest("sgp-lite.zip no está versionado (ver docs/plan-produccion.md, P0.2)")
        esperados = set(expandidos())
        with zipfile.ZipFile(ZIP) as z:
            self.assertEqual(esperados, set(z.namelist()),
                             "el zip no tiene exactamente los archivos del manifiesto")
            for rel in sorted(esperados):
                self.assertEqual((KIT / rel).read_bytes(), z.read(rel),
                                 f"contenido desactualizado en el zip: {rel}")


if __name__ == "__main__":
    unittest.main()
```

  **Nota de implementacion**: la guarda compara contenido con finales de linea normalizados
  (normalizado(b) = b.replace(b"\r\n", b"\n")) para no depender de core.autocrlf ni del SO. El zip
  se genera desde el arbol de trabajo, asi que incluye cambios sin commitear de kit/.

  4. Correr todos los tests (el nuevo incluido): `cd kit; python -m unittest discover -s tools -p "test_*.py" -v` → `OK`.
  5. Commit y tag:
     - `git add .gitattributes sgp-lite.zip kit/tools/test_kit_consistency.py`
     - `git commit -m "Versionar sgp-lite.zip y guardar su consistencia con sgp-kit.manifest"`
     - `git tag -a v1.4.0 -m "SGP Lite 1.4.0: política y protocolo como skills del kit (6 proceso + 2 comportamiento)"`
- **Verificación**:
  - `git ls-files -- sgp-lite.zip` → devuelve la ruta (ya versionado).
  - `cd kit; python -m unittest tools/test_kit_consistency.py -v` → `OK`.
  - Manipulación negativa (obligatoria): editar temporalmente un archivo del kit cubierto por el
    manifiesto (p. ej. añadir una línea a `kit/METODOLOGIA.md`), correr el test del zip → debe
    **FALLAR** con "contenido desactualizado". Revertir la edición y volver a correr → `OK`.
- **Evidencia a registrar**: salida de los tests (verde y la falla inducida) + `git tag -l`.
- **Hecho cuando**: zip versionado, tag creado, guarda en verde y la manipulación negativa falla como se describe.
- **Commit**: el del paso 5.

#### [x] Tarea P0.3 — Gobernanza (contribución, seguridad, conducta, plantillas)

- **Objetivo**: que un tercero sepa cómo contribuir, cómo reportar un problema de seguridad y qué esperar del repo.
- **Depende de**: nada.
- **Archivos (nuevos)**: `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
  `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md`,
  `.github/pull_request_template.md`; edición de `README.md` (sección "Contribuir").
- **Pasos y contenido**:

  1. Crear `CONTRIBUTING.md`:

```markdown
# Contribuir a ia-sdlc

Gracias por aportar. Este repo contiene la metodología SGP Lite (`kit/`), la política de ingeniería
(`docs/system-engineering-policy.SKILL.md`) y un ejemplo ejecutable (`examples/descuento/`).

## Antes de abrir un PR

1. Corre las pruebas del kit: `cd kit && python -m unittest discover -s tools -p "test_*.py" -v`
   (deben quedar en `OK`).
2. Corre el verificador sobre el ejemplo: `python kit/tools/sgp_check.py --root examples/descuento --run`
   (debe terminar en `Resumen: 0 error(es), 0 aviso(s).`).
3. Si tu cambio toca `docs/` o `kit/skills/{protocolo-ingenieria-senior,system-engineering-policy}`,
   recuerda la guarda de sincronía (`kit/tools/test_policy_sync.py`): las copias deben ser idénticas.
4. Si creaste o cambiaste archivos del kit cubiertos por `sgp-kit.manifest`, regenera el zip:
   `python kit/tools/sgp_zip.py --source kit --dest sgp-lite.zip` y corre
   `kit/tools/test_kit_consistency.py`.

## Reglas

- Prohibido borrar o debilitar pruebas para hacer pasar un cambio (ratchet: `tools/pre-commit`).
- Un cambio = un alcance declarado; lo demás se reporta, no se mezcla.
- Los tools son solo-stdlib (Python 3.8+): no agregues dependencias.
- Describe en el PR: qué problema resuelve, qué verificación ejecutaste y su salida real.

## Licencia

Al contribuir aceptas que tu aporte se distribuya bajo la licencia MIT de este repositorio.
```

  2. Crear `SECURITY.md`:

```markdown
# Seguridad

## Reportar una vulnerabilidad

Abre un **borrador de aviso de seguridad** en la pestaña *Security* del repositorio
("Report a vulnerability"). No abras un issue público para un problema de seguridad.

## Frontera de confianza (importante)

Este kit ejecuta comandos que declares en `sgp.yaml` usando `shell=True`
(`kit/tools/sgp_check.py`), y el hook `kit/tools/pre-commit` ejecuta el verificador y el ratchet.
Consecuencias:

- No instales ni ejecutes el kit sobre un repositorio cuyo `sgp.yaml` o `tools/` no hayas revisado.
- El kit asume que el repositorio donde vive es de confianza; no es un sandbox.
- No incluyas secretos en `sgp.yaml`, `specs/`, `changes/` ni en la salida de los sensores.
```

  3. Crear `CODE_OF_CONDUCT.md` (base: Contributor Covenant v2.1, texto mínimo):

```markdown
# Código de conducta

Este proyecto adopta el [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

**Nuestro compromiso:** un entorno abierto y libre de acoso para todas las personas que participan.

**Comportamiento esperado:** lenguaje respetuoso, crítica técnica sobre el trabajo y no sobre la
persona, y disposición a aceptar correcciones con evidencia.

**Comportamiento inaceptable:** acoso, insultos, ataques personales y publicación de información
privada de terceros.

**Aplicación:** los mantenedores pueden eliminar comentarios, cerrar hilos o bloquear cuentas ante
incumplimientos. Para reportar un incidente, usa el canal privado de los mantenedores o abre un
issue pidiendo contacto privado; los reportes se tratan con discreción.
```

  4. Crear `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Reporte de bug
about: Algo del kit o del ejemplo no funciona como se documenta
labels: bug
---

**Qué esperabas que pasara**

**Qué pasó realmente** (pega la salida real del comando)

**Cómo reproducirlo** (comandos exactos, en orden)

**Entorno** (SO, versión de Python, versión del kit: `kit/VERSION`)
```

  5. Crear `.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Propuesta
about: Una mejora o una idea para el kit, la metodología o la documentación
labels: enhancement
---

**Problema que resuelve** (no la solución: el dolor concreto)

**Propuesta concreta**

**Alternativa considerada**

**¿Afecta a `specs/`/`changes/` o solo al kit?**
```

  6. Crear `.github/pull_request_template.md`:

```markdown
## Qué cambia

## Verificación (pega las salidas reales)
- [ ] `cd kit && python -m unittest discover -s tools -p "test_*.py" -v`
- [ ] `python kit/tools/sgp_check.py --root examples/descuento --run`
- [ ] Si toqué kit o skills: zip regenerado (`python kit/tools/sgp_zip.py --source kit --dest sgp-lite.zip`) y guardas en verde

## Fuera de alcance (lo que NO toca este PR)
```

  7. Añadir al final de `README.md`, antes de `## Licencia`, esta sección:

```markdown
## Contribuir

Lee [`CONTRIBUTING.md`](CONTRIBUTING.md) (pruebas que debes correr, regenerar el zip, reglas del
ratchet) y [`SECURITY.md`](SECURITY.md) (frontera de confianza del kit). Para problemas de
seguridad, usa el aviso privado del repositorio; para todo lo demás, abre un issue.
```

- **Verificación**: `git status --porcelain` lista los 7 archivos nuevos y `README.md`; los enlaces
  citados (`CONTRIBUTING.md`, `SECURITY.md`) existen en la raíz.
- **Evidencia a registrar**: listado de archivos creados + enlaces verificados.
- **Hecho cuando**: los 6 archivos nuevos existen con su contenido y el README enlaza CONTRIBUTING/SECURITY.
- **Commit**: `Añadir gobernanza: guía de contribución, política de seguridad, código de conducta y plantillas de issues/PR`

#### [ ] Tarea P0.4 — Publicar (remoto, push, release opcional) — **BLOQUEADA (D1)** hasta tener la URL

- **Objetivo**: que el repositorio y el tag queden publicados y el CI corra verde.
- **Depende de**: D1 (URL del remoto), P0.1 y P0.2 completas.
- **Pasos**:
  1. `git remote add origin <URL-de-D1>`
  2. `git push -u origin master`
  3. `git push origin v1.4.0`
  4. (Opcional, si hay `gh` autenticado) `gh release create v1.4.0 sgp-lite.zip --title "v1.4.0" --notes "SGP Lite 1.4.0: política y protocolo como skills del kit (6 proceso + 2 comportamiento)"`
- **Verificación**: `git remote -v` muestra origin; la pestaña Actions muestra el run **verde**; el tag `v1.4.0` es visible.
- **Evidencia a registrar**: URL del run verde + `git remote -v`.
- **Hecho cuando**: CI verde en GitHub y tag publicado.
- **Commit**: no aplica (solo push).

---

### Fase P1 — Coherencia y robustez

#### [ ] Tarea P1.1 — Sincronizar el ejemplo con el kit (8 skills) + guarda

- **Objetivo**: que el ejemplo deje de estar desactualizado y que ninguna desincronización futura pase inadvertida.
- **Depende de**: P0.2 (crea `test_kit_consistency.py`).
- **Archivos**: `examples/descuento/skills/*` (3 dirs nuevos), `examples/descuento/AGENTS.md` (1 línea),
  `kit/tools/test_kit_consistency.py` (se añade la clase **Ejemplo**).
- **Pasos**:
  1. Copiar las 3 skills que faltan (desde la raíz):
     ```powershell
     Copy-Item -Recurse -Force kit/skills/sgp-documento-requerimientos, kit/skills/protocolo-ingenieria-senior, kit/skills/system-engineering-policy examples/descuento/skills/
     ```
  2. En `examples/descuento/AGENTS.md`, reemplazar la línea de "Skills disponibles" por la misma
     redacción de `kit/AGENTS.md` (8 skills: 6 de proceso + 2 de comportamiento), sustituyendo
     `<tu-agente>` según el ejemplo.
  3. Añadir a `kit/tools/test_kit_consistency.py`, antes de `if __name__ == "__main__":`, esta clase:

```python
class EjemploTests(unittest.TestCase):
    def test_skills_del_ejemplo_iguales_al_kit(self):
        kit_skills = sorted(p.name for p in (KIT / "skills").iterdir() if p.is_dir())
        ej_skills = sorted(p.name for p in (EJEMPLO / "skills").iterdir() if p.is_dir())
        self.assertEqual(kit_skills, ej_skills, "el ejemplo debe tener las mismas skills que el kit")
        for name in kit_skills:
            self.assertEqual(
                (KIT / "skills" / name / "SKILL.md").read_bytes(),
                (EJEMPLO / "skills" / name / "SKILL.md").read_bytes(),
                f"examples/descuento/skills/{name}/SKILL.md difiere del kit",
            )

    def test_tools_del_ejemplo_iguales_al_kit(self):
        for rel in ("sgp_check.py", "sync_skills.py"):
            self.assertEqual(
                (KIT / "tools" / rel).read_bytes(),
                (EJEMPLO / "tools" / rel).read_bytes(),
                f"examples/descuento/tools/{rel} difiere del kit",
            )

    def test_agents_del_ejemplo_lista_las_skills_del_kit(self):
        texto = (EJEMPLO / "AGENTS.md").read_text(encoding="utf-8")
        for name in sorted(p.name for p in (KIT / "skills").iterdir() if p.is_dir()):
            self.assertIn(name, texto, f"AGENTS.md del ejemplo no menciona {name}")
```

  4. Correr: `cd kit; python -m unittest discover -s tools -p "test_*.py" -v` → `OK`.
  5. Commit: `git add examples/descuento kit/tools/test_kit_consistency.py && git commit -m "Sincronizar el ejemplo con el kit (8 skills) y guardar la consistencia"`
- **Verificación**: suite completa → `OK`; `examples/descuento/skills/` tiene 8 dirs; manipulación
  negativa: cambiar un byte de una copia del ejemplo y correr `test_kit_consistency` → debe **FALLAR**;
  revertir.
- **Evidencia a registrar**: listado de `examples/descuento/skills/` + salida de los tests.
- **Hecho cuando**: ejemplo con 8 skills, AGENTS.md actualizado, guarda en verde y la manipulación negativa falla.
- **Commit**: el del paso 5.

#### [ ] Tarea P1.2 — Titular de licencia

- **Objetivo**: que la licencia tenga titular (aplica **D2**, default `the ia-sdlc authors`).
- **Depende de**: nada.
- **Archivos**: `LICENSE` (1 línea).
- **Pasos**:
  1. Cambiar `Copyright (c) 2026` por `Copyright (c) 2026 the ia-sdlc authors` (o el titular que
     indique el humano en D2).
  2. Commit: `git add LICENSE && git commit -m "Completar el titular de la licencia MIT"`
- **Verificación**: `Select-String -LiteralPath LICENSE -Pattern 'Copyright'` → una línea con titular.
- **Hecho cuando**: la línea de copyright tiene titular.
- **Commit**: el del paso 2.

#### [ ] Tarea P1.3 — Documentar y probar el subconjunto YAML de `sgp.yaml`

- **Objetivo**: que el parser casero (`kit/tools/sgp_check.py:56-71`) no sorprenda: subconjunto documentado y probado.
- **Depende de**: nada.
- **Archivos**: `kit/sgp.yaml` (comentario de cabecera), `kit/LEEME.md` (1 frase), `kit/tools/test_sgp_check.py` (1 test).
- **Pasos**:
  1. Añadir a `kit/sgp.yaml`, debajo del comentario de la primera línea, este bloque:

```yaml
# Subconjunto soportado por el verificador: secciones `clave:` y dentro pares `clave: valor`
# (con o sin comillas). No hay listas YAML ni anidamiento: las líneas que no son `clave: valor`
# se ignoran. Los comentarios empiezan con # (fuera de comillas). Ver tools/sgp_check.py (read_config).
```

  2. En `kit/LEEME.md`, tras la línea que menciona `sgp-kit.manifest` (sección "Instalar y actualizar"), añadir:
     El archivo `sgp.yaml` usa un subconjunto simple de YAML (secciones y pares `clave: valor`); no
     admite listas ni anidamiento.
  3. Añadir a `kit/tools/test_sgp_check.py`, en la clase `Estructura`, este test:

```python
    def test_yaml_con_estructura_no_soportada_no_crashea(self):
        # listas y anidamiento se ignoran; comillas protegen el # interno
        y = ("rutas:\n  tests: tests\nlistas:\n  - uno\n  - dos\n"
             "comandos:\n"
             "  build: \"echo # no es comentario\"\n"
             "  tests: \"\"\n"
             "  lint: \"\"\n"
             "  test_por_requisito: \"\"\n")
        rc, out = self.run_check(self.repo({"sgp.yaml": y}), "--run")
        self.assertEqual(rc, 0, out)
```

  4. Correr la suite completa → `OK`.
  5. Commit: `git add kit/sgp.yaml kit/LEEME.md kit/tools/test_sgp_check.py && git commit -m "Documentar y probar el subconjunto YAML de sgp.yaml"`
- **Verificación**: el test nuevo pasa en Windows y Linux (sin dependencias de plataforma).
- **Evidencia a registrar**: salida del test nuevo + suite completa.
- **Hecho cuando**: documentación en `sgp.yaml` y `LEEME.md`, test en verde.
- **Commit**: el del paso 5.

---

### Fase P2 — Producto (priorizado)

#### [ ] Tarea P2.1 — `sgp_check --version`

- **Objetivo**: que el verificador informe la versión del kit, igual que `sgp_kit --version`.
- **Depende de**: nada.
- **Archivos**: `kit/tools/sgp_check.py`, `kit/tools/test_sgp_check.py`.
- **Pasos**:
  1. En `kit/tools/sgp_check.py`, añadir esta función después de `DEFAULTS`:

```python
def read_version(kit_dir):
    v = kit_dir / "VERSION"
    return v.read_text(encoding="utf-8").strip() if v.exists() else "(sin VERSION)"
```

  2. En `main()`: insertar `ap.add_argument("--version", action="store_true", help="muestra la versión del kit y sale")` **después** de la línea `ap.add_argument("--today", ...)` y **antes** de `a = ap.parse_args()`; luego, justo **después** de `a = ap.parse_args()`, insertar:

```python
    if a.version:
        print(read_version(Path(__file__).resolve().parent.parent))
        return 0
```

  No duplicar `a = ap.parse_args()`: ya existe; solo se añade el argumento y el bloque `if`.

  3. Añadir a `kit/tools/test_sgp_check.py`, en `Estructura`:

```python
    def test_cli_version(self):
        p = subprocess.run([PY, CHECK, "--version"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertTrue(p.stdout.strip())
```

  4. Correr la suite completa → `OK`.
  5. Commit: `git add kit/tools/sgp_check.py kit/tools/test_sgp_check.py && git commit -m "Añadir sgp_check --version"`
- **Verificación**: `python kit/tools/sgp_check.py --version` → imprime `1.4.0` (o la versión vigente de `kit/VERSION`).
- **Hecho cuando**: el flag existe y devuelve la versión.
- **Commit**: el del paso 5.

#### [ ] Tarea P2.2 — Badges en README

- **Objetivo**: mostrar estado de CI y licencia en el encabezado.
- **Depende de**: P0.1 y P0.4 (el badge de CI necesita el workflow y el remoto).
- **Archivos**: `README.md` (2 líneas).
- **Pasos**:
  1. Debajo del bloque `>` inicial del README, añadir:

```markdown
[![CI](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
```

  2. Commit: `git add README.md && git commit -m "Añadir badges de CI y licencia al README"`
- **Verificación**: en GitHub, el badge de CI refleja el run de `master`.
- **Hecho cuando**: los badges se ven en el README publicado.
- **Commit**: el del paso 2.

#### [ ] Tarea P2.3 — Ciclo de «deltas» y archivo de specs (BACKLOG — requiere diseño aparte)

- **Objetivo**: evaluar un mecanismo tipo OpenSpec (deltas ADDED/MODIFIED/REMOVED + archivo) para specs que viven años.
- **Depende de**: **NO ejecutar desde este plan.** Requiere un cambio en modo ARQUITECTURA con su
  propio diseño y aprobación (contrato nuevo en `specs/`/`changes/`).
- **Hecho cuando**: exista un diseño aprobado en `changes/` con ADR; este plan solo deja el pendiente registrado.

#### [ ] Tarea P2.4 — Traducción al inglés de README y manual (OPCIONAL)

- **Objetivo**: ampliar adopción fuera del español.
- **Depende de**: decisión del humano (no hay D asignada).
- **Nota**: si se hace, debe ser un archivo espejo por cada documento (p. ej. `README.en.md`,
  `docs/manual-usuario.en.md`) y el README debe enlazarlos; **no** traducir `specs/` ni las plantillas.

---

## 4. Matriz de verificación final

| # | Comando (desde la raíz) | Esperado | Aplica a |
|---|---|---|---|
| V1 | `cd kit; python -m unittest discover -s tools -p "test_*.py" -v` | `OK` (hoy 40 tests; crece con las guardas que añade el plan) | todas las fases |
| V2 | `python kit/tools/sgp_check.py --root examples/descuento --run` | `Resumen: 0 error(es), 0 aviso(s).` | todas las fases |
| V3 | `python kit/tools/sgp_check.py --version` | `1.4.0` | P2.1+ |
| V4 | `git ls-files -- sgp-lite.zip` | ruta listada | P0.2+ |
| V5 | `python kit/tools/sgp_zip.py --source kit --dest sgp-lite.zip` y `cd kit; python -m unittest tools/test_kit_consistency.py -v` | `Creado ... (N archivos, kit 1.4.0)` y `OK` | P0.2+ |
| V6 | GitHub Actions | 3 jobs verdes | P0.1+P0.4 |

## 5. Orden de commits sugerido

1. `Añadir CI: tests del kit y ejemplo en matriz Linux/Windows y Python 3.8/3.12` (P0.1)
2. `Versionar sgp-lite.zip y guardar su consistencia con sgp-kit.manifest` (P0.2; incluye el tag `v1.4.0`)
3. `Añadir gobernanza: guía de contribución, política de seguridad, código de conducta y plantillas de issues/PR` (P0.3)
4. `Sincronizar el ejemplo con el kit (8 skills) y guardar la consistencia` (P1.1)
5. `Completar el titular de la licencia MIT` (P1.2)
6. `Documentar y probar el subconjunto YAML de sgp.yaml` (P1.3)
7. `Añadir sgp_check --version` (P2.1)
8. `Añadir badges de CI y licencia al README` (P2.2)

(P0.4 no tiene commit: solo `push`.)

## 6. Rollback

| Qué | Cómo deshacerlo |
|---|---|
| Un commit del plan | `git revert <hash>` (nunca reescribir `master` publicado) |
| El tag `v1.4.0` (si aún no se publicó) | `git tag -d v1.4.0`; si ya se publicó: `git push origin :refs/tags/v1.4.0` |
| CI molesto | desactivar el workflow desde la pestaña Actions (no borrar el archivo si solo es un fallo transitorio) |
| Zip versionado | `git rm --cached sgp-lite.zip` y quitar la línea de `.gitattributes` (los tests lo saltan con `skipTest`) |

## 7. Registro de ejecución

| Tarea | Estado | Evidencia (salida real / URL) |
|---|---|---|
| P0.1 CI | HECHO (`63318f1`) | suite local 40 OK; `sgp_check --root examples/descuento --run` -> `Resumen: 0 error(es), 0 aviso(s).` |
| P0.2 zip + guarda + tag | HECHO (`9cbbe67`, tag `v1.4.0`) | suite 42 OK; prueba negativa: alterar el kit -> `FAILED (contenido desactualizado en el zip: METODOLOGIA.md)`; restaurar -> OK |
| P0.3 gobernanza | HECHO (`997cdba`) | 6 archivos + `README.md` seccion Contribuir; enlaces CONTRIBUTING/SECURITY verificados |
| P0.4 publicar | BLOQUEADA (D1) | falta la URL del remoto; el tag `v1.4.0` ya existe en local |
| P1.1 ejemplo + guarda | PENDIENTE | |
| P1.2 licencia | PENDIENTE | |
| P1.3 YAML | PENDIENTE | |
| P2.1 --version | PENDIENTE | |
| P2.2 badges | PENDIENTE | |
| P2.3 deltas (backlog) | NO INICIADA | |
| P2.4 EN (opcional) | NO INICIADA | |

## 8. Hallazgos fuera de alcance

- (vacío) — anotar aquí lo que aparezca sin ejecutarlo.

## 9. Referencias del contraste

- GitHub Spec Kit — README oficial: `https://github.com/github/spec-kit` (consultado 2026-10-09).
- OpenSpec — documentación (`docs/getting-started.md`, `docs/concepts.md`, `docs/commands.md`):
  `https://github.com/Fission-AI/OpenSpec` (consultado 2026-10-09).
- BMAD-METHOD — `docs/reference/workflow-map.md` y `docs/reference/agents.md`:
  `https://github.com/bmad-code-org/BMAD-METHOD` (consultado 2026-10-09).
- Kiro — documentación de specs (`/docs/specs/`, Requirements-First, EARS, steering):
  `https://kiro.dev/docs/specs/` (consultado 2026-10-09).
- Comparativas de terceros (citadas, no reverificadas en su totalidad):
  `https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html`,
  `https://ainativesoftware.engineering/compare`,
  `https://github.com/cameronsjo/spec-compare`.

**Diferenciadores de este repo que el plan NO debe erosionar** (del contraste):

1. Trazabilidad **ejecutable** requisito→prueba (`sgp_check --stage pre-merge`).
2. **Ratchet** de pruebas (hook git) que ninguno de los comparados trae de fábrica.
3. **Presupuesto** (`apetito_dias`, `max_iteraciones_por_tarea`) como gates duros.
4. **Carriles** (`rapido`/`normal`/`mayor`) para ajustar la ceremonia al tamaño.
5. **Capa de comportamiento** separada (política v2 + protocolo) como skills del kit.
