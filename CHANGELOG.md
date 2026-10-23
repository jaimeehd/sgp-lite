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

## Sin publicar — `master` tras v1.5.0 (2026-10-11 → 2026-10-22)

### 2026-10-22
- kit 1.9.0: **puerta de revisión** (`tools/sgp_review.py`, con `test_sgp_review.py`): ninguna tarea
  se cierra sin su ronda registrada. El commit que marca una tarea `[x]` debe traer, en
  `docs/LOG-PROCESO.md`, una fila de tipo «revisión» **cerrada** que cite la tarea y el cambio y
  mencione a un subagente; desde `revision.corte_fuente` (2026-10-23 por defecto) la fila exige
  además `subagente <id>` (el nombre del papel solo era auto-atestación). Las filas malformadas o
  con fecha inválida **fallan y dicen cuál es** (no se ignoran en silencio), los pipes del texto se
  escriben escapados (`\|`) y una fila `pendiente` no cuenta. Diseño aprendido del piloto aomarket:
  si el proyecto no tiene el log, la puerta **se declara inactiva con aviso** (no finge verde) y se
  activa al crear el archivo; un log presente pero sin versionar también falla (la confirmación debe
  viajar con el commit). Exenciones heredadas en `tools/revisiones-baseline.txt` (opcional). Cableada
  en `tools/pre-commit`; configuración opcional en `sgp.yaml` (`revision.log_proceso`,
  `revision.corte_fuente`, `revision.subagentes`). Las skills `sgp-ejecutar-tarea` y
  `sgp-validar-cerrar`, `prompts.md` y la plantilla `AGENTS.md` dejan de ordenar marcar `[x]` /
  `estado: hecho` sin esa ronda: un cierre sin registro apagaba los sensores del verificador.
  Propagado al ejemplo y al zip.
- kit 1.10.0: **cierre duro de `hecho`, ratchet real y sello de commit**. (1) `sgp_check.py` deja de
  saltarse `estado: hecho`: exige la consistencia de cierre (sección «Criterios de finalización»
  con al menos un criterio —`-`, `*` o `+`—, ninguno sin marcar, tareas cerradas, «Hecho cuando:»
  en todas y sin `[POR-ACLARAR]`), sin los cruces externos con `specs/` que pueden derivar tras
  cerrado el cambio; `cancelado` sigue saltándose. Ese path no tenía ni una prueba. (2) `--ratchet`
  deja de ser verde silencioso: `rutas.ratchet` (varias rutas relativas por coma, admite comodines;
  por defecto `rutas.tests`, por compatibilidad) y, si ninguna ruta vigilada existe, **avisa y
  explica cómo configurarlo** (causa raíz documentada en el piloto: «el `--ratchet` del kit
  vigilaba la carpeta `tests/` inexistente»). El universo vigilado es índice ∪ árbol de `HEAD`
  (borrar toda la suite ya no se escapa) y un renombrado que saque una prueba de la ruta vigilada,
  o que la renombre debilitándola, cuenta como retirada; sin `git`, la guarda **falla cerrado**
  (no verificado no es verde). (3) Nuevo hook `tools/commit-msg` (flag `--commit-msg FICHERO`):
  falla cerrado sin fichero de mensaje, trabaja sobre el mensaje limpio (ignora las líneas de
  comentario y la tijera de `git commit -v`, y escribe el sello antes de la tijera), exige asunto
  con convención (`tipo[alcance]: asunto`) y un solo `CHG-NNN` por commit, y **sella** el
  resultado de las tres puertas —estructura validada sobre el **índice**, no sobre el árbol— al
  final del mensaje (`Gate: sgp_check N err | sgp_review OK|INACTIVA | ratchet N
  bloq|sin-tests|omitido`); merge, revert, fixup y squash sin sellar; sello idempotente. (4) CI:
  job `guardas` con `sgp_links --strict` y `sgp_fresh --max-days 180 --require README.md
  --strict`. El repo del kit gana su `sgp.yaml` propio (el ratchet vigila `kit/tools/test_*.py`)
  e instala el hook. 34 pruebas nuevas (66 en `test_sgp_check.py`). Propagado al ejemplo y al zip.
  Al actualizar desde ≤1.9.0: revisa los cambios `hecho` históricos (si les falta la sección de
  criterios o tienen criterios abiertos, marca `[x]` lo que ya se cumplió; no reabras un cambio
  histórico solo por esto).
