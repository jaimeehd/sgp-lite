# Spec — <dominio>

> Comportamiento VIGENTE del dominio. Se edita primero la spec y luego el código (con diff revisado por ti).
> Un requisito por línea: `- **DOM-NNN** <patrón EARS>`. Prefijo = 2-5 letras mayúsculas del dominio.
> Cada requisito indica **cómo se comprueba** (mensaje, salida, estado): si no podés decir cómo verificarlo, no es un requisito.
> Un **supuesto** no es un requisito: lo asumido va en «Supuestos», marcado `[POR-ACLARAR]`.
> Ante conflicto entre requisitos, precedencia: seguridad > restricción de proyecto > pedido > compatibilidad > corrección > mantenibilidad.

## Contexto y objetivo
<Por qué existe esto y qué resultado se espera. Sin tecnología.>

## Requisitos
- **DOM-001** CUANDO <evento>, EL SISTEMA <respuesta observable> (salida 0).
- **DOM-002** SI <condición no deseada>, ENTONCES EL SISTEMA <respuesta y mensaje de error> (salida 1).
- **DOM-003** MIENTRAS <estado>, EL SISTEMA <comportamiento>.
- **DOM-004** EL SISTEMA <propiedad que siempre se cumple>.

## No funcionales
- <Medibles: tiempo, plataformas, idioma de mensajes.>

## Casos límite (→ requisito que los cubre)
- <caso> → DOM-00N

## Fuera de alcance
- <lo que NO se hará>

## Supuestos
- [POR-ACLARAR] <algo asumido, a la espera de confirmación> → <requisito afectado>

## Dudas abiertas
- [POR-ACLARAR] <pregunta> (elimínala al resolverla)
