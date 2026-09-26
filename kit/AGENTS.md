# AGENTS.md — <proyecto>

## Proyecto
<Que es, en 2 lineas.>

## Comandos
- Build: `<cmd>` · Tests: `<cmd>` · Lint: `<cmd>`
- Verificar: `python tools/sgp_check.py --run`

## Skills disponibles
Si el agente soporta el estandar Agent Skills (SKILL.md), instalalas una vez con `python tools/sync_skills.py --agent <tu-agente>`: `sgp-especificar`, `sgp-qa-spec`, `sgp-planificar-cambio`, `sgp-ejecutar-tarea`, `sgp-validar-cerrar`. Si no, usar los prompts equivalentes de `prompts.md`.

## Reglas
- Antes de tocar codigo lee `docs/constitution.md`, `specs/` y el cambio activo en `changes/`.
- Trabaja **una tarea por sesion**; al terminar, para. No empieces la siguiente.
- Pruebas primero. No borres ni edites pruebas existentes para hacer pasar el trabajo.
- No modifiques `specs/` salvo peticion explicita; si falta o es ambiguo un requisito, para y pregunta.
- Si superas `max_iteraciones_por_tarea` (`sgp.yaml`), detente y anota en el cambio que falta aclarar.
- Nada fuera del alcance del cambio: las ideas nuevas van a su seccion "Notas".

## Al terminar cualquier tarea
- ejecutar `python tools/sgp_check.py --run`, muestra el resultado, marca la tarea `[x]` solo si pasa y anota en "Progreso" que hiciste y que sigue.

## Convenciones
<Solo lo que no se deduce leyendo el codigo.>
