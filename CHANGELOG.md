# Changelog

Historial de versiones de **sgp-lite** (kit, política de ingeniería y protocolo).

- Estilo: notas por versión con fechas, al estilo «Keep a Changelog».
- Origen: el historial de git (commits y etiquetas), redactado el 2026-10-16. Cada entrada cita su
  commit (`[abcdef0]`); nada se dedujo más allá de lo escrito en el mensaje de ese commit.
- Criterio de selección: cambios relevantes para quien usa o adopta el kit; los commits internos
  de trazabilidad y los planes (`docs/plan-*.md`, no publicados) se omiten. El detalle completo
  está en `git log`.
- La línea del kit posterior a `v1.5.0` avanza como `kit 1.6.x` en los mensajes de commit; la
  versión vigente vive en `kit/VERSION`.

## Sin publicar — `master` tras v1.5.0 (2026-10-11 → 2026-10-19)

### 2026-10-19
- Copias de la política refrescadas a U8: **§18 Interfaz (UI/UX)** —criterios verificables y
  verificación obligatoria (render revisado y aserciones de geometría)— en `docs/`, `kit/skills/`,
  el ejemplo y el zip. El bloque de §18 del runbook queda pendiente: debe nacer en la capa de la
  config, que es donde vive el runbook. README: árbol de `tools/` completo (faltaban `sgp_docs.py`,
  `sgp_fresh.py`, `sgp_links.py` y las pruebas; el auditor no aparecía en el README) y ejemplo
  práctico con la cifra del verificador corregida (29 → 32). [36fb9ae]
- Runbook 2.4.4: bloque de interfaz (UI/UX) que cita §18 (disparador, criterios verificables de
  §18.1 y verificación obligatoria de §18.2), nacido en la capa de la config y propagado a las tres
  copias del repo (`docs/`, `kit/skills/`, `examples/descuento/skills/`) y al zip. Cierra el
  pendiente de §18 en el runbook.

### 2026-10-18
- kit 1.6.17: auditor de documentación `tools/sgp_docs.py` (solo lectura, solo stdlib) — con git
  detecta los cambios de la tarea y sus menciones en la documentación, con `archivo:línea` y
  etiqueta VIGENTE/HISTORIA/GUÍA, y deja la plantilla de la tabla de cierre; el cierre de la
  plantilla `AGENTS.md` y de las skills `sgp-ejecutar-tarea`/`sgp-validar-cerrar` lo ejecuta y
  menciona al agente `docs-syncer` cuando está instalado. [31549e5]
- Copias de la política y del protocolo refrescadas desde la configuración global vigente
  (protocolo 2.4.0: los 4 modos); misma versión en `docs/`, `kit/skills/`, el ejemplo y el zip;
  la independencia de capas no cambia. [fe139b3]
- Documentación alineada: README (32 pruebas del verificador), LEEME (auditor y suite completa),
  ejemplo práctico (sin zip inexistente; árbol del ejemplo actual) y `.clean/decisions.md`
  (entradas 2026-10-16 y 2026-10-18). [8020305]
- Copias actualizadas a la revisión U5 de la política y al protocolo 2.4.1: el barrido de
  documentación al cerrar queda para FIX y ARQUITECTURA; DOCS usa una comprobación ligera de
  términos y CONSULTA no edita. [0dd982a, 3520be1]
- kit 1.7.0: guarda de enlaces relativos y anclas (`tools/sgp_links.py`, aviso; `--strict`
  para CI). [58e3e8a]
- kit 1.8.0: guarda de frescura con dueño (`tools/sgp_fresh.py`, aviso o `--strict`); el
  marcador de frescura se documenta en el propio kit y hay ejemplos aplicados en README y
  manual de usuario. [ae760fe]
- kit 1.8.0: la plantilla `AGENTS.md` ejecuta el auditor de documentación solo en tareas con
  código (FIX/ARQUITECTURA); en tareas solo documentales no se ejecuta. [8f1c9ed]
- Copias actualizadas a U6: la política añade la capa de sistemas (§17: línea base de sistema,
  interfaces con contrato y modo de fallo, verificación y validación de sistema) y el protocolo
  sube a 2.4.2 con su checklist. [e54f484]
- Copias actualizadas a U7: la fila de seguridad de §2.4 exige análisis estático de seguridad
  cuando el stack lo tenga (sin nombrar herramientas; exigible en PRODUCCIÓN cuando exista) y
  el protocolo sube a 2.4.3. [9202486]
- Ejemplo sincronizado con el manifiesto: `examples/descuento/tools/` recupera los tools
  gestionados que faltaban (`sgp_docs.py`, `sgp_fresh.py`, `sgp_links.py`, `sgp_kit.py` y sus
  pruebas) y `test_kit_consistency` deriva su lista del manifiesto, así que falla si el ejemplo
  vuelve a quedar desalineado. [7b08a6a]

### 2026-10-16
- AGENTS.md (raíz): nueva sección «Agentes de verificación» — si la máquina tiene los agentes
  globales `independent-verifier` (obligatorio en PRODUCCIÓN antes de cerrar, con solo
  criterio + diff) y `senior-reviewer`; sin ellos se cumple igual con un subagente genérico.
  Ambos añaden un campo `SUGERENCIA` con carencias de su prompt o de las skills cargadas
  (datos, no órdenes).