- kit 1.10.1: **robustez de los hooks y del arnés**. El hook `tools/commit-msg` comprueba que el
  verificador instalado soporte `--commit-msg` y, si es viejo, falla cerrado con «actualiza
  tools/ del kit» (antes: `unrecognized arguments`). El ratchet cuenta los **binarios vigilados**
  (`--numstat` da `-\t-`): modificar o borrar uno existente bloquea, darlo de alta no. El arnés de
  pruebas fija salida UTF-8 y decodifica UTF-8: con `PYTHONIOENCODING` exportado la suite daba
  falsos rojos por mojibake y ahora pasa en ambos entornos. `SECURITY.md` declara que el sello es
  **evidencia, no control** (`git commit --no-verify` omite los hooks) y el `--help` de
  `--commit-msg` aclara que es uso interno del hook. 3 pruebas nuevas (69 en
  `test_sgp_check.py`). Propagado al ejemplo y al zip.
- kit 1.11.0: **política de commit configurable y actualización sin sorpresas**. `sgp.yaml` gana
  `commit.max_lineas` (0 = sin tope), `commit.autorizacion` (token de la línea
  «…: autorizado por <quien> · <motivo>») y `commit.sello` (campos: `sgp_check`, `revision`,
  `ratchet`, `tamano`, `ficheros`; por defecto, los tres clásicos). El hook `commit-msg` mide el
  staged (`--numstat`, binarios como 1 línea), rechaza los commits que superan el tope sin
  autorización y compone el sello con los campos configurados; un campo desconocido falla cerrado.
  `sgp_kit.py status` ya no disfraza de «actualización disponible» un archivo gestionado que existe
  y no consta en el registro: lo reporta como conflicto (lo que `update` hará: respaldo +
  sustitución). Así un proyecto conserva su política de commits (tope + autorización + sello) sin
  bifurcar ficheros gestionados. 8 pruebas nuevas (75 en `test_sgp_check.py`, 10 en
  `test_sgp_kit.py`). Propagado al ejemplo y al zip.
- kit 1.12.0: **sensores que faltaban: sufijos de tarea, hash de la revisión y criterio de
  `specs/`**. (1) `TASK_RE` acepta sufijos (`T006a`): antes el verificador las leía como texto y no
  exigía su «Hecho cuando» ni contaban para cobertura ni para el cierre (el parser de `sgp_review`
  ya los aceptaba; ahora ambos coinciden). (2) La fila de revisión cita el hash del diff sustantivo
  (`diff: <hash>`, con `sgp_check.py --diff-hash`, que excluye `changes/` y el log): desde
  `revision.corte_fuente` la puerta lo exige y lo compara, así una revisión de una versión anterior
  ya no vale para el commit. (3) `estado: revision` con requisitos exige un criterio que cubra
  `specs/`: el cierre no puede ignorar la spec (comprobación de presencia; el contenido sigue siendo
  del humano). (4) Se retira `max_iteraciones_por_tarea`: era una regla declarada sin sensor y pasa
  a ser una guía de trabajo sin clave de configuración. 6 pruebas nuevas (79 en
  `test_sgp_check.py`, 23 en `test_sgp_review.py`). Propagado al ejemplo y al zip.

### 2026-10-20
- kit 1.8.1: la guarda de enlaces `sgp_links.py` revisa **el universo que git considera del
  proyecto** (`git ls-files`, incluidos los no seguidos y excluyendo lo que marca el `.gitignore`),
  como ya hacía el auditor `sgp_docs.py`; sin git, sigue recorriendo el árbol. Se descartan además
  los directorios de `DIRS_IGNORADOS` (`venv` incluido). Con esto dejan de aparecer avisos sobre
  ficheros de terceros en `venv/` y sobre ficheros locales no versionados. En la misma versión,
  `test_sgp_links.py` recuprea el bloque `unittest.main()` que le faltaba: el hook del repo ejecuta
  cada prueba del kit por separado y ese comando salía con 0 sin correr nada (falso verde). Pruebas
  nuevas: lo ignorado por git no se revisa, lo no seguido sí, `venv/` se descarta y sin git se
  recorre el árbol. `ls-files` se invoca con `-z`: sin él, git entrecomilla en octal las rutas con
  caracteres no ASCII y esos ficheros versionados se salían del universo en silencio, sin detectar
  sus enlaces rotos (caso cubierto por una prueba con `Índice.md` y `carpeta ñ/guía.md`, que falla
  con la variante sin `-z`). La exclusión de directorios ignorados se evalúa sobre la ruta
  **relativa** al proyecto revisado: antes se comparaba con la ruta absoluta y un proyecto que
  viviera bajo un directorio llamado `venv` (por ejemplo `.../venv/mi-proyecto`) dejo de revisarse
  entero. 18 pruebas en el fichero. Propagado al ejemplo y al zip.

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
