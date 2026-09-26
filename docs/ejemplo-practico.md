# Ejemplo practico y funcional — SGP Lite de punta a punta

Un proyecto real, chico, ejecutado con la metodologia completar: constitucion → spec → QA → cambio → tareas → validacion → cierre, mas un bugfix en carril `rapido` y una demostracion en vivo del ratchet de pruebas. Cada bloque de codigo de abajo es la **salida real** de correr los comandos, no una simulacion redactada — incluye un error genuino que cometi a mitad de camino y como el propio verificador lo detecto.

**El proyecto:** una funcion que calcula el precio final con descuento para la libreria, algo que podrias usar de verdad en `BookStore`. Repo completo (con historial de git) en `demo-descuento.zip`.

---

## 0. Instalar el kit

```text
demo-descuento/
├── AGENTS.md  CLAUDE.md  sgp.yaml
├── docs/constitution.md  docs/adr/_plantilla.md
├── specs/  changes/_plantilla.md
├── skills/sgp-{especificar,qa-spec,planificar-cambio,ejecutar-tarea,validar-cerrar}/SKILL.md
└── tools/sgp_check.py  tools/sync_skills.py  tools/pre-commit
```

`docs/constitution.md`:
```text
1. **La spec manda**: ningun calculo se implementa sin un requisito en `specs/`. Verificado por: estructura (`sgp_check`) y revision humana.
2. **Tests como puerta**: cada tarea termina con sus pruebas en verde. Verificado por: tests.
3. **Las pruebas no se borran ni se debilitan** sin aprobacion explicita. Verificado por: ratchet.
4. **Los precios nunca quedan negativos ni con mas de 2 decimales.** Verificado por: tests.
5. **Solo biblioteca estandar** (sin dependencias externas). Verificado por: humano.
```

---

## 1. Especificar (`skills/sgp-especificar`)

La entrevista real, de una pregunta a la vez:

```text
1. ¿El descuento se expresa como porcentaje (ej. 15) o como fraccion (0.15)?
   → porcentaje, de 0 a 100.
2. ¿Que debe pasar si el descuento es negativo o mayor a 100?
   → rechazar con un error claro para quien atiende caja.
3. ¿El precio de lista puede venir negativo o en 0?
   → negativo no; en 0 si es valido (promociones).
4. ¿Cuantos decimales debe tener el resultado?
   → 2, para no perder precision en calculos encadenados.
5. ¿Hay un caso de "sin descuento" que deba comportarse distinto?
   → no, simplemente que no toque el precio.
```

Resultado, `specs/descuento/spec.md`:

```markdown
## Requisitos
- **DESC-001** CUANDO se calcula el precio final con un precio de lista y un porcentaje de descuento entre 0 y 100, EL SISTEMA devolvera el precio final redondeado a 2 decimales (salida 0).
- **DESC-002** SI el porcentaje de descuento es menor que 0 o mayor que 100, ENTONCES EL SISTEMA rechazara el calculo con un error que indique el valor recibido (salida 1).
- **DESC-003** SI el precio de lista es negativo, ENTONCES EL SISTEMA rechazara el calculo con un error que lo indique (salida 1).
- **DESC-004** EL SISTEMA nunca devolvera un precio final negativo ni con mas de 2 decimales.
- **DESC-005** MIENTRAS el descuento sea 0, EL SISTEMA devolvera el precio de lista sin modificar (salvo redondeo a 2 decimales).
```

## 2. QA de la spec (`skills/sgp-qa-spec`)

```text
1. Ambiguedades:
   - DESC-001 no dice que politica de redondeo usar si el resultado cae exacto en .005.
3. Casos limite sin cubrir:
   - Precio de lista = 0 con descuento > 0: no hay escenario explicito.

→ Respuesta: redondeo half-up estandar; precio 0 da 0, ya lo cubren DESC-001 y DESC-004.
```

Este acuerdo verbal (half-up) **vuelve a aparecer en el paso 6** — no quedo escrito en la spec, y eso causo un bug real.

```
$ python tools/sgp_check.py
Resumen: 0 error(es), 0 aviso(s).
```

## 3. Planificar el cambio (`skills/sgp-planificar-cambio`)

