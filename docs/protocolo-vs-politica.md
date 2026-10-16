# Protocolo frente a política — clasificación y decisión (2026-10-15)

Documento de trazabilidad: por qué el skill `protocolo-ingenieria-senior` pasó de 320 líneas
a runbook (v2.0.0). Decisión: **opción A** del análisis del 2026-10-15 (el protocolo solo cita).

## Método
1. Comparación línea a línea (normalizada) entre el protocolo y la política.
2. Lectura completa de ambos documentos y clasificación de cada línea del protocolo en:
   *regla reescrita* (ya está en la política) · *detalle operativo* (listas/ejemplos) · *hueco real* (regla solo aquí).

## Resultado
- 136 líneas de contenido en el protocolo: **8 coincidían literalmente** con la política,
  **122 eran reescrituras** de reglas que también están en la política, **0 huecos reales**.
- Conclusión: el protocolo **no definía ninguna regla propia**; su valor era el orden de trabajo
  (listas), que se conserva reescrito como runbook con citas.

## Derivas detectadas (la razón de la decisión)
| Regla actualizada en la política | Estado en el protocolo (antes) |
|---|---|
| Fila "docs de proyecto" con `git diff --name-only HEAD` (§2.4) | `git diff --name-only`, sin `HEAD` (`:91`) |
| Inventario de docs con grep + tabla de entrega (§16.5) | Ausente; versión antigua en `:316-318` |
| Línea base §4.4 con "doc mínima desde el primer commit" | Ausente; la lista tenía 5 puntos (`:156-161`) |

Ninguna guarda automática detectaba esto: `test_policy_sync.py` compara las copias de cada documento
entre sí, no la política contra el protocolo.

## Consecuencias aplicadas
- El protocolo pasa a runbook: **no repite reglas**, cada punto cita su sección de la política.
- Las 3 derivas desaparecen por construcción (no se reescribe la regla que podría quedar vieja).
- La política **no se modificó** (no había reglas que subir).

## Hallazgos para revisar en el próximo cambio de la política
- **Resuelto el 2026-10-15** (kit 1.6.10): la política, §1.2, decía del protocolo *"este skill
  establece el procedimiento de rigor"*. Ahora dice que el protocolo es el **runbook** ("no define
  reglas: las cita de esta política") y que el rigor vive en la política. Se aplicó la cadena
  completa: canónica → 3 copias del kit (byte a byte, guardadas) → 3 proyectos.
- **Decisión (2026-10-15): opción A** — el runbook se conserva como **skill separado** (no como
  anexo de la política: anexarlo obligaría a cargar la chuleta en todas las sesiones y mezclaría
  obligaciones con listas prácticas). Para que no pueda desviarse en silencio:
  - El runbook **no define reglas**: cita secciones de la política.
  - Nueva guarda `kit/tools/test_protocolo_citas.py`: falla si alguna cita `§` del runbook apunta
    a una sección que no existe en la política, o si el runbook deja de citar.
  - Revisión prevista: si en la práctica no se consulta, se retirará (opción C) y se quitará su
    paso de §1.2.
