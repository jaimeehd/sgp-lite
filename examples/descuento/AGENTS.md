# AGENTS.md — descuento-librodemo

## Proyecto
Calculadora de precio final con descuento para LibroDemo, una librería ficticia. Lógica en `descuento/calculo.py`.

## Comandos
- Tests: `python -m unittest discover -s tests -t .`
- Verificar: `python tools/sgp_check.py --run`

## Skills disponibles
Si tu agente soporta el estándar Agent Skills (SKILL.md), instálalas con `python tools/sync_skills.py --agent <tu-agente>`: las 6 de proceso (`sgp-documento-requerimientos`, `sgp-especificar`, `sgp-qa-spec`, `sgp-planificar-cambio`, `sgp-ejecutar-tarea`, `sgp-validar-cerrar`) y las 2 de comportamiento (`system-engineering-policy` y `protocolo-ingenieria-senior`). Se puede reejecutar cuando el kit se actualice: refresca solas las skills intactas y conserva las editadas a mano (`--force` las reemplaza). Si tu agente no soporta SKILL.md, usa los prompts equivalentes de `prompts.md` (las 2 de comportamiento no tienen prompt).

## Reglas
- Si la política global del equipo no es la que este proyecto requiere, no está completa o estas copias son mejores, rigen estas copias del proyecto (citadas); la global no se impone. Excepción única: la seguridad nunca se relaja (decisión 2026-10-16).
- Lee `docs/constitution.md`, `specs/` y el cambio activo en `changes/` antes de tocar código.
- Una tarea por sesión; al terminar, para. Pruebas primero; no borres pruebas.
- No modifiques `specs/` salvo petición explícita.

## Al terminar cualquier tarea
- Ejecuta `python tools/sgp_check.py --run`, muestra el resultado, marca la tarea `[x]` solo si pasa.
