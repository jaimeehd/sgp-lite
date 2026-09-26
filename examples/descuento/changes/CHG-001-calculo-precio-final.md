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
**Resultado esperado:** una funcion confiable que calcule el precio final o rechace datos invalidos con un mensaje claro.
**Alcance:** funcion `precio_final(precio_lista, descuento_pct)` con validacion y redondeo a 2 decimales.
**Fuera de alcance:** descuentos por volumen, interfaz grafica, historico.

## Criterios de finalizacion
- [x] Todos los requisitos del cambio con prueba en verde (`sgp_check --stage pre-merge`).
- [x] `specs/` refleja el comportamiento final (ya esta escrita).
- [x] Demo manual: 3 casos (con descuento, sin descuento, descuento invalido) dan el resultado esperado.

## Tareas
- [x] T001 [DESC-001, DESC-004, DESC-005] Calcular precio final valido, redondeado a 2 decimales
  Hecho cuando: las pruebas DESC-001 y DESC-005 pasan.
- [x] T002 [DESC-002, DESC-003] Rechazar descuento o precio invalidos con mensaje claro
  Hecho cuando: las pruebas DESC-002 y DESC-003 pasan.

## Progreso
- (2026-09-25) T001 hecha en 3 iteraciones: 1) prueba en rojo (sin modulo), 2) implementacion sin redondeo (fallo DESC-001 y DESC-005), 3) se agrego round() y paso. Cubre DESC-001, DESC-004, DESC-005.

- (2026-09-25) T002 hecha. Nota real: al pegar las pruebas nuevas quedaron por accidente dentro del bloque `if __name__`, `unittest discover` las ignoro silenciosamente (2 de 4). Se corrigio reordenando el archivo. Cambio a revision.

## Notas
