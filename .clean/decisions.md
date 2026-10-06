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
