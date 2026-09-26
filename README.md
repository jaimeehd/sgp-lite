# Del SDLC en cascada al desarrollo continuo con agentes de IA

> Cómo las etapas clásicas del ciclo de vida del software (requerimientos → especificación →
> etapas → pruebas → despliegue → mantenimiento) se comprimieron en un ciclo continuo por
> cambio, y qué mecanismos concretos reemplazan a cada etapa cuando quien construye es
> mayormente un agente de IA.

Este repo nació de una sesión real trabajando con un agente de IA en el diseño de un sistema
de gestión de proyectos, comparándolo contra herramientas de la industria (GitHub Spec Kit,
OpenSpec, BMAD-METHOD) y contra una política de ingeniería personal ya en uso. El resultado no
fue "la herramienta definitiva" — fue un mapa de qué reemplaza a qué, una plantilla mínima
(`kit/`) para aplicarlo, y la política de ingeniería completa (`docs/system-engineering-policy.SKILL.md`)
que terminó demostrando, en la práctica, casi todos los puntos del mapeo de abajo.

## El mapeo

| SDLC tradicional | Qué pasaba | Equivalente con un agente de IA | Mecanismo concreto |
|---|---|---|---|
| **Documento de requerimientos** | Se escribía una vez, al inicio del proyecto | Se convierte en un **requisito por cambio**, no por proyecto: se redacta cada vez que hay un pedido, con criterio de aceptación observable | Sección `REQUISITO` antes de tocar código; entrevista de una pregunta a la vez |
| **Documento de especificaciones** | Derivado del anterior; definía módulos y contratos | **Vive en el repo** (`specs/`), no en un documento aparte; se lee y actualiza en cada cambio, nunca "se termina" | Requisitos en formato EARS con ID, versionados en git |
| **Etapas del proyecto** | Fases secuenciales (análisis → diseño → construcción) | **Modos que se activan según la tarea**, no según el calendario | FIX / ARQUITECTURA / DOCS / CONSULTA — o, más simple, carriles por tamaño (rápido / normal / mayor) |
| **Tareas por etapa** | Asignadas a personas, seguimiento manual | Tareas de 20-30 min por sesión de agente, cada una con un **criterio de éxito verificable** | "Hecho cuando: \<condición observable\>" |
| **Entregables por etapa** | Documentos de diseño, código, casos de prueba | **Evidencia ejecutada**, no descripciones: output real de comandos, nunca inventado | Nunca declarar terminado sin mostrar el resultado real de un comando |
| **Pruebas (al final)** | Fase separada, después de "terminar" de construir | **Simultáneas a cada tarea**: el test se escribe antes que el código | Rojo → verde por tarea; trazabilidad real (ejecutar la prueba de cada requisito, no solo buscar su nombre en el código) |
| **Despliegue a producción** | Evento único, al final del proyecto | Un release por cambio pequeño, con **criticidad declarada desde el inicio** que decide cuánto rigor exige | Producción / herramienta interna / script descartable — no todo pesa igual |
| **Corrección de errores** | Fase posterior al despliegue, con su propio flujo | El **mismo mecanismo que construir**, solo que más acotado | Un carril "rápido": bug reproducido con una prueba de regresión, sin la ceremonia de un requisito nuevo |
| **Mantenimiento** | Fase final, a menudo descuidada — "nadie actualiza los documentos" | **No es una fase**: la spec nunca deja de estar viva porque cada cambio futuro la relee antes de tocar nada | Decisiones documentadas (ADR) para no repetir una decisión ya tomada y descartada |

## La diferencia real, no cosmética

En el modelo tradicional el riesgo estaba en que **construir era lento y corregir el rumbo
costaba caro** — por eso se invertía tanto en especificar antes de escribir código. Con un
agente de IA, construir es barato y rápido; el riesgo se invirtió: **el peligro es que el
agente construya rápido y mal, sin que nadie lo note.**

Por eso los mecanismos que importan hoy no son "escribe más documentación", son:

- que nada se dé por terminado sin una prueba real que lo demuestre,
- que lo que falta se pregunte, nunca se infiera,
- que no se toque nada fuera del pedido actual,
- que las decisiones no se pierdan en una conversación oral que nadie vuelve a leer.

