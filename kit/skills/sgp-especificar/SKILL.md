---
name: sgp-especificar
description: Redacta o actualiza specs/<dominio>/spec.md en requisitos EARS verificables mediante una entrevista de una pregunta a la vez. Úsala cuando el usuario pida una funcionalidad nueva, cambiar el comportamiento vigente de un dominio, o diga "especificar", "definir requisitos", "actualizar la spec". NO la uses para bugs de una línea (carril rápido) ni para escribir código.
---

# Especificar (o cambiar) una spec — SGP

No escribas código. El objetivo es dejar `specs/<dominio>/spec.md` correcto y aprobado por el humano.

## Pasos
1. Lee `docs/constitution.md` y la spec vigente del dominio (si existe).
2. Haz preguntas de **una en una** para eliminar ambigüedades: casos límite, errores, fuera de alcance. Máximo 6 preguntas. Prioriza las que más cambian el alcance.
3. Con las respuestas, edita `specs/<dominio>/spec.md`:
   - Contexto y objetivo (sin tecnología).
   - Requisitos con ID único `DOM-NNN` en formato EARS en español:
     - CUANDO <evento>, EL SISTEMA <respuesta observable>
     - SI <condición no deseada>, ENTONCES EL SISTEMA <respuesta>
     - MIENTRAS <estado>, EL SISTEMA <respuesta>
     - EL SISTEMA <propiedad que siempre se cumple>
   - No funcionales, casos límite (→ requisito que los cubre), fuera de alcance, dudas abiertas con `[POR-ACLARAR]`.
4. Cada respuesta debe ser observable (mensaje, código de salida, estado). Nada de "rápido", "intuitivo", "adecuado" sin cifra.
5. Muestra el diff y espera aprobación explícita antes de continuar a un cambio.

## No hacer
- No toques código ni archivos de `changes/`.
- No asumas respuestas a las preguntas: pregunta y espera.
- No mezcles el *cómo* (arquitectura, stack) en la spec.
