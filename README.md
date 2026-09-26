# Del SDLC en cascada al desarrollo continuo con agentes de IA

> Como las etapas clasicas del ciclo de vida del software (requerimientos → especificacion →
> etapas → pruebas → despliegue → mantenimiento) se comprimieron en un ciclo continuo por
> cambio, y que mecanismos concretos reemplazan a cada etapa cuando quien construye es
> mayormente un agente de IA.

Este repo nacio de una sesion real trabajando con un agente de IA en el diseño de un sistema
de gestion de proyectos, comparandolo contra herramientas de la industria (GitHub Spec Kit,
OpenSpec, BMAD-METHOD) y contra una politica de ingenieria personal ya en uso. El resultado no
fue "la herramienta definitiva" — fue un mapa de que reemplaza a que, una plantilla minima
(`kit/`) para aplicarlo, y la politica de ingenieria completar (`docs/system-engineering-policy.SKILL.md`)
que termino demostrando, en la practica, casi todos los puntos del mapeo de abajo.

## El mapeo

| SDLC tradicional | Que pasaba | Equivalente con un agente de IA | Mecanismo concreto |
|---|---|---|---|
| **Documento de requerimientos** | Se escribia una vez, al inicio del proyecto | Se convierte en un **requisito por cambio**, no por proyecto: se redacta cada vez que hay un pedido, con criterio de aceptacion observable | Seccion `REQUISITO` antes de tocar codigo; entrevista de una pregunta a la vez |
| **Documento de especificaciones** | Derivado del anterior; definia modulos y contratos | **Vive en el repo** (`specs/`), no en un documento aparte; se lee y actualiza en cada cambio, nunca "se termina" | Requisitos en formato EARS con ID, versionados en git |
| **Etapas del proyecto** | Fases secuenciales (analisis → diseño → construccion) | **Modos que se activan segun la tarea**, no segun el calendario | FIX / ARQUITECTURA / DOCS / CONSULTA — o, mas simple, carriles por tamaño (rapido / normal / mayor) |
| **Tareas por etapa** | Asignadas a personas, seguimiento manual | Tareas de 20-30 min por sesion de agente, cada una con un **criterio de exito verificable** | "Hecho cuando: \<condicion observable\>" |
| **Entregables por etapa** | Documentos de diseño, codigo, casos de prueba | **Evidencia ejecutada**, no descripciones: output real de comandos, nunca inventado | Nunca declarar terminado sin mostrar el resultado real de un comando |
| **Pruebas (al final)** | Fase separada, despues de "terminar" de construir | **Simultaneas a cada tarea**: el test se escribe antes que el codigo | Rojo → verde por tarea; trazabilidad real (ejecutar la prueba de cada requisito, no solo buscar su nombre en el codigo) |
| **Despliegue a produccion** | Evento unico, al final del proyecto | Un release por cambio pequeño, con **criticidad declarada desde el inicio** que decide cuanto rigor exige | Produccion / herramienta interna / script descartable — no todo pesa igual |
| **Correccion de errores** | Fase posterior al despliegue, con su propio flujo | El **mismo mecanismo que construir**, solo que mas acotado | Un carril "rapido": bug reproducido con una prueba de regresion, sin la ceremonia de un requisito nuevo |
| **Mantenimiento** | Fase final, a menudo descuidada — "nadie actualiza los documentos" | **No es una fase**: la spec nunca dejar de estar viva porque cada cambio futuro la relee antes de tocar nada | Decisiones documentadas (ADR) para no repetir una decision ya tomada y descartada |

## La diferencia real, no cosmetica

En el modelo tradicional el riesgo estaba en que **construir era lento y corregir el rumbo
costaba caro** — por eso se invertia tanto en especificar antes de escribir codigo. Con un
agente de IA, construir es barato y rapido; el riesgo se invirtio: **el peligro es que el
agente construya rapido y mal, sin que nadie lo note.**

Por eso los mecanismos que importan hoy no son "escribe mas documentacion", son:

- que nada se de por terminado sin una prueba real que lo demuestre,
- que lo que falta se pregunte, nunca se infiera,
- que no se toque nada fuera del pedido actual,
- que las decisiones no se pierdan en una conversacion oral que nadie vuelve a leer.

Lo que **no** cambio: alguien humano tiene que aprobar antes de comprometerse (commit, merge,
release), y las decisiones de arquitectura se siguen documentando para no repetir errores. La
IA no lo volvio innecesario — lo volvio mas urgente, porque ahora las decisiones se toman con
mas frecuencia y mas rapido que antes.

## Que hay en este repo

```text
.
├── README.md                    — este documento
├── docs/
│   ├── ejemplo-practico.md              — recorrido real, con salidas de comandos capturadas (no simuladas)
│   └── system-engineering-policy.SKILL.md — politica de ingenieria completar (evidencia antes de editar,
│                                             DONE verificable, sin inferir, sin tocar fuera de alcance,
│                                             confirmacion antes de comprometer cambios). Instalable tal
│                                             cual como Agent Skill en cualquier agente compatible.
├── kit/                         — plantilla minima aplicable a cualquier repo (SGP Lite)
│   ├── METODOLOGIA.md           — la metodologia en una pagina
│   ├── docs/constitution.md     — principios innegociables, cada uno con su forma de verificarse
│   ├── specs/                   — donde viven los requisitos vigentes
│   ├── changes/                 — plantilla de un cambio (propuesta + tareas + progreso)
│   ├── skills/                  — 5 Agent Skills (estandar agentskills.io) instalables en el agente
│   ├── prompts.md               — los mismos 5 pasos como prompts, para agentes sin soporte de skills
│   └── tools/
│       ├── sgp_check.py         — verificador: estructura, trazabilidad real, presupuesto, ratchet de pruebas
│       ├── sync_skills.py       — instalar las skills en la ruta de el agente
│       └── pre-commit           — hook de git que bloquea pruebas borradas o debilitadas
└── examples/
    └── descuento/                — proyecto real y ejecutable de punta a punta (ver docs/ejemplo-practico.md)
```

