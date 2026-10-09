# Seguridad

## Reportar una vulnerabilidad

Abre un **borrador de aviso de seguridad** en la pestaña *Security* del repositorio
("Report a vulnerability"). No abras un issue público para un problema de seguridad.

## Frontera de confianza (importante)

Este kit ejecuta comandos que declares en `sgp.yaml` usando `shell=True`
(`kit/tools/sgp_check.py`), y el hook `kit/tools/pre-commit` ejecuta el verificador y el ratchet.
Consecuencias:

- No instales ni ejecutes el kit sobre un repositorio cuyo `sgp.yaml` o `tools/` no hayas revisado.
- El kit asume que el repositorio donde vive es de confianza; no es un sandbox.
- No incluyas secretos en `sgp.yaml`, `specs/`, `changes/` ni en la salida de los sensores.
