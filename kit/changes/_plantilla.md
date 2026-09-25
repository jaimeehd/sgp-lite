---
id: CHG-000
titulo: <título corto en imperativo>
carril: normal            # rapido (<1 día, sin requisitos nuevos) | normal (1 dominio) | mayor (cruza dominios, arquitectura, contratos o dependencias nuevas)
estado: propuesta         # propuesta | aplicando | revision | hecho | cancelado
apetito_dias: 3           # tope de días de calendario; al agotarse: reformular o cancelar
inicio:                   # AAAA-MM-DD al pasar a "aplicando"
requisitos: []            # IDs de specs/ que este cambio añade o modifica, ej.: [EXP-001, EXP-002]
---

## Propuesta
**Problema:** <qué duele hoy y para quién>
**Resultado esperado:** <observable>
**Alcance:** <incluido>
**Fuera de alcance:** <no-gos>

## Diseño (obligatorio en carril "mayor"; opcional en "normal" si hay decisiones técnicas)
**Enfoque:** <solución elegida, en pocas líneas>
**Alternativa considerada:** <opción descartada y por qué>
**Contratos/datos afectados:** <APIs, esquemas, formatos persistidos; compatible o requiere versión mayor>
**ADR:** <ADR-NNNN si la decisión es estructural (afecta a >1 módulo, cara de revertir, descarta una alternativa razonable)>

## Criterios de finalización
- [ ] Todos los requisitos del cambio con prueba en verde (`sgp_check --stage pre-merge`).
- [ ] `specs/` refleja el comportamiento final.
- [ ] <criterio propio, p. ej. demo manual del flujo completo>

## Tareas
> Una tarea = una sesión de agente = un commit (20-30 min). `[x]` solo si los sensores pasan.

- [ ] T001 [DOM-001] <descripción>
  Hecho cuando: <condición verificable>
- [ ] T002 [DOM-002] <descripción>
  Hecho cuando: <condición verificable>

## Verificación manual (solo para lo que no se puede automatizar, p. ej. VB6/COM)
| Requisito | Pasos | Esperado | Resultado |
|---|---|---|---|

## Progreso
- (fecha) <qué se hizo, qué falló, iteraciones usadas, siguiente paso>

## Notas
- <ideas fuera de alcance, dudas [POR-ACLARAR]>