### Kit vs. politica — como se relacionan

`kit/` (SGP Lite) resuelve el *ciclo del cambio*: spec → tareas → verificacion → cierre, con un
verificador que corre en cualquier CI. `docs/system-engineering-policy.SKILL.md` resuelve el
*comportamiento del agente dentro de cada tarea*: que evidencia exige antes de editar, cuando
algo cuenta como "hecho", cuando debe preguntar en vez de inferir, y cuando debe pedir tu
confirmacion antes de comprometerse. Son complementarias — puedes usar una sin la otra, o las dos
juntas: la politica gobierna el paso 4 (ejecutar una tarea) del kit con mas profundidad de la que
el kit define por si solo.

### Empezar

```bash
cd kit
python tools/sgp_check.py --help
python -m unittest tools/test_sgp_check.py -v   # 27 pruebas del propio verificador
```

Para instalar el kit en un repo propio, seguir `kit/LEEME.md`.

## Procedimiento de implementacion

Orden recomendado para adoptar esto en un repo real, de menor a mayor compromiso. Cada paso es
opcional respecto al siguiente — se puede parar en cualquiera y quedar en un estado util.

### Paso 0 — Solo la politica de comportamiento (mas barato, sin tocar nada del repo)

1. Copiar `docs/system-engineering-policy.SKILL.md` a la carpeta de skills de el agente
   (p. ej. `~/.claude/skills/system-engineering-policy/SKILL.md` para Claude Code).
2. No requiere ningun archivo nuevo en el repo de trabajo. Gobierna el *comportamiento* del
   agente (evidencia antes de editar, DONE verificable, no inferir, no salir de alcance) en
   cualquier tarea, sin metodologia de specs.
3. Valido como punto de partida unico — es la pieza que mas impacto tiene por menor costo.

### Paso 1 — Kit minimo en un repo (metodologia de specs)

1. Copiar al repo: `kit/docs/`, `kit/specs/`, `kit/changes/`, `kit/tools/`, `kit/AGENTS.md`,
   `kit/CLAUDE.md`, `kit/sgp.yaml`, `kit/prompts.md`, `kit/METODOLOGIA.md`.
2. Editar `docs/constitution.md`, `AGENTS.md` y los comandos de `sgp.yaml` (build, tests, lint,
   `test_por_requisito`) para el stack.
3. Instalar el hook: `cp tools/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`.

### Paso 2 — Skills del kit (si el agente soporta Agent Skills)

```bash
python tools/sync_skills.py --agent claude-code   # o copilot, codex, cursor, generico
```

Instala `sgp-especificar`, `sgp-qa-spec`, `sgp-planificar-cambio`, `sgp-ejecutar-tarea` y
`sgp-validar-cerrar`. Si el agente no soporta skills, usa los mismos 5 pasos como prompts desde
`kit/prompts.md`.

### Paso 3 — Primer cambio real

1. Especificar: entrevista de una pregunta a la vez → `specs/<dominio>/spec.md` con requisitos
   EARS e ID (`DOM-001`).
2. QA de la spec: ambiguedades, contradicciones, casos limite, conflictos con la constitucion.
3. Planificar: `python tools/sgp_check.py --nuevo <nombre>` → completar propuesta, criterios de
   finalizacion y tareas de 20-30 min con "Hecho cuando: ...".
4. Ejecutar: una tarea por sesion, prueba en rojo antes que codigo, `sgp_check.py --run` al
   terminar cada una.
5. Validar y cerrar: `sgp_check.py --stage pre-merge` (trazabilidad real por requisito, no solo
   por nombre) antes de aprobar el merge.

Ver `docs/ejemplo-practico.md` para este mismo procedimiento corrido de punta a punta, con las
salidas reales de cada comando.

### Paso 4 — Repetir y ajustar

No hay fase final. Cada cambio futuro repite el Paso 3 y relee `specs/` antes de tocar nada —
asi la especificacion nunca queda desactualizada. Ajusta `sgp.yaml` (presupuesto de iteraciones,
limite de revisiones) con lo que un uso muestre que hace falta.

## Por que esto no es "la forma correcta"

La base de evidencia sobre desarrollo guiado por especificaciones con IA es todavia joven —
Thoughtworks lo tiene en su Radar en el anillo *Assess* (vale la pena explorar, no adoptar a
ciegas) al momento de escribir esto. Este repo documenta un mapeo y una plantilla que
funcionaron en un caso concreto, con sus pruebas y su ejemplo ejecutable — no una receta
universal. Ajustalo con tu propia evidencia antes de confiar en el para produccion.

## Fuentes y practicas de referencia

- Thoughtworks Technology Radar — *Spec-driven development* y *OpenSpec*
- GitHub Spec Kit, Kiro (specs con notacion EARS), BMAD-METHOD (pistas por complejidad)
- Bockeler, *Harness engineering for coding agent users* (Martin Fowler blog) — guias vs. sensores
- Anthropic, *Effective harnesses for long-running agents*
- DORA — informe 2025 sobre desarrollo asistido por IA
- El estandar abierto Agent Skills (agentskills.io)

Ninguna de estas fuentes se cita como autoridad ultima; se contrastaron entre si y varias son
blogs o repositorios comunitarios, no normas oficiales.

## Licencia

MIT — ver [`LICENSE`](LICENSE). Usalo, adaptalo, rompelo y contame que no funciono.
