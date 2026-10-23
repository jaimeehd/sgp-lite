---
name: sgp-validar-cerrar
description: Valida un cambio SGP requisito por requisito (qué prueba lo cubre y su resultado) antes del merge, y prepara el cierre. Úsala cuando el usuario diga "valida este cambio", "prepáralo para revisión" o cuando todas las tareas de un changes/CHG-*.md estén marcadas.
---

# Validar y cerrar — SGP

Contexto: el cambio, `specs/` y el resultado de `python tools/sgp_check.py --stage pre-merge`.

## Pasos
1. Ejecuta `python tools/sgp_check.py --stage pre-merge` y recoge la tabla de trazabilidad.
2. Ejecuta `python tools/sgp_docs.py` y exige la tabla de docs actualizada: solo documentos VIGENTES; historia (CHANGELOG, decisiones) y guías no se tocan.
3. Recorre cada requisito del cambio: qué prueba lo cubre, su resultado, y si la prueba comprueba de verdad el comportamiento o es trivial.
4. Revisa los «Criterios de finalización» uno por uno y si `specs/` ya refleja el comportamiento final.
5. Señala explícitamente: pruebas borradas o debilitadas, código fuera del alcance declarado, requisitos sin cobertura real.
6. Da un veredicto (cumplido / no cumplido) y una lista de lo que el humano debe revisar antes de aprobar el merge. NO apruebes tú el merge.
7. Registra la ronda de revisión en `docs/LOG-PROCESO.md` (fila de tipo «revisión», **cerrada**, que cite la tarea y el cambio; desde `revision.corte_fuente` debe citar además `subagente <id>`) y ejecuta `python tools/sgp_review.py`. Solo si la puerta sale en verde y el humano aprueba: cambia `estado: hecho` en el frontmatter del cambio.

## No hacer
- No marques el cambio como `hecho` sin la aprobación explícita del humano.
- No marques `estado: hecho` sin la fila de revisión cerrada en `docs/LOG-PROCESO.md` y `python tools/sgp_review.py` en verde: de un cambio `hecho` solo se comprueba su consistencia de cierre (criterios y tareas marcados), así que cerrarlo sin esa ronda es un falso verde.
- No ocultes una prueba trivial o sin cobertura real solo porque el comando devolvió éxito.
