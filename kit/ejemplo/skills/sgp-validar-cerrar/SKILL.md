---
name: sgp-validar-cerrar
description: Valida un cambio SGP requisito por requisito (que prueba lo cubre y su resultado) antes del merge, y prepara el cierre. Usala cuando el usuario diga "valida este cambio", "preparalo para revision" o cuando todas las tareas de un changes/CHG-*.md esten marcadas.
---

# Validar y cerrar — SGP

Contexto: el cambio, `specs/` y el resultado de `python tools/sgp_check.py --stage pre-merge`.

## Pasos
1. Ejecuta `python tools/sgp_check.py --stage pre-merge` y recoge la tabla de trazabilidad.
2. Recorre cada requisito del cambio: que prueba lo cubre, su resultado, y si la prueba comprueba de verdad el comportamiento o es trivial.
3. Revisa los «Criterios de finalizacion» uno por uno y si `specs/` ya refleja el comportamiento final.
4. Señala explicitamente: pruebas borradas o debilitadas, codigo fuera del alcance declarado, requisitos sin cobertura real.
5. Da un veredicto (cumplido / no cumplido) y una lista de lo que el humano debe revisar antes de aprobar el merge. NO apruebes tu el merge.
6. Si se aprueba: cambia `estado: hecho` en el frontmatter del cambio.

## No hacer
- No marques el cambio como `hecho` sin la aprobacion explicita del humano.
- No ocultes una prueba trivial o sin cobertura real solo porque el comando devolvio exito.
