---
id: CHG-002
titulo: Corregir precio_final con descuentos con decimales largos
carril: rapido
estado: hecho
apetito_dias: 1
inicio: 2026-09-25
requisitos: []
---

## Propuesta
**Problema:** `precio_final(2.675, 0)` da 2.67 en vez de 2.68. `round()` de Python usar redondeo banker\'s (al par mas cercano), no half-up como se acordo en la Fase 2 (QA de la spec).
**Resultado esperado:** el resultado siempre tiene como maximo 2 decimales reales, sin residuos de flotante.
**Alcance:** corregir la funcion existente.
**Fuera de alcance:** cambiar la spec (el comportamiento esperado ya esta en DESC-004, esto es un bug de implementacion).

## Criterios de finalizacion
- [x] Prueba de regresion en verde.
- [x] `sgp_check --stage pre-merge` sin errores.

## Tareas
- [x] T001 Corregir el residuo de flotante en precio_final
  Hecho cuando: la prueba de regresion pasa y DESC-004 sigue en verde.

## Progreso

## Notas
