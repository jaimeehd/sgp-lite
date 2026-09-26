---
id: CHG-001
titulo: Exportar el catalogo a JSON
carril: normal
estado: revision
apetito_dias: 3
inicio: 2026-09-14
requisitos: [EXP-001, EXP-002, EXP-003, EXP-004]
---

## Propuesta
**Problema:** publicar el catalogo requiere copiar datos a mano (unos 40 min, con errores).
**Resultado esperado:** un JSON del catalogo completo y valido, o un error que nombra el registro incorrecto.
**Alcance:** exportar libros activos con validacion de campos obligatorios.
**Fuera de alcance:** sincronizacion, imagenes, otros formatos.

## Criterios de finalizacion
- [x] Todos los requisitos del cambio con prueba en verde (`sgp_check --stage pre-merge`).
- [x] `specs/` refleja el comportamiento final.
- [x] Demo manual: exportar un catalogo de ejemplo.

## Tareas
- [x] T001 [EXP-001, EXP-004] Exportar libros activos excluyendo retirados
  Hecho cuando: las pruebas EXP-001 y EXP-004 pasan.
- [x] T002 [EXP-002] Validar titulo y nombrar el libro en el error
  Hecho cuando: la prueba EXP-002 pasa.
- [x] T003 [EXP-003] Catalogo vacio con mensaje de conteo
  Hecho cuando: la prueba EXP-003 pasa.

## Progreso
- (2026-09-14) T001 hecha.
- (2026-09-15) T002 hecha en 2 iteraciones: el primer error no incluia el identificador del libro.
- (2026-09-16) T003 hecha. Cambio a revision.

## Notas
- Idea fuera de alcance: exportar tambien CSV.
