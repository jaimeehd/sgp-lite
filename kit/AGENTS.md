# AGENTS.md — <proyecto>

## Proyecto
<Qué es, en 2 líneas.>

## Comandos
- Build: `<cmd>` · Tests: `<cmd>` · Lint: `<cmd>`
- Verificar: `python tools/sgp_check.py --run`

## Skills disponibles
Si tu agente soporta el estándar Agent Skills (SKILL.md), instálalas una vez con `python tools/sync_skills.py --agent <tu-agente>`: `sgp-especificar`, `sgp-qa-spec`, `sgp-planificar-cambio`, `sgp-ejecutar-tarea`, `sgp-validar-cerrar`. Si no, usa los prompts equivalentes de `prompts.md`.

## Reglas
- Antes de tocar código lee `docs/constitution.md`, `specs/` y el cambio activo en `changes/`.
- Trabaja **una tarea por sesión**; al terminar, para. No empieces la siguiente.
- Pruebas primero. No borres ni edites pruebas existentes para hacer pasar el trabajo.
- No modifiques `specs/` salvo petición explícita; si falta o es ambiguo un requisito, para y pregunta.
- Si superas `max_iteraciones_por_tarea` (`sgp.yaml`), detente y anota en el cambio qué falta aclarar.
- Nada fuera del alcance del cambio: las ideas nuevas van a su sección "Notas".

## Al terminar cualquier tarea
- Ejecuta `python tools/sgp_check.py --run`, muestra el resultado, marca la tarea `[x]` solo si pasa y anota en "Progreso" qué hiciste y qué sigue.

## Convenciones
<Solo lo que no se deduce leyendo el código.>
