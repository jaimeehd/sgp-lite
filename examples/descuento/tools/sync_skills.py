#!/usr/bin/env python3
"""sync_skills.py — instala las skills de SGP (formato agentskills.io) en el directorio
de tu agente. Fuente única: skills/*/SKILL.md. No genera contenido nuevo: solo copia.

Uso:
    python tools/sync_skills.py --agent claude-code
    python tools/sync_skills.py --agent copilot --scope personal
    python tools/sync_skills.py --list
"""
import argparse
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


def main():
    ap = argparse.ArgumentParser(description="Instala las skills SGP para un agente")
    ap.add_argument("--agent", choices=list(DESTINOS))
    ap.add_argument("--scope", choices=["repo", "personal"], default="repo")
    ap.add_argument("--root", default=".")
    ap.add_argument("--list", action="store_true")
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
    for skill_dir in sorted(p for p in src.iterdir() if p.is_dir()):
        target = dest / skill_dir.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(skill_dir, target)
        print(f"-> {target}")
    print(f"\n{len(list(src.iterdir()))} skill(s) instaladas para {a.agent} ({a.scope}).")
    print("Si tu agente no aparece en la lista: cualquier herramienta compatible con el estándar")
    print("agentskills.io puede leer skills/*/SKILL.md directamente; solo copia la carpeta a su ruta de skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
