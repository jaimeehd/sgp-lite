---
name: sgp-planificar-cambio
description: Crea un changes/CHG-NNN-*.md de SGP con propuesta, diseño (si aplica) y tareas de 20-30 min enlazadas a requisitos existentes en specs/. Úsala cuando el usuario diga "crear un cambio", "planificar esta funcionalidad" o tras aprobar una spec. Elige el carril (rapido/normal/mayor) según el alcance.
---

# Planificar un cambio — SGP

No escribas código.

## Pasos
1. Crea el archivo: `python tools/sgp_check.py --nuevo <nombre>`.
2. Elige el carril:
   - **rapido**: bug o spike de <1 día, sin requisitos nuevos.
   - **normal**: toca un solo dominio de `specs/`, sin decisiones de arquitectura.
   - **mayor**: cruza dominios, cambia un contrato/API, o añade una dependencia — exige sección `## Diseño` con una alternativa descartada y, si la decisión es estructural, un ADR en `docs/adr/`.
   Si dudas entre dos, elige el menor y sube si aparece incertidumbre real.
3. Completa: Propuesta (problema, resultado esperado, alcance, fuera de alcance, apetito en días), `requisitos:` con los IDs de la spec (deben existir ya en `specs/`), Diseño si corresponde, Criterios de finalización.
4. Tareas de 20-30 min, en orden de dependencia, cada una con `[IDs]` y una línea `Hecho cuando:` verificable. Todo requisito citado debe quedar cubierto por alguna tarea. Si el cambio supera ~10 tareas, propón dividirlo en más de un cambio.
5. Ejecuta `python tools/sgp_check.py` y muestra el resultado.

## No hacer
- No inventes requisitos: si falta uno en `specs/`, usa primero la skill `sgp-especificar`.
- No escribas código ni pruebas todavía.
