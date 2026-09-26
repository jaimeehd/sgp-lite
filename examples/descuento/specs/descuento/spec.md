# Spec — descuento

## Contexto y objetivo
LibroDemo, una libreria ficticia aplica descuentos manuales en caja y a veces se equivoca redondeando. Se necesita una funcion que calcule el precio final de forma confiable, sin depender de la calculadora del celular.

## Requisitos
- **DESC-001** CUANDO se calcula el precio final con un precio de lista y un porcentaje de descuento entre 0 y 100, EL SISTEMA devolvera el precio final redondeado a 2 decimales (salida 0).
- **DESC-002** SI el porcentaje de descuento es menor que 0 o mayor que 100, ENTONCES EL SISTEMA rechazara el calculo con un error que indique el valor recibido (salida 1).
- **DESC-003** SI el precio de lista es negativo, ENTONCES EL SISTEMA rechazara el calculo con un error que lo indique (salida 1).
- **DESC-004** EL SISTEMA nunca devolvera un precio final negativo ni con mas de 2 decimales.
- **DESC-005** MIENTRAS el descuento sea 0, EL SISTEMA devolvera el precio de lista sin modificar (salvo redondeo a 2 decimales).

## No funcionales
- Los mensajes de error estan en español, dirigidos a quien atiende la caja (no jerga tecnica).

## Casos limite
- Descuento del 100 % → precio final 0.00 → DESC-001
- Precio de lista con mas de 2 decimales (ej. 19.999) → DESC-001 (se redondea)

## Fuera de alcance
- Aplicar descuentos por volumen o combos.
- Guardar el historico de descuentos aplicados.

## Dudas abiertas
(ninguna: resueltas en la entrevista)
