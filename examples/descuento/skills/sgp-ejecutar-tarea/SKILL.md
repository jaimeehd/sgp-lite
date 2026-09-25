---
name: sgp-ejecutar-tarea
description: Implementa UNA tarea de un cambio SGP (tests primero, una tarea por sesión) y para al terminar. Úsala cuando el usuario diga "implementa la tarea T00N", "sigue con la siguiente tarea" o durante la ejecución de un changes/CHG-*.md ya planificado.
---

# Ejecutar una tarea — SGP

Contexto mínimo: `AGENTS.md`, el cambio activo (`changes/CHG-NNN-*.md`), la spec de los requisitos citados por la tarea y los archivos que toca.

## Pasos
1. Localiza la tarea `TNNN` indicada (o la primera `[ ]` si no se indica ninguna).
2. Escribe primero la prueba — su nombre incluye el ID del requisito con guion bajo, p. ej. `test_EXP_001_...` — y confirma que falla.
3. Implementa lo mínimo para que pase.
4. Ejecuta `python tools/sgp_check.py --run` y muestra el resultado completo.
5. Si falla: corrige y repite (tope: `max_iteraciones_por_tarea` en `sgp.yaml`). Si lo agotas, detente y anota en «Progreso» qué debe aclararse.
6. Si pasa: marca la tarea `[x]`, indica qué requisitos cubre, actualiza «Progreso» (hecho, siguiente paso) y **párate**. No empieces la siguiente tarea en esta misma sesión.

## No hacer
- No borres ni edites pruebas existentes para hacer pasar el trabajo.
- No amplíes el alcance de la tarea; ideas nuevas van a «Notas».
- No sigas con otra tarea tras terminar esta.
