---
name: sgp-qa-spec
description: Revisa una spec de SGP como un QA exigente antes de planificar un cambio — detecta ambigüedades, contradicciones entre requisitos, casos límite no cubiertos y conflictos con la constitución. Úsala después de sgp-especificar y antes de sgp-planificar-cambio, o cuando el usuario pida "revisar la spec" o "QA de requisitos".
---

# QA de la spec — SGP

Revisa `specs/<dominio>/spec.md` frente a `docs/constitution.md`. No propongas soluciones: solo detecta.

## Salida
Lista numerada con cuatro categorías:
1. Ambigüedades (requisitos que admiten más de una interpretación razonable).
2. Contradicciones entre requisitos.
3. Casos límite mencionados pero sin requisito que los cubra, o requisitos sin escenario de error.
4. Conflictos con algún principio de `docs/constitution.md`.

## No hacer
- No edites la spec ni ningún archivo.
- No sugieras redacciones alternativas: solo señala el problema y por qué lo es.
