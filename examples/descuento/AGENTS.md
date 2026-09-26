# AGENTS.md — descuento-librodemo

## Proyecto
Calculadora de precio final con descuento para LibroDemo, una libreria ficticia. Logica en `descuento/calculo.py`.

## Comandos
- Tests: `python -m unittest discover -s tests -t .`
- Verificar: `python tools/sgp_check.py --run`

## Skills disponibles
`python tools/sync_skills.py --agent <tu-agente>` instalar: sgp-especificar, sgp-qa-spec, sgp-planificar-cambio, sgp-ejecutar-tarea, sgp-validar-cerrar.

## Reglas
- Lee `docs/constitution.md`, `specs/` y el cambio activo en `changes/` antes de tocar codigo.
- Una tarea por sesion; al terminar, para. Pruebas primero; no borres pruebas.
- No modifiques `specs/` salvo peticion explicita.

## Al terminar cualquier tarea
- ejecutar `python tools/sgp_check.py --run`, muestra el resultado, marca la tarea `[x]` solo si pasa.