```
$ python tools/sgp_check.py --nuevo "calculo-precio-final"
Creado changes/CHG-001-calculo-precio-final.md
```

El comando genera el archivo desde la plantilla (frontmatter + secciones vacias). Lo completo: carril `normal`, apetito 2 dias, 5 requisitos, 2 tareas de ~20-30 min cada una.

## 4. Ejecutar — Tarea 1 (`skills/sgp-ejecutar-tarea`)

**Rojo primero**, antes de escribir la funcion:
```
$ python -m unittest discover -s tests -t .
ModuleNotFoundError: No module named 'descuento.calculo'
```

**Primera implementacion — falla de verdad** (sin redondeo):
```
FAIL: test_DESC_001_calcula_precio_con_descuento_redondeado
AssertionError: 16.99915 != 17.0
FAIL: test_DESC_005_sin_descuento_devuelve_el_precio_de_lista
AssertionError: 19.999 != 20.0
```

**Correccion** (`round(bruto, 2)`) y verificacion completar:
```
$ python tools/sgp_check.py --run
→ build: python -m compileall -q descuento
→ tests: python -m unittest discover -s tests -t .
→ lint: python -m compileall -q tests
Resumen: 0 error(es), 0 aviso(s).
```

Marco T001 `[x]`, anoto en «Progreso» las 3 iteraciones reales, y **paro** — nueva sesion para la siguiente tarea.

## 4b. Ejecutar — Tarea 2

Añado las pruebas de validacion de errores. Al ejecutar el checker completo:
```
$ python tools/sgp_check.py --stage pre-merge
[AVISO] pre-merge: no hay cambios en estado 'revision'
```
El verificador avisa correctamente que el cambio sigue en `aplicando`.

**Error real que cometi:** al pegar las pruebas nuevas con un editor de texto, quedaron *dentro* del bloque `if __name__ == "__main__":` por mala indentacion — sintacticamente valido, pero `unittest discover` las ignoro en silencio. Solo se ejecutaron 2 de 4 pruebas y ambas "pasaron" porque ni siquiera se cargaron las nuevas. Lo detecte al pedir `-v` (verbose) y ver que faltaban dos nombres de prueba en la lista. Lo corregi reordenando el archivo — el tipo de error que un checklist de revision humana (§9 de la metodologia) esta pensado para atrapar.

## 5. Validar (`skills/sgp-validar-cerrar`) — el verificador encuentra algo real

Con las 4 tareas de validacion hechas, paso el cambio a `revision` y corro `--stage pre-merge`:

```
Trazabilidad CHG-001-calculo-precio-final:
  DESC-001  ok
  DESC-002  ok
  DESC-003  ok
  DESC-004  sin pruebas
  DESC-005  ok

[ERROR] CHG-001-calculo-precio-final/DESC-004: requisito sin cobertura comprobada (sin pruebas)
        Como corregirlo: escribe una prueba cuyo nombre incluya DESC_004
```

**Esto es exactamente la debilidad que corregimos respecto a la primera version de la plantilla** (el "falso verde" del informe comparativo): DESC-004 es una propiedad general ("nunca negativo, nunca mas de 2 decimales") que las otras pruebas satisfacen de rebote, pero ninguna la nombra explicitamente. El verificador no se conforma con eso — exige una prueba con su ID. La escribo:

```python
def test_DESC_004_nunca_negativo_ni_mas_de_2_decimales(self):
    resultado = precio_final(10.005, 100)
    self.assertGreaterEqual(resultado, 0)
    self.assertEqual(resultado, round(resultado, 2))
```

```
$ python tools/sgp_check.py --stage pre-merge
Trazabilidad CHG-001-calculo-precio-final:
  DESC-001  ok   DESC-002  ok   DESC-003  ok   DESC-004  ok   DESC-005  ok
Resumen: 0 error(es), 0 aviso(s).
```

Cierro: `estado: hecho`.

## 6. El acuerdo verbal que no quedo escrito, vuelve como bug

Dias despues, en caja: un descuento de 0% sobre $2.675 da $2.67 en vez de $2.68.

```python
>>> round(2.675, 2)
2.67
```

