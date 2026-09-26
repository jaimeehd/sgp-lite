---
name: sgp-qa-spec
description: Revisa una spec de SGP como un QA exigente antes de planificar un cambio — detecta ambiguedades, contradicciones entre requisitos, casos limite no cubiertos y conflictos con la constitucion. Usala despues de sgp-especificar y antes de sgp-planificar-cambio, o cuando el usuario pida "revisar la spec" o "QA de requisitos".
---

# QA de la spec — SGP

Revisa `specs/<dominio>/spec.md` frente a `docs/constitution.md`. No propongas soluciones: solo detecta.

## Salida
Lista numerada con cuatro categorias:
1. Ambiguedades (requisitos que admiten mas de una interpretacion razonable).
2. Contradicciones entre requisitos.
3. Casos limite mencionados pero sin requisito que los cubra, o requisitos sin escenario de error.
4. Conflictos con algun principio de `docs/constitution.md`.

## No hacer
- No edites la spec ni ningun archivo.
- No sugieras redacciones alternativas: solo señala el problema y por que lo es.
