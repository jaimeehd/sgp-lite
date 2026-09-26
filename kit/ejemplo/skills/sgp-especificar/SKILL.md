---
name: sgp-especificar
description: Redacta o actualiza specs/<dominio>/spec.md en requisitos EARS verificables mediante una entrevista de una pregunta a la vez. Usala cuando el usuario pida una funcionalidad nueva, cambiar el comportamiento vigente de un dominio, o diga "especificar", "definir requisitos", "actualizar la spec". NO la uses para bugs de una linea (carril rapido) ni para escribir codigo.
---

# Especificar (o cambiar) una spec — SGP

No escribas codigo. El objetivo es dejar `specs/<dominio>/spec.md` correcto y aprobado por el humano.

## Pasos
1. Lee `docs/constitution.md` y la spec vigente del dominio (si existe).
2. Haz preguntas de **una en una** para eliminar ambiguedades: casos limite, errores, fuera de alcance. Maximo 6 preguntas. Prioriza las que mas cambian el alcance.
3. Con las respuestas, editar `specs/<dominio>/spec.md`:
   - Contexto y objetivo (sin tecnologia).
   - Requisitos con ID unico `DOM-NNN` en formato EARS en español:
     - CUANDO <evento>, EL SISTEMA <respuesta observable>
     - SI <condicion no deseada>, ENTONCES EL SISTEMA <respuesta>
     - MIENTRAS <estado>, EL SISTEMA <respuesta>
     - EL SISTEMA <propiedad que siempre se cumple>
   - No funcionales, casos limite (→ requisito que los cubre), fuera de alcance, dudas abiertas con `[POR-ACLARAR]`.
4. Cada respuesta debe ser observable (mensaje, codigo de salida, estado). Nada de "rapido", "intuitivo", "adecuado" sin cifra.
5. Muestra el diff y espera aprobacion explicita antes de continuar a un cambio.

## No hacer
- No toques codigo ni archivos de `changes/`.
- No asumas respuestas a las preguntas: pregunta y espera.
- No mezcles el *como* (arquitectura, stack) en la spec.
