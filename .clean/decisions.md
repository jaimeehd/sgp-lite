# Decisiones deliberadas — sgp-lite

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

## 2026-10-09 — Fuente única de la política y su skill

- **Contexto**: había copias divergentes del skill `protocolo-ingenieria-senior` y de la política en
  varios directorios de skills y en proyectos que adoptaron el kit, algunas con numeración previa
  a la v2.
- **Decisión**: el repo es la **fuente única**. `kit/skills/{protocolo-ingenieria-senior,
  system-engineering-policy}` se mantiene idéntico a `docs/…SKILL.md` por `test_policy_sync`; las
  copias desplegadas en los directorios de skills del agente se sincronizan desde el repo (copia o
  enlace). Se eliminó una copia suelta que ningún cargador leía.
- **Razones**: elimina la duplicación que produjo el desfase (un subconjunto copiado a mano, sin
  sincronía); un cambio commiteado en el repo llega solo a los roots, sin copiar.
- **Consecuencias**:
  1. Si el repo cambia de ubicación, los enlaces (si se usaron) se recrean.
  2. Cuando cambie la política de origen: reescribir `docs/system-engineering-policy.SKILL.md`,
     copiar a `kit/skills/system-engineering-policy/SKILL.md` y correr los tests del kit.
  3. Los repos que adoptaron el kit se actualizan con `sgp_kit update` + `sync_skills.py`.
  4. La guarda `kit/tools/test_policy_sync.py` cubre `docs/` ↔ `kit/skills/` (falla si divergen).

- **Estado (2026-10-11)**: superada en lo relativo a las copias desplegadas por «Independencia entre las políticas del equipo y las del proyecto». La cadena interna (`docs/` → `kit/skills/` → `examples/descuento/skills/` → `sgp-lite.zip`) sigue vigente.

## 2026-10-09 — Publicación: solo bajo la licencia, sin canal de contribución

- **Contexto**: se publica el repositorio en https://github.com/jaimeehd/sgp-lite
  (nombre `sgp-lite`, rama `master`, tag `v1.4.0`).
- **Decisión**:
  1. Licencia MIT con titular `Copyright (c) 2026 the sgp-lite authors`.
  2. El repositorio se publica **solo bajo la licencia**: no se aceptan contribuciones. Se retiran
     `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/*` y
     `.github/pull_request_template.md`, y las secciones "Contribuir"/"Contributing".
  3. Se conservan `SECURITY.md` (canal privado de reporte de seguridad) y el workflow de CI
     (`.github/workflows/ci.yml`, disparado por `pull_request`).
- **Razones**: decisión del autor; el repositorio no busca contribuciones externas.
- **Consecuencias**: no se añaden plantillas de issue/PR ni guías de contribución; los cambios
  llegan solo por el autor.

## 2026-10-09 — Todo en español, salvo la licencia y el código

- **Contexto**: la fase P2.4 añadió versiones en inglés (`README.en.md`,
  `docs/manual-usuario.en.md`) con conmutadores de idioma.
- **Decisión**: los documentos del repositorio se escriben **íntegramente en español neutro** (sin
  voseo ni regionalismos). Se eliminan `README.en.md` y `docs/manual-usuario.en.md` y los
  conmutadores de idioma. Se exceptúan el texto de la licencia (MIT, en inglés) y el código
  (comandos, identificadores y fragmentos incluidos en la documentación, que pueden ir en inglés).
  La descripción del frontmatter de la política se traduce y se propaga a las tres copias
  (`docs/`, `kit/skills/` y `examples/`).
- **Razones**: decisión del autor (hablante de español).
- **Consecuencias**: no se agrega documentación en inglés; al cambiar la descripción de la política
  hay que propagarla a `kit/skills/` y `examples/` y regenerar `sgp-lite.zip` (lo exigen
  `test_policy_sync` y `test_kit_consistency`).

## 2026-10-09 — Los planes y pendientes viven solo en local