Lo que **no** cambió: alguien humano tiene que aprobar antes de comprometerse (commit, merge,
release), y las decisiones de arquitectura se siguen documentando para no repetir errores. La
IA no lo volvió innecesario — lo volvió más urgente, porque ahora las decisiones se toman con
más frecuencia y más rápido que antes.

## Qué hay en este repo

```text
.
├── README.md                    — este documento
├── docs/
│   ├── ejemplo-practico.md              — recorrido real, con salidas de comandos capturadas (no simuladas)
│   └── system-engineering-policy.SKILL.md — política de ingeniería completa (evidencia antes de editar,
│                                             DONE verificable, sin inferir, sin tocar fuera de alcance,
│                                             confirmación antes de comprometer cambios). Instalable tal
│                                             cual como Agent Skill en cualquier agente compatible.
├── kit/                         — plantilla mínima aplicable a cualquier repo (SGP Lite)
│   ├── METODOLOGIA.md           — la metodología en una página
│   ├── docs/constitution.md     — principios innegociables, cada uno con su forma de verificarse
│   ├── specs/                   — dónde viven los requisitos vigentes
│   ├── changes/                 — plantilla de un cambio (propuesta + tareas + progreso)
│   ├── skills/                  — 5 Agent Skills (estándar agentskills.io) instalables en tu agente
│   ├── prompts.md               — los mismos 5 pasos como prompts, para agentes sin soporte de skills
│   └── tools/
│       ├── sgp_check.py         — verificador: estructura, trazabilidad real, presupuesto, ratchet de pruebas
│       ├── sync_skills.py       — instala las skills en la ruta de tu agente
│       └── pre-commit           — hook de git que bloquea pruebas borradas o debilitadas
└── examples/
    └── descuento/                — proyecto real y ejecutable de punta a punta (ver docs/ejemplo-practico.md)
```

### Kit vs. política — cómo se relacionan

`kit/` (SGP Lite) resuelve el *ciclo del cambio*: spec → tareas → verificación → cierre, con un
verificador que corre en cualquier CI. `docs/system-engineering-policy.SKILL.md` resuelve el
*comportamiento del agente dentro de cada tarea*: qué evidencia exige antes de editar, cuándo
algo cuenta como "hecho", cuándo debe preguntar en vez de inferir, y cuándo debe pedir tu
confirmación antes de comprometerse. Son complementarias — podés usar una sin la otra, o las dos
juntas: la política gobierna el paso 4 (ejecutar una tarea) del kit con más profundidad de la que
el kit define por sí solo.

### Empezar

```bash
cd kit
python tools/sgp_check.py --help
python -m unittest tools/test_sgp_check.py -v   # 27 pruebas del propio verificador
```

Para instalar el kit en un repo propio, seguí `kit/LEEME.md`.

## Por qué esto no es "la forma correcta"

La base de evidencia sobre desarrollo guiado por especificaciones con IA es todavía joven —
Thoughtworks lo tiene en su Radar en el anillo *Assess* (vale la pena explorar, no adoptar a
ciegas) al momento de escribir esto. Este repo documenta un mapeo y una plantilla que
funcionaron en un caso concreto, con sus pruebas y su ejemplo ejecutable — no una receta
universal. Ajustalo con tu propia evidencia antes de confiar en él para producción.

## Fuentes y prácticas de referencia

- Thoughtworks Technology Radar — *Spec-driven development* y *OpenSpec*
- GitHub Spec Kit, Kiro (specs con notación EARS), BMAD-METHOD (pistas por complejidad)
- Böckeler, *Harness engineering for coding agent users* (Martin Fowler blog) — guías vs. sensores
- Anthropic, *Effective harnesses for long-running agents*
- DORA — informe 2025 sobre desarrollo asistido por IA
- El estándar abierto Agent Skills (agentskills.io)

Ninguna de estas fuentes se cita como autoridad última; se contrastaron entre sí y varias son
blogs o repositorios comunitarios, no normas oficiales.

## Licencia

MIT — ver [`LICENSE`](LICENSE). Usalo, adaptalo, rompelo y contame qué no funcionó.
