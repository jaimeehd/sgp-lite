# SGP Lite — Spec-Driven con IA en una pagina

**Idea:** tu decides el *que* y el *por que* (la spec); el agente propone el *como* y ejecutar; un verificador comprueba. Tres aprobaciones tuyas: **la spec, el plan/tareas y el merge**.

## Que hay en el repositorio

| Archivo | Para que |
|---|---|
| `docs/constitution.md` | 4-6 principios innegociables (≤15 lineas); cada uno dice *como se verifica* |
| `AGENTS.md` (+ `CLAUDE.md` = `@AGENTS.md`) | Comandos y reglas para el agente (≤30 lineas) |
| `specs/<dominio>/spec.md` | El comportamiento **vigente**: requisitos EARS con ID (`EXP-001`) |
| `changes/CHG-NNN-nombre.md` | **Un archivo por cambio**: propuesta, criterios de finalizacion, tareas, progreso |
| `sgp.yaml` | Comandos de build/tests/lint y como ejecutar las pruebas de un requisito |
| `tools/sgp_check.py`, `tools/pre-commit` | Verificador y hook (ratchet de pruebas) |
| `prompts.md` | 5 prompts, uno por fase (para agentes sin soporte de skills) |
| `skills/*/SKILL.md` | Las mismas 5 fases como Agent Skills (estandar agentskills.io); `tools/sync_skills.py` las instalar en el agente |

## Flujo

| # | Fase | Skill / prompt | Tu apruebas | Sensor |
|---|---|---|---|---|
| 1 | **Especificar**: entrevista de una pregunta a la vez; el agente editar `specs/` y te muestra el diff. Sin codigo. | `sgp-especificar` / prompt 1 | **La spec** | Formato EARS, IDs unicos |
| 2 | **QA de la spec**: ambiguedades, contradicciones, casos limite, conflictos con la constitucion | `sgp-qa-spec` / prompt 2 | — | Sin `[POR-ACLARAR]` |
| 3 | **Cambio**: `--nuevo nombre` crear el archivo; elige carril, plan breve y tareas (20-30 min, cada una con «Hecho cuando:») | `sgp-planificar-cambio` / prompt 3 | **Plan y tareas** | Requisitos existen en `specs/`; cada uno cubierto por una tarea; carril `mayor` exige diseño |
| 4 | **Ejecutar**: una tarea por sesion, pruebas primero; para al terminar | `sgp-ejecutar-tarea` / prompt 4 | — | build, tests, lint, ratchet |
| 5 | **Validar**: requisito por requisito, que prueba lo cubre y su resultado | `sgp-validar-cerrar` / prompt 5 | **El merge** | `--stage pre-merge` (ejecutar las pruebas de cada requisito) |
| 6 | **Cerrar**: `estado: hecho`; `specs/` ya refleja la realidad | — | — | — |

**Cambio posterior a algo existente:** primero la spec (fase 1, con diff), luego un cambio nuevo. Nunca codigo antes de spec.

## Tres carriles (elige el mas chico que aun sea honesto)

| Carril | Cuando | Exige |
|---|---|---|
| **rapido** | Bug o spike de <1 dia, sin requisitos nuevos | Una tarea con «Hecho cuando:» y una prueba de regresion |
| **normal** | Toca un solo dominio de `specs/`, sin decisiones de arquitectura | Requisitos + tareas (por defecto) |
| **mayor** | Cruza dominios, cambia un contrato/API, o añade una dependencia | Ademas, seccion `## Diseño` con una alternativa descartada; si la decision es estructural, un ADR |

Si dudas entre dos, elige el menor y **sube si aparece incertidumbre real** (una decision no trivial, un contrato afectado); el verificador avisa (no bloquea) si un cambio `normal` toca mas de un dominio, por si en realidad es `mayor`. Subir de carril nunca cuenta como fallo.

## Escribir requisitos (EARS en español)

Un requisito por linea: `- **DOM-001** <patron>`.

- **CUANDO** <evento>, EL SISTEMA <respuesta> — comportamiento normal.
- **SI** <condicion no deseada>, **ENTONCES** EL SISTEMA <respuesta> — errores y casos limite.
- **MIENTRAS** <estado>, EL SISTEMA <respuesta> — comportamiento dependiente de un estado.
- **DONDE** <caracteristica opcional>, EL SISTEMA <respuesta>.
- EL SISTEMA <propiedad> — lo que siempre se cumple.

Reglas: la respuesta es **observable** (mensaje, codigo de salida, estado); el *que*, no el *como* (la tecnologia va en el plan); nada de «rapido», «intuitivo», «adecuado» sin cifra; los errores y casos limite son requisitos de primera clase.

## Escalera de «hecho»

- **Tarea:** su linea «Hecho cuando:» se cumple y los sensores pasan.
- **Cambio:** sus «Criterios de finalizacion» estan marcados y `sgp_check --stage pre-merge` no da errores.
- **Spec:** cada requisito tiene una prueba que lo ejercita (o una fila `OK` en «Verificacion manual»).

## Reglas del arnes

1. Los sensores se enganchan por **hooks** (git y, si el agente lo permite, del agente), no por prompt.
2. **Un sensor sin comprobacion real es un error**: comandos vacios en `sgp.yaml` fallan en pre-merge.
3. **Las pruebas no se borran ni se debilitan** para hacer pasar el trabajo (ratchet: `SGP_TESTS_APPROVED=1` solo con tu aprobacion).
4. **Presupuesto:** `apetito_dias` por cambio y `max_iteraciones_por_tarea`. Al agotarse se detiene: **reformular o cancelar, nunca extender**.

## Convencion de pruebas (trazabilidad real)

El nombre de la prueba incluye el ID del requisito con guion bajo (`test_EXP_001_...`). `sgp.yaml → test_por_requisito` ejecutar solo esas pruebas; si no encuentra ninguna, el requisito cuenta como **sin cobertura** (un comentario con el ID no basta). Lo que no se automatiza (VB6/COM, hardware) va en la tabla «Verificacion manual» del cambio con `OK` por requisito.

## Si necesitas mas (sube de nivel solo cuando duela)

- **Decisiones estructurales:** `docs/adr/_plantilla.md`.
- **Varios cambios en paralelo:** un `git worktree` y una rama por cambio.
- **Metricas DORA, limite de revisiones, deltas por dominio, portafolio:** estan en el kit completo anterior (`sgp-template`). No los actives hasta necesitarlos.

## Limites

El verificador comprueba estructura, trazabilidad, presupuesto y ejecucion; **no juzga la calidad de la spec ni de las pruebas** (una prueba trivial con el nombre correcto pasa). Eso sigue siendo tu revision. La evidencia sobre SDD es joven: ajusta esta practica con tus propios repositorios.
