---
id: CHG-001
titulo: Calcular el precio final con descuento
carril: normal
estado: hecho
apetito_dias: 2
inicio: 2026-09-25
requisitos: [DESC-001, DESC-002, DESC-003, DESC-004, DESC-005]
---

## Propuesta
**Problema:** en caja se calculan descuentos a mano o con el celular y a veces se redondea mal.
**Resultado esperado:** una función confiable que calcule el precio final o rechace datos inválidos con un mensaje claro.
**Alcance:** función `precio_final(precio_lista, descuento_pct)` con validación y redondeo a 2 decimales.
**Fuera de alcance:** descuentos por volumen, interfaz gráfica, histórico.

## Criterios de finalización
- [x] Todos los requisitos del cambio con prueba en verde (`sgp_check --stage pre-merge`).
- [x] `specs/` refleja el comportamiento final (ya está escrita).
- [x] Demo manual: 3 casos (con descuento, sin descuento, descuento inválido) dan el resultado esperado.

## Tareas
- [x] T001 [DESC-001, DESC-004, DESC-005] Calcular precio final válido, redondeado a 2 decimales
  Hecho cuando: las pruebas DESC-001 y DESC-005 pasan.
- [x] T002 [DESC-002, DESC-003] Rechazar descuento o precio inválidos con mensaje claro
  Hecho cuando: las pruebas DESC-002 y DESC-003 pasan.

## Progreso
- (2026-09-25) T001 hecha en 3 iteraciones: 1) prueba en rojo (sin módulo), 2) implementación sin redondeo (falló DESC-001 y DESC-005), 3) se agregó round() y pasó. Cubre DESC-001, DESC-004, DESC-005.

- (2026-09-25) T002 hecha. Nota real: al pegar las pruebas nuevas quedaron por accidente dentro del bloque `if __name__`, `unittest discover` las ignoró silenciosamente (2 de 4). Se corrigió reordenando el archivo. Cambio a revisión.

## Notas
