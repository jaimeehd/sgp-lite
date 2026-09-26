# SGP Lite — plantilla Spec-Driven con IA

Metodologia minima para trabajar con agentes de IA a partir de una spec acordada. Lee `METODOLOGIA.md` (una pagina). Requiere Python 3.8+ (solo libreria estandar).

## Instalar en un repo (5 pasos)

1. copiar al repo: `docs/`, `specs/`, `changes/`, `tools/`, `skills/`, `AGENTS.md`, `CLAUDE.md`, `sgp.yaml`, `prompts.md`, `METODOLOGIA.md`.
2. editar `docs/constitution.md`, `AGENTS.md` y los comandos de `sgp.yaml` (build, tests, lint y `test_por_requisito`).
3. Hook: `cp tools/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit` (en Windows funciona con Git Bash).
   Skills (opcional, si el agente las soporta): `python tools/sync_skills.py --agent claude-code` (o `copilot`, `codex`, `cursor`, `generico`; `--list` muestra las opciones).
4. Primer cambio: fase 1 especificar → 2 QA → 3 planificar (elige carril: rapido/normal/mayor) → 4 ejecutar (una tarea por sesion) → 5 validar. usar las skills si las instalaste, o los prompts equivalentes de `prompts.md`.
5. Verifica cuando quieras: `python tools/sgp_check.py` (rapido) · `--run` (con comandos) · `--stage pre-merge` (estricto, con trazabilidad).

## Ver como se ve terminado

`ejemplo/` es un mini-repo real (codigo, pruebas, spec, cambio en revision). Desde la raiz de esta carpeta:

```bash
python tools/sgp_check.py --root ejemplo --stage pre-merge
```
(sus comandos usan `python`; si en tu sistema es `python3`, ajusta `ejemplo/sgp.yaml`).

## Probar el verificador

```bash
python -m unittest tools/test_sgp_check.py -v     # 23 pruebas
```

## Contenido

```text
docs/constitution.md   docs/adr/_plantilla.md   specs/_plantilla-dominio/spec.md
changes/_plantilla.md  AGENTS.md  CLAUDE.md  sgp.yaml  prompts.md  METODOLOGIA.md
tools/sgp_check.py  tools/pre-commit  tools/sync_skills.py  tools/test_sgp_check.py
skills/sgp-especificar  skills/sgp-qa-spec  skills/sgp-planificar-cambio  skills/sgp-ejecutar-tarea  skills/sgp-validar-cerrar
ejemplo/
```
