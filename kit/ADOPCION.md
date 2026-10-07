# Adopción por tamaño — ¿cuánto del kit usar?

Este kit sirve para proyectos de cualquier tamaño, pero **no todo proyecto necesita todo el kit**.
La regla es la de la industria: **empezar por lo mínimo y subir solo cuando duela**.

> Es una guía, no una ley. Mira tus señales (tamaño, criticidad, cuántas personas/agentes, cuánto va a durar) y decide.

## Cuatro formas de trabajar (de menos a más)

| Forma | Cuándo usarla | Qué agrega | Cómo se comprueba |
|---|---|---|---|
| **1. Solo la política** | Casi nunca tocas código, o no quieres cambiar nada del repo | La skill de comportamiento del agente (`docs/system-engineering-policy.SKILL.md`) | — |
| **2. Spec primero** (*spec-first*) | Cambio no obvio en un proyecto chico | Una spec breve antes de codificar + `AGENTS.md` corto | Tests (si hay) o prueba manual |
| **3. Spec anclada** (*spec-anchored*) | El proyecto vive y evoluciona; hay requisitos que conviene mantener y auditar | `specs/`, `changes/`, `docs/constitution.md`, `sgp_check` | `python tools/sgp_check.py --run` |
| **4. Kit completo** (*spec-as-source* + gobierno) | Ruta crítica, compliance, varios agentes/personas, regresiones costosas | Skills, `pre-commit`/ratchet, ADR, presupuestos, trazabilidad por requisito | `python tools/sgp_check.py --stage pre-merge` |

No son fases obligatorias: son **puntos de entrada**. Puedes quedarte en cualquiera y seguir en un estado útil.

## Puntos de entrada independientes (no todo es "una feature")

- **Bugfix**: un arreglo con su prueba de regresión. Si es trivial (typo, una línea), un *quick fix* alcanza.
- **Assessment**: decidir si algo merece la pena, antes de construir. Puede usarse solo.
- **Documento de requerimientos** (opcional, solo documentación): aclarar un pedido grande o confuso antes de escribir la spec. No es una fase ni lo verifica el kit.

## Cuándo subir de forma

- Se borró o debilitó una prueba → añade el candado (ratchet).
- El cambio toca **más de un dominio** o cambia un contrato/API → sección de diseño / ADR.
- Varias personas o agentes sobre el repo → skills + constitución.
- Necesitas **trazar** cada requisito a una prueba (auditoría, compliance) → IDs EARS + `--stage pre-merge`.
- El proyecto va a **durar** → spec anclada.

## Cuándo bajar de forma

- Si nunca relees `specs/`/`changes/`, vuelve a *spec primero*.
- Si no hay forma de ejecutar tests automáticos, descarta `sgp_check`.
- Si el flujo se siente como **"un martillo para una nuez"**, baja.

## Señales de que te pasaste (ceremonia inútil)

- Revisas más markdown que código.
- Un bug de una línea genera una spec de varias páginas.
- El equipo dejó de usar la metodología.

## Para no duplicar

- Cuándo **no** conviene: `docs/manual-usuario.md` §9.
- La metodología en una página: `METODOLOGIA.md`.
- Procedimiento por pasos: `README.md` → «Procedimiento de implementación».

## Basado en

Thoughtworks Technology Radar (SDD en «Assess»; flujos ligeros vs pesados) · Böckeler/Fowler
(«spec-first / spec-anchored / spec-as-source») · Kiro (Quick vs Feature, Bugfix vs quick fix) ·
GitHub Spec Kit (puntos de entrada independientes) · PMI/CMMI (ajustar el proceso al tamaño y la criticidad).
