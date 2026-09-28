# SGP Lite — plantilla Spec-Driven con IA

Metodología mínima para trabajar con agentes de IA a partir de una spec acordada. Lee `METODOLOGIA.md` (una página). Requiere Python 3.8 o superior (solo librería estándar).

## Instalar en un repo (5 pasos)

1. Copia al repo: `docs/`, `specs/`, `changes/`, `tools/`, `skills/`, `AGENTS.md`, `CLAUDE.md`, `sgp.yaml`, `prompts.md`, `METODOLOGIA.md`.
2. Edita `docs/constitution.md`, `AGENTS.md` y los comandos de `sgp.yaml` (build, tests, lint y `test_por_requisito`).
3. Hook: `cp tools/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit` (en Windows funciona con Git Bash).
   Skills (opcional, si tu agente las soporta): `python tools/sync_skills.py --agent claude-code` (o `copilot`, `codex`, `cursor`, `generico`; `--list` muestra las opciones).
4. Primer cambio: fase 1 especificar → 2 QA → 3 planificar (elige carril: rapido/normal/mayor) → 4 ejecutar (una tarea por sesión) → 5 validar. Usa las skills si las instalaste, o los prompts equivalentes de `prompts.md`.
5. Verifica cuando quieras: `python tools/sgp_check.py` (rápido) · `--run` (con comandos) · `--stage pre-merge` (estricto, con trazabilidad).

## Ver cómo se ve terminado

En la raíz de este repositorio, `examples/descuento/` es un proyecto real y ejecutable (código, pruebas, especificaciones, dos cambios cerrados). El recorrido completo, con la salida real de cada comando, está en `docs/ejemplo-practico.md`.

```bash
python tools/sgp_check.py --root ../examples/descuento --stage pre-merge
```

Si tu sistema usa `python3` en vez de `python`, ajusta el comando o `examples/descuento/sgp.yaml`.

## Probar el verificador

```bash
python -m unittest tools/test_sgp_check.py -v     # 27 pruebas
```

## Contenido

```text
docs/constitution.md   docs/adr/_plantilla.md   specs/_plantilla-dominio/spec.md
changes/_plantilla.md  AGENTS.md  CLAUDE.md  sgp.yaml  prompts.md  METODOLOGIA.md
tools/sgp_check.py  tools/pre-commit  tools/sync_skills.py  tools/test_sgp_check.py
skills/sgp-especificar  skills/sgp-qa-spec  skills/sgp-planificar-cambio  skills/sgp-ejecutar-tarea  skills/sgp-validar-cerrar
```