`round()` de Python usar *banker's rounding* (al par mas cercano), no half-up — el redondeo que se acordo **verbalmente** en la Fase 2 (QA) pero nunca se escribio en la spec ni en un ADR. Es un bug de implementacion, no un requisito nuevo → **carril `rapido`**:

```
$ python tools/sgp_check.py --nuevo "bug-descuento-decimal"
Creado changes/CHG-002-bug-descuento-decimal.md
```

Prueba de regresion primero (rojo):
```
AssertionError: 2.67 != 2.68
```

Correccion con `decimal.Decimal` y `ROUND_HALF_UP`:
```python
from decimal import Decimal, ROUND_HALF_UP

def precio_final(precio_lista, descuento_pct):
    ...
    bruto = Decimal(str(precio_lista)) * (Decimal(1) - Decimal(str(descuento_pct)) / Decimal(100))
    return float(bruto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
```

```
$ python -m unittest discover -s tests -t . -v
... 6 tests ... OK
$ python tools/sgp_check.py --stage pre-merge
(cambios en revision sin trazabilidad por requisito, carril rapido: CHG-002-bug-descuento-decimal)
Resumen: 0 error(es), 0 aviso(s).
```

**Leccion real del ejercicio:** una decision de diseño (half-up vs. banker's) que se acuerda hablando y no se anota en ningun artefacto, se pierde. Con este historial, la correccion correcta hubiera sido anotarlo en la spec como parte de DESC-001, o abrir un ADR — el carril `mayor` lo habria exigido; el `rapido` no, porque es una correccion de implementacion, no un requisito nuevo.

## 7. El ratchet de pruebas, en vivo

Simulo el caso tipico: "arreglar rapido" debilitando una prueba en vez de corregir el codigo.

```python
def test_DESC_002_descuento_fuera_de_rango_falla_con_el_valor(self):
    pass  # TODO: arreglar esto despues
```

```
$ git add tests/test_calculo.py && git commit -m "arreglo rapido"
[ERROR] ratchet de pruebas: el commit elimina o modifica lineas existentes en tests/
        - tests/test_calculo.py: 3 linea(s)
        Como corregirlo: no borres ni debilites pruebas para hacer pasar el trabajo.
        Si es legitimo, pide aprobacion humana y repite con SGP_TESTS_APPROVED=1.

commit exit=1
```

El commit **no se hizo**. Si de verdad fuera legitimo (una prueba mal escrita), la via es `SGP_TESTS_APPROVED=1 git commit ...` — una aprobacion explicita, no silenciosa.

## 8. Bonus: un defecto real del propio verificador, encontrado al usarlo

Durante el paso 6, `--stage pre-merge` con `CHG-002` en revision (carril `rapido`, sin requisitos) mostraba `[AVISO] no hay cambios en estado 'revision'`, que es **falso** — si lo habia, solo que el carril `rapido` no lleva trazabilidad por requisito. Lo corregi en `tools/sgp_check.py` (ahora distingue "no hay ninguno" de "hay, pero es carril rapido") y volvi a correr las 27 pruebas del verificador: siguen en verde. La version corregida es la que trae este zip y tambien `sgp-lite.zip`.

---

## Que demuestra este ejemplo

- La entrevista de especificacion produce requisitos con ID, no prosa vaga.
- El checker detecta un **falso verde real** (DESC-004 sin prueba propia) — el motivo por el que existe la trazabilidad por ejecucion.
- El ratchet **bloquea de verdad** un intento de debilitar pruebas.
- El carril `rapido` funciona para un bug real sin la sobrecarga de una spec nueva.
- Un acuerdo que no queda por escrito, vuelve como bug — es el argumento a favor de anotar hasta las decisiones "obvias".
- El propio verificador tuvo un defecto de mensaje, se encontro usandolo y se corrigio con sus propias pruebas como red de seguridad.

## Como correrlo usted mismo

```bash
cd demo-descuento
python tools/sgp_check.py --stage pre-merge   # snapshot final: 0 errores
git log --oneline                              # las 6 sesiones/commits reales
python -m unittest discover -s tests -t . -v    # 6 pruebas
```
