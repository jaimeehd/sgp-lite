#!/usr/bin/env python3
"""sync_skills.py — instala las skills de SGP (formato agentskills.io) en el directorio
de tu agente. Fuente única: skills/*/SKILL.md. No genera contenido nuevo: solo copia.

Protección por hash (mismo criterio que sgp_kit.py) para no clavar las copias en la
primera instalación:
  - skill que falta en el destino          -> se instala;
  - skill intacta desde la última copia    -> se actualiza sola, sin --force;
  - skill editada a mano (o sin registro)  -> se conserva y se avisa; --force la pisa.
El registro de lo instalado vive en <destino>/.sgp-sync-state.json.

Uso:
    python tools/sync_skills.py --agent claude-code
    python tools/sync_skills.py --agent copilot --scope personal
    python tools/sync_skills.py --list
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

# Rutas conocidas (repo = dentro del proyecto; personal = para todos tus proyectos).
# Consulta la documentación vigente del agente antes de asumir que una ruta sigue siendo correcta.
DESTINOS = {
    "claude-code": {"repo": ".claude/skills", "personal": "~/.claude/skills"},
    "copilot":     {"repo": ".github/skills", "personal": "~/.copilot/skills"},
    "codex":       {"repo": ".agents/skills", "personal": "~/.codex/skills"},
    "cursor":      {"repo": ".cursor/skills", "personal": None},
    "opencode":    {"repo": ".agents/skills", "personal": "~/.agents/skills"},  # estándar agentskills.io; opencode lo lee
    "generico":    {"repo": ".agents/skills", "personal": None},  # estándar agentskills.io
}

STATE = ".sgp-sync-state.json"


def tree_hash(d: Path) -> str:
    """Hash de una carpeta entera (ruta relativa + bytes de cada fichero, en orden)."""
    h = hashlib.sha256()
    for f in sorted(p for p in d.rglob("*") if p.is_file()):
        h.update(f.relative_to(d).as_posix().encode("utf-8"))
        h.update(f.read_bytes())
    return h.hexdigest()


def load_state(dest: Path) -> dict:
    try:
        return json.loads((dest / STATE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(dest: Path, state: dict) -> None:
    (dest / STATE).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Instala las skills SGP para un agente")
    ap.add_argument("--agent", choices=list(DESTINOS))
    ap.add_argument("--scope", choices=["repo", "personal"], default="repo")
    ap.add_argument("--root", default=".")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="reemplaza también las skills editadas a mano en el destino")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    src = root / "skills"

    if a.list or not a.agent:
        print("Agentes soportados:", ", ".join(DESTINOS))
        print("Skills disponibles:", ", ".join(p.name for p in sorted(src.iterdir()) if p.is_dir()))
        if not a.agent:
            return 0

    dest_tpl = DESTINOS[a.agent][a.scope]
    if not dest_tpl:
        print(f"'{a.agent}' no tiene ruta conocida para scope '{a.scope}'. Instálalo a mano siguiendo su documentación.")
        return 1
    dest = (Path(dest_tpl).expanduser() if dest_tpl.startswith("~") else root / dest_tpl)
    dest.mkdir(parents=True, exist_ok=True)
    state = load_state(dest)
    installed = updated = up_to_date = protected = 0
    for skill_dir in sorted(p for p in src.iterdir() if p.is_dir()):
        target = dest / skill_dir.name
        src_hash = tree_hash(skill_dir)
        if not target.exists():
            shutil.copytree(skill_dir, target)
            state[skill_dir.name] = src_hash
            installed += 1
            print(f"-> {target}")
            continue
        cur_hash = tree_hash(target)
        if cur_hash == src_hash:
            state[skill_dir.name] = src_hash
            up_to_date += 1
            print(f"  [al día] {skill_dir.name}")
        elif a.force or state.get(skill_dir.name) == cur_hash:
            # --force, o copia intacta desde la última instalación (la fuente avanzó sola).
            shutil.rmtree(target)
            shutil.copytree(skill_dir, target)
            state[skill_dir.name] = src_hash
            updated += 1
            causa = "forzada" if a.force else "intacta, se actualiza sola"
            print(f"  [actualizada] {skill_dir.name} ({causa}) -> {target}")
        else:
            # Editada a mano o sin registro: no se pisa sin orden expresa.
            protected += 1
            print(f"  [editada a mano] {target} (se conserva; usa --force para reemplazar)")
    save_state(dest, state)
    print(f"\n{installed} instalada(s), {updated} actualizada(s), {up_to_date} al día, {protected} protegida(s) "
          f"para {a.agent} ({a.scope}).")
    print("Si tu agente no aparece en la lista: cualquier herramienta compatible con el estándar")
    print("agentskills.io puede leer skills/*/SKILL.md directamente; solo copia la carpeta a su ruta de skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
