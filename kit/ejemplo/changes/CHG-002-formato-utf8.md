---
id: CHG-002
titulo: Exportar el JSON en UTF-8 legible (no escapado)
carril: mayor
estado: hecho
apetito_dias: 2
inicio: 2026-09-17
requisitos: [EXP-001]
---

## Propuesta
**Problema:** el JSON exportado escapaba tildes y eñes (`\u00f1`), dificultando revisarlo a simple vista.
**Resultado esperado:** el archivo exportado usa caracteres UTF-8 directamente.
**Alcance:** cambiar la codificación de salida de `export_catalog`.
**Fuera de alcance:** cambiar el formato a otro distinto de JSON.

## Diseño
**Enfoque:** usar `ensure_ascii=False` en `json.dumps`.
**Alternativa considerada:** dejar `ensure_ascii=True` y transcodificar en el sitio web; descartada porque traslada el problema a otro repositorio sin necesidad.
**Contratos/datos afectados:** el archivo JSON exportado sigue siendo válido; cambia solo la codificación de los caracteres no ASCII (compatible: cualquier parser JSON acepta UTF-8).
**ADR:** ADR-0001

## Criterios de finalización
- [x] EXP-001 sigue en verde con el nuevo formato.
- [x] `specs/` no necesita cambios (el requisito no especificaba la codificación; se documenta en el ADR).
- [x] Se revisó a simple vista que el JSON de ejemplo ya no escapa tildes.

## Tareas
- [x] T001 [EXP-001] Cambiar a `ensure_ascii=False` y confirmar que EXP-001 sigue en verde
  Hecho cuando: la prueba EXP-001 pasa y un título con tilde aparece legible en el JSON.

## Progreso
- (2026-09-17) T001 hecha en 1 iteración. Cambio a revisión y luego a hecho.

## Notas
- Ninguna.
