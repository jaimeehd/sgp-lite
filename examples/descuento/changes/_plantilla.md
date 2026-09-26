---
id: CHG-000
titulo: <titulo corto en imperativo>
carril: normal            # rapido (<1 dia, sin requisitos nuevos) | normal (1 dominio) | mayor (cruza dominios, arquitectura, contratos o dependencias nuevas)
estado: propuesta         # propuesta | aplicando | revision | hecho | cancelado
apetito_dias: 3           # tope de dias de calendario; al agotarse: reformular o cancelar
inicio:                   # AAAA-MM-DD al pasar a "aplicando"
requisitos: []            # IDs de specs/ que este cambio añade o modifica, ej.: [EXP-001, EXP-002]
---

## Propuesta
**Problema:** <que duele hoy y para quien>
**Resultado esperado:** <observable>
**Alcance:** <incluido>
**Fuera de alcance:** <no-gos>

## Diseño (obligatorio en carril "mayor"; opcional en "normal" si hay decisiones tecnicas)
**Enfoque:** <solucion elegida, en pocas lineas>
**Alternativa considerada:** <opcion descartada y por que>
**Contratos/datos afectados:** <APIs, esquemas, formatos persistidos; compatible o requiere version mayor>
**ADR:** <ADR-NNNN si la decision es estructural (afecta a >1 modulo, cara de revertir, descarta una alternativa razonable)>

## Criterios de finalizacion
- [ ] Todos los requisitos del cambio con prueba en verde (`sgp_check --stage pre-merge`).
- [ ] `specs/` refleja el comportamiento final.
- [ ] <criterio propio, p. ej. demo manual del flujo completo>

## Tareas
> Una tarea = una sesion de agente = un commit (20-30 min). `[x]` solo si los sensores pasan.

- [ ] T001 [DOM-001] <descripcion>
  Hecho cuando: <condicion verificable>
- [ ] T002 [DOM-002] <descripcion>
  Hecho cuando: <condicion verificable>

## Verificacion manual (solo para lo que no se puede automatizar, p. ej. VB6/COM)
| Requisito | Pasos | Esperado | Resultado |
|---|---|---|---|

## Progreso
- (fecha) <que se hizo, que fallo, iteraciones usadas, siguiente paso>

## Notas
- <ideas fuera de alcance, dudas [POR-ACLARAR]>
