# AGENTS.md — sgp-lite

## Proyecto
SGP Lite: metodología spec-driven para trabajar con agentes de IA, más la política de ingeniería
(`docs/system-engineering-policy.SKILL.md`) y su protocolo. El kit se distribuye desde `kit/`
(incluye `sgp-lite.zip`); hay un ejemplo ejecutable en `examples/descuento/`.

## Comandos
- Tests del kit: `cd kit && python -m unittest discover -s tools -p "test_*.py" -v`
- Verificar el ejemplo: `python kit/tools/sgp_check.py --root examples/descuento --run`
- Regenerar el zip: `python kit/tools/sgp_zip.py --source kit --dest sgp-lite.zip`

## Reglas
- **Nada de secretos ni datos personales** en el repositorio: tokens, claves, `.env`, rutas con el
  usuario del sistema, nombres reales, correos o logs que los contengan. Si aparece algo así, se
  reporta y se elimina antes de confirmar el cambio.
- **Nada de logs** versionados (`*.log`). Si un log es evidencia necesaria, se sanitiza y se incluye
  como fragmento en el documento correspondiente, nunca el archivo crudo.
- Las pruebas no se borran ni se debilitan para hacer pasar un trabajo.
- Si se modifican archivos del kit cubiertos por `sgp-kit.manifest`, se debe regenerar
  `sgp-lite.zip`: la guarda `kit/tools/test_kit_consistency.py` lo exige.
- Los tools son solo-stdlib (Python 3.8+): no se agregan dependencias.
- Un cambio equivale a un alcance declarado; lo demás se reporta, no se mezcla.

## Idioma y convenciones
- La documentación se escribe en **español neutro**: sin voseo ni regionalismos.
- El código (nombres, identificadores y comentarios técnicos) puede escribirse en inglés.

## Política de comportamiento
Este repositorio sigue `docs/system-engineering-policy.SKILL.md` (norma) y
`docs/protocolo-ingenieria-senior.SKILL.md` (procedimiento).

## Al terminar cualquier tarea
- Se ejecutan los tests del kit y el verificador del ejemplo, y se muestra la salida real antes de
  dar algo por terminado.