- **Contexto**: `docs/plan-produccion.md` se había publicado en el remoto.
- **Decisión**: los planes y pendientes no se publican. Se retira del índice
  (`git rm --cached docs/plan-produccion.md`), el archivo queda solo en local y `.gitignore` lo
  excluye con `docs/plan-*.md`. La historia previa del remoto se deja intacta (no se reescribe).
- **Razones**: decisión del autor; los planes son de trabajo interno.
- **Consecuencias**:
  1. Todo plan/pendiente nuevo en `docs/plan-*.md` queda solo en local, nunca en el remoto.
  2. El registro duradero de decisiones es `.clean/decisions.md` (sí publicado), no el plan.
  3. La historia del remoto conserva el plan ya publicado (no se purgó por decisión del autor).

## 2026-10-09 — P2.3 (ciclo de «deltas» y archivo de specs): backlog

- **Contexto**: el plan P2.3 evaluaba un mecanismo tipo OpenSpec (deltas ADDED/MODIFIED/REMOVED +
  archivo) para specs de larga vida.
- **Decisión**: no se ejecuta. Queda documentado como posible implementación a posteriori.
- **Razones**: requiere un diseño propio (contrato nuevo en `specs/`/`changes/`) y aprobación
  explícita; excede el alcance de esta fase.
- **Consecuencias**: se registra aquí porque el plan (`docs/plan-produccion.md`) no se publica; si
  se retoma, se hace en MODO ARQUITECTURA con su propio diseño y ADR.

## 2026-10-09 — El repositorio es la fuente de verdad: se verifica, no se asume

- **Contexto**: la política y sus skills existen en varios lugares además del repositorio
  (directorios de skills de los agentes, el archivo de política inyectado en la configuración local
  de un agente, plugins o cachés sincronizados desde una cuenta y copias en proyectos que adoptaron
  el kit). Una sesión de agente dio por vigente una de esas copias sin comprobarla contra el
  repositorio.
- **Decisión**: a partir de esta fecha, el repositorio es la fuente de verdad de la política, del
  protocolo y de las skills. Cualquier otra ubicación es una copia derivada, nunca un origen: no se
  edita ni se da por vigente sin verificar.
- **Razones**: decisión del autor; evitar que se afirme qué versión rige por el nombre, la ruta o
  la fecha de un archivo.
- **Consecuencias**:
  1. Antes de afirmar qué versión rige en cualquier ubicación, se compara con el repositorio (hash
     o diff, con finales de línea normalizados: el mismo texto puede ser CRLF en Windows y LF en
     otras copias).
  2. Los cambios se hacen solo en el repositorio, en este orden: `docs/` → `kit/skills/` →
     `examples/descuento/skills/` → `sgp-lite.zip`; después se propagan a las copias desplegadas.
  3. Los tests cubren `docs/` ↔ `kit/skills/` (`test_policy_sync`) y `kit/` ↔ `examples/descuento/`
     y el zip (`test_kit_consistency`). Las copias fuera del repositorio (política inyectada en la
     configuración local de un agente, plugins o cachés de una cuenta) no tienen guarda: se
     verifican por hash tras cada cambio.
  4. Ante cualquier discrepancia, prevalece el repositorio sobre la copia desplegada.

- **Estado (2026-10-11)**: superada en lo relativo a subordinar la configuración del equipo al repositorio por «Independencia entre las políticas del equipo y las del proyecto». La verificación por hash y la cadena interna siguen vigentes **dentro del repo**.

## 2026-10-11 — Independencia entre las políticas del equipo y las del proyecto

- **Contexto**: la decisión 2026-10-09 hizo del repositorio la fuente única y trató la política
  inyectada en la configuración local del agente como copia derivada. Eso acopló el equipo al repo
  (skills del agente por enlace a `kit/skills/`) y subordinó la configuración de cada máquina al
  proyecto.
