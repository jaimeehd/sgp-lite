# Decisiones deliberadas — ia-sdlc

Registro de decisiones que no se ven en el código. Formato: fecha, contexto,
decisión, razones (sin reinterpretar) y consecuencias. Nada aquí se toca "de paso".

## 2026-10-06 — Los `print()` de las CLIs del kit son salida oficial, no debug

- **Contexto**: el hook `clean-code` (`scan_repo.py`, regla `^\s*print\s*\(`) marca
  "debug output left in production code" en `kit/tools/sgp_check.py` (14),
  `kit/tools/sgp_kit.py` (12) y `kit/tools/sync_skills.py` (7).
- **Decisión**: no se modifica ningún `print()` por este hallazgo.
- **Razones**:
  1. Esos `print()` son el contrato de salida de las CLIs: informe `ERROR/AVISO`,
     progreso `->`, tablas de trazabilidad y confirmaciones de instalación.
  2. Los tests afirman sobre stdout capturado (`EXP-001`, `sin pruebas`); con
     `logging.debug` la ejecución normal no mostraría nada y el comportamiento
     observable dejaría de probarse.
  3. Scripts de un archivo solo-stdlib, diseñados para copiarse: sin framework
     de logging a propósito (YAGNI).
  4. El propio scanner se declara *advisory* ("measurements, not verdicts";
     "fix only if it blocks, creates real risk, or your change introduced it")
     — ninguna aplica: no bloquea, no hay riesgo, y los prints preexisten.
- **Consecuencias**: futuros commits ignoran ese aviso para `kit/tools/*.py`
  (y sus copias en `examples/`). Revisar solo si cambia el contrato de salida.

## 2026-10-09 — Fuente única de la política y su skill; junctions en los roots de agente

- **Contexto**: copias divergentes del skill `protocolo-ingenieria-senior` y de la política en
  varios roots (`~/.claude/skills`, `~/.config/opencode/skills`, tres repos con el kit, el plugin
  de Claude Desktop) y variantes viejas ("[redactado]"/`CLAUDE.md`, numeración previa a la v2).
- **Decisión**: el repo es la **fuente única**. `kit/skills/{protocolo-ingenieria-senior,
  system-engineering-policy}` se mantiene idéntico a `docs/…SKILL.md` por `test_policy_sync`; los
  roots personales `~/.claude/skills/…` y `~/.config/opencode/skills/protocolo-ingenieria-senior`
  son **junctions** (mklink /J) a `kit/skills/…`. Se eliminó el stray
  `~/.config/opencode/protocolo-ingenieria-senior/` (ningún loader lo leía).
- **Razones**: elimina la duplicación que produjo el desfase (un subconjunto copiado a mano, sin
  sincronía); un cambio commiteado en el repo llega solo a los roots, sin copiar.
- **Consecuencias**:
  1. Si el repo se mueve de `<ruta-del-repo>`, los junctions se rompen: hay que recrearlos.
  2. Cuando cambie `~/.config/opencode/system_prompt.md`: reescribir
     `docs/system-engineering-policy.SKILL.md` (frontmatter actual + cuerpo íntegro), copiar a
     `kit/skills/system-engineering-policy/SKILL.md` y correr los tests del kit; los roots lo ven
     por junction.
  3. Los repos que adoptaron el kit se actualizan con `sgp_kit update` + `sync_skills.py`.
  4. El plugin de Claude Desktop se reconstruye desde su origen: la copia local actualizada no
     garantiza persistencia.
  5. La guarda `kit/tools/test_policy_sync.py` cubre `docs/` ↔ `kit/skills/` (falla si divergen).
