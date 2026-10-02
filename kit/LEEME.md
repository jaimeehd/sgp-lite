# SGP Lite — plantilla Spec-Driven con IA

Metodología mínima para trabajar con agentes de IA a partir de una spec acordada. Lee `METODOLOGIA.md` (una página). Requiere Python 3.8 o superior (solo librería estándar).

## Instalar y actualizar (recomendado)

El kit trae un instalador/actualizador (`tools/sgp_kit.py`) que deja una copia **actualizable**,
no una copia muerta: guarda en el proyecto `.sgp-kit.json` (versión + hashes) y distingue entre
archivos gestionados por el kit y archivos tuyos.

```bash
# Instalar (desde la raíz de TU proyecto). <kit> = ruta a esta carpeta, p. ej. ../ia-sdlc/kit
python <kit>/tools/sgp_kit.py init   --source <kit> --dest .
# Ver qué cambió el kit desde tu última versión
python <kit>/tools/sgp_kit.py status --source <kit> --dest .
# Traer actualizaciones respetando tus ediciones (respalda conflictos en .sgp-kit-backup/)
python <kit>/tools/sgp_kit.py update --source <kit> --dest .
```

- **managed** (se actualizan): `tools/*`, `skills/`, `prompts.md`, `METODOLOGIA.md` y las plantillas en blanco.
- **seeded** (solo se copian si faltan; nunca se pisan): `docs/constitution.md`, `AGENTS.md`, `CLAUDE.md`, `sgp.yaml`.
- `sgp-kit.manifest` (en el kit) declara qué es cada cosa.

Si preferís el método manual (sin updates), copiá a mano la misma lista de `sgp-kit.manifest`.

## Instalar en un repo (5 pasos)

1. Copia al repo (o usa `sgp_kit.py init`, arriba): `docs/`, `specs/`, `changes/`, `tools/`, `skills/`, `AGENTS.md`, `CLAUDE.md`, `sgp.yaml`, `prompts.md`, `METODOLOGIA.md`.
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

## Probar el kit

```bash
python -m unittest tools/test_sgp_check.py -v     # pruebas del verificador
python -m unittest tools/test_sgp_kit.py -v       # pruebas del instalador/actualizador
```

## Contenido

```text
VERSION  sgp-kit.manifest
docs/constitution.md   docs/adr/_plantilla.md   specs/_plantilla-dominio/spec.md
changes/_plantilla.md  AGENTS.md  CLAUDE.md  sgp.yaml  prompts.md  METODOLOGIA.md  ADOPCION.md
tools/sgp_check.py  tools/pre-commit  tools/sync_skills.py  tools/test_sgp_check.py
tools/sgp_kit.py  tools/test_sgp_kit.py
skills/sgp-especificar  skills/sgp-qa-spec  skills/sgp-planificar-cambio  skills/sgp-ejecutar-tarea  skills/sgp-validar-cerrar
```
