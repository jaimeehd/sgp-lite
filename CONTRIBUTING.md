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