- **Decisión**: se independizan. Las políticas globales del equipo y las copias empaquetadas en el
  repo son **independientes y complementarias**. El repo es fuente **solo de sus propias copias**;
  las copias del repo son para **portabilidad** (si el equipo no tiene las políticas globales, se
  usan las copias incluidas o se sugiere instalarlas). Se rompen los enlaces (junctions) del
  directorio de skills del agente a `kit/skills/`; pasan a ser copias propias.
- **Razones**: decisión del autor; el proyecto debe poder instalarse en equipos sin las políticas
  globales sin depender de la ubicación del repo, y la configuración del equipo no debe quedar atada
  al proyecto.
- **Consecuencias**:
  1. Supera la decisión 2026-10-09 "Fuente única de la política y su skill" y la de "El repositorio
     es la fuente de verdad" en lo que respecta a subordinar la configuración del equipo al repo.
  2. Se conserva la consistencia **interna** del repo: `test_policy_sync` (`docs/` ↔ `kit/skills/`)
     y `test_kit_consistency` (`kit/` ↔ `examples/descuento/` ↔ zip).
  3. Las actualizaciones del proyecto se propagan con `sgp_kit update` + `sync_skills.py`, sin asumir
     autoridad sobre la configuración global del equipo.

## 2026-10-16 — Separación global ↔ proyecto: el repo deja de sincronizarse con la configuración global del equipo

- **Contexto**: la decisión 2026-10-11 independizó las capas, pero la plantilla del kit y varios
  ficheros citaban una cadena de sincronía con la configuración global del equipo. El 2026-10-16
  esa configuración retiró sus pasos de propagación y fijó que cada capa es autónoma, con su
  propia política.
- **Decisión**: el repositorio es fuente solo de sus propias copias (`docs/` → `kit/skills/` →
  `examples/descuento/skills/` → `sgp-lite.zip`). Si la política global del equipo no es la que
  este proyecto requiere, no está completa o estas copias son mejores, rigen las reglas y copias
  del proyecto (citándolas); la global no se impone. Excepción única: la seguridad nunca se
  relaja. `test_policy_sync` deja de comparar con la configuración global y verifica solo la
  sincronía interna del repo.
- **Razones**: el proyecto debe instalarse en equipos sin las políticas globales sin depender de
  su ubicación; la configuración del equipo no debe quedar atada al proyecto, y viceversa.
- **Consecuencias**:
  1. Las referencias a la «precedencia 2026-10-16» de `AGENTS.md`, `kit/AGENTS.md` y el
     `CHANGELOG` apuntan a esta decisión, registrada aquí.
  2. No hay propagación automática desde la configuración global: las copias del repo se
     actualizan por revisión deliberada del autor, con verificación por diff.
  3. La consistencia interna la cubren `test_policy_sync` y `test_kit_consistency`.

## 2026-10-18 — Copias de la política y del protocolo refrescadas desde la global (mantenimiento puntual)

- **Contexto**: las copias del repo eran del 2026-10-15 y la configuración global del equipo había
  seguido evolucionando: 31 líneas de diferencia en la política y 32 en el protocolo (contadas por
  diff, con finales de línea normalizados). Al ser capas independientes no había regla de
  caducidad; la seguridad ya quedaba cubierta por la excepción (la global nunca se relaja), pero
  quien leyera solo el kit veía reglas desactualizadas.
- **Decisión**: el autor decide refrescar las copias del repo con la versión global vigente, por la
  cadena interna (`docs/` → `kit/skills/` → `examples/` → zip), como mantenimiento puntual. No se
  establece sincronía permanente ni automática.
- **Razones**: decisión del autor; los lectores del kit no deben leer reglas desactualizadas.
- **Consecuencias**:
  1. Misma versión en las cuatro copias internas y en el zip, verificada por las guardas.
  2. Futuros refrescos: diff global vs copia → edición → suite del kit → commit.
  3. La independencia de capas no cambia: la global sigue siendo la del equipo.
