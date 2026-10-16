# AGENTS.md — <proyecto>

## Proyecto
<Qué es, en 2 líneas.>

## Comandos
- Build: `<cmd>` · Tests: `<cmd>` · Lint: `<cmd>`
- Verificar: `python tools/sgp_check.py --run`

## Skills disponibles
Si tu agente soporta el estándar Agent Skills (SKILL.md), instálalas con `python tools/sync_skills.py --agent <tu-agente>`: las 6 de proceso (`sgp-documento-requerimientos`, `sgp-especificar`, `sgp-qa-spec`, `sgp-planificar-cambio`, `sgp-ejecutar-tarea`, `sgp-validar-cerrar`) y las 2 de comportamiento (`system-engineering-policy` y `protocolo-ingenieria-senior`). Se puede reejecutar cuando el kit se actualice: refresca solas las skills intactas y conserva las editadas a mano (`--force` las reemplaza). Si tu agente no soporta SKILL.md, usa los prompts equivalentes de `prompts.md` (las 2 de comportamiento no tienen prompt).

## Reglas
- La política de ingeniería vive en la configuración global del equipo. Si esa política global no es la que este proyecto requiere, no está completa o estas copias son mejores, rigen las reglas y copias de este proyecto (citándolas); la global no se impone. Excepción única: la seguridad nunca se relaja. Cada capa mantiene su copia del protocolo y su referencia es su propia política (separación global ↔ proyecto, decisión 2026-10-16).
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
