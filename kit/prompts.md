# Prompts SGP Lite

Pega el prompt de la fase, con el contexto indicado. Cada uno declara **que NO hacer** y la **evidencia** que debe devolver.

## 1. Especificar (o cambiar la spec) — apruebas la spec
Contexto: `docs/constitution.md`, `specs/<dominio>/spec.md` (si existe) y tu idea.
```text
NO escribas codigo. Vamos a redactar (o cambiar) la spec de <funcionalidad>. Lee docs/constitution.md y la spec vigente.
1. Hazme preguntas de UNA en UNA para eliminar ambiguedades (casos limite, errores, fuera de alcance). Maximo 6.
2. Con mis respuestas, edita specs/<dominio>/spec.md: contexto y objetivo, requisitos con ID unico (DOM-NNN) en EARS en español, no funcionales,
   casos limite (→ requisito que los cubre), fuera de alcance y dudas abiertas con [POR-ACLARAR].
3. Solo el QUE y el POR QUE: nada de stack, arquitectura ni archivos.
4. Cada respuesta del sistema debe ser observable (mensaje, codigo de salida o estado). Sin terminos vagos.
Evidencia: muestrame el diff de la spec y espera mi aprobacion.
```

## 2. QA de la spec
```text
Revisa specs/<dominio>/spec.md como un QA muy exigente. Lista numerada de: (1) ambiguedades, (2) contradicciones entre requisitos,
(3) casos limite no cubiertos, (4) conflictos con docs/constitution.md. NO propongas soluciones: solo detecta. No toques archivos.
```

## 3. Cambio: plan y tareas — apruebas plan y tareas
Contexto: constitucion, spec aprobada, `changes/_plantilla.md`, codigo de las areas afectadas.
```text
NO escribas codigo. Crea el cambio con `python tools/sgp_check.py --nuevo <nombre>` y completalo:
- Propuesta: problema, resultado esperado, alcance, fuera de alcance. Apetito en dias.
- `requisitos:` con los IDs de la spec que se añaden o modifican (deben existir en specs/).
- Diseño (solo si hay decisiones tecnicas): enfoque breve y alternativa descartada. Si es una decision estructural, redacta un ADR (docs/adr/).
- Criterios de finalizacion.
- Tareas de 20-30 min maximo, en orden de dependencia, cada una con [IDs] y una linea «Hecho cuando:» verificable.
  Todos los requisitos deben estar cubiertos por alguna tarea. Si el cambio supera ~10 tareas, propon dividirlo.
Evidencia: ejecuta `python tools/sgp_check.py` y muestrame el resultado.
```

## 4. Ejecutar UNA tarea (sesion nueva por tarea)
Contexto minimo: `AGENTS.md`, el cambio activo, la spec de los requisitos de la tarea y los archivos que toca.
```text
Implementa SOLO la tarea <TNNN> de changes/<CHG-NNN>.md. Escribe primero la prueba (su nombre incluye el ID, p. ej. test_EXP_001_...) y verifica que falla; luego el codigo.
NO borres ni edites pruebas existentes. NO amplies el alcance (ideas nuevas → «Notas»). Si un requisito es ambiguo, para y pregunta.
Ejecuta `python tools/sgp_check.py --run` y MUESTRAME el resultado. Si falla, corrige (max. iteraciones: sgp.yaml); si las agotas, detente y anota en «Progreso» que debe aclararse.
Al pasar: marca la tarea [x], indica que requisitos cubre, actualiza «Progreso» y DETENTE. No empieces la siguiente tarea.
```

## 5. Validar y cerrar — apruebas el merge
Contexto: el cambio, la spec y el resultado de `python tools/sgp_check.py --stage pre-merge`.
```text
Recorre los requisitos del cambio uno por uno. Para cada uno indica: que prueba lo cubre, el resultado de ejecutarla y si la prueba comprueba de verdad
el comportamiento (o es trivial). Revisa los «Criterios de finalizacion» y que specs/ refleje el comportamiento final. Señala pruebas borradas o debilitadas y todo lo que se salga del alcance.
Da un veredicto: ¿el cambio esta cumplido? NO apruebes tu el merge: lista lo que debo revisar.
```