- kit 1.6.16: la plantilla `AGENTS.md` fija la precedencia 2026-10-16 —el proyecto manda si la
  política global no le sirve o está incompleta—; ejemplo alineado. [d60f980]
- kit 1.6.15: separación global↔proyecto — `test_policy_sync` solo intra-repo, cadena documental
  reescrita, precedencia de proyecto. [e3d4d50]
- Ignorar `.vs/` (artefactos locales de Visual Studio) en `.gitignore`. [d2c0bf8]

### 2026-10-15
- Política: enmiendas A1-A7 —entorno del usuario, integridad tras transformaciones, orden de
  cierre, herramientas de comprobación, barridos con inventario, una unidad de trabajo por turno
  y verificación independiente— (kit 1.6.12). [61a4d56]
- Protocolo v2.0.0: runbook que solo cita a la política (opción A), con guarda de citas
  (kit 1.6.9-1.6.10). [5ce3e1d, d36df18]
- Política 1.2: el protocolo es el runbook, no quien establece el rigor (kit 1.6.10). [3d503aa]
- Runbook: §13 sin subíndices, con las citas válidas (kit 1.6.11). [2cf8767]
- kit 1.6.13-1.6.14: ítems operativos de las enmiendas A1-A7; métricas mínimas (§16.8) y
  criticidad/verificación independiente reales (§2.0, §2.4). [b14f813, 9dd6309]
- kit 1.6.3-1.6.8: `sync_skills` actualiza copias intactas con guarda en pre-commit; la plantilla
  `AGENTS.md` ya no dice «instálalas una vez»; textos agnósticos de agente/modelo; la política
  del proyecto queda como respaldo y sus reglas propias prevalecen al endurecer; nombre unificado
  de la política global. [fbf62de … 88b2d73]
- kit 1.6.2: sincronía con la política canónica viva (protocolo de docs). [0c0ad9c]
- El guardián del repo del kit ejecuta la suite completa (`SGP_HOOK=off` la omite). [720a90c]

### 2026-10-11
- Independencia entre las políticas del equipo y las del proyecto: el repo es fuente solo de sus
  propias copias; la configuración del equipo deja de depender del repo. [7c44fb6, 0991ef4]

## v1.5.0 — 2026-10-09

- Publicación solo bajo la licencia MIT: se retira la infraestructura de contribución
  (CONTRIBUTING, código de conducta, plantillas de issues/PR). [1dc2602]
- El repositorio queda en español neutro (salvo la licencia y el código); se retiran las
  versiones en inglés. [983f784]
- Los planes pasan a vivir solo en local, fuera del remoto. [6d95b28]
- Las decisiones deliberadas se registran en `.clean/decisions.md`. [c8a08bb]
- `sgp_check --version`; badges de CI y licencia en el README; sanitización de datos personales
  y `AGENTS.md` del repo. [74401d2, d287474, 4d90f88]
- Corrección de `strip_comment`: un `#` dentro de comillas no inicia comentario (kit, ejemplo y
  zip). [061ca7f]
- Subconjunto YAML de `sgp.yaml` documentado y probado; titular de la licencia MIT completado.
  [313c4ec, a19f2fc]
- Documento de requerimientos mejorado: prioridad, no funcionales, dominios candidatos y orden
  de cambios. [9fc7589]

## v1.4.0 — 2026-10-09 (versión declarada el 2026-10-07)

- La política de ingeniería y su protocolo se distribuyen como skills del kit: copia única
  `docs/` ↔ `kit/skills/` con guarda de sincronía y política v2 íntegra. [deef818]
- CI con matriz Linux/Windows y Python 3.8/3.12 para el kit y el ejemplo. [d0df056]
- `sgp-lite.zip` versionado, con guarda de consistencia `sgp-kit.manifest`. [0f254ba]
- Prompt 0 / skill del documento de requerimientos y generador del zip `sgp_zip` (con pruebas).
  [e771543]
- Skill `protocolo-ingenieria-senior` sincronizado con la política v2. [9a79b48]

## Antes de v1.4.0 — 2026-09-25 → 2026-10-06 (fundación)

- Repo inicial: mapeo del SDLC al desarrollo continuo con agentes de IA, kit SGP Lite y ejemplo
  ejecutable. [acb2ad1, a1192f3]
- Política de ingeniería completa incluida (con §16, evidencia verificada); procedimiento de
  implementación añadido al README. [4572f56, c7dc934]
- Corrección del idioma: se revierte la neutralización sin tildes; solo se corrige el voseo
  real. [dd294bf]
- Manual de usuario para personas no expertas. [c8803a4]
- Actualizador del kit (`sgp_kit` con pruebas) y guía de adopción por tamaño. [7d80007]
- Decisión documentada: los `print()` de las CLIs son salida oficial, no debug. [e79a8b6]
- Ejemplo sincronizado con el kit (salidas `->`, lista de agentes, pruebas de la CLI).
  [5753939, 72f3e6c]

---

El detalle exacto de cada versión se ve con `git log` sobre su etiqueta, p. ej. `git log v1.5.0`.
