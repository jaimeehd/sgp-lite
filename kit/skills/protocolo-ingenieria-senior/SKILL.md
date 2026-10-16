---
name: protocolo-ingenieria-senior
description: |
  Runbook operativo que acompaña a la política de ingeniería `system-engineering-policy`.
  NO define reglas: todas viven en la política, que es normativa; aquí solo está el orden de
  trabajo, las listas de comprobación por modo y ejemplos de las plantillas, cada punto con la
  cita de la sección que manda. Úsalo al ejecutar cualquier tarea de ingeniería (bug fix,
  refactor, función o módulo nuevo, elección de stack/patrón, propuesta de arquitectura).
  Si algo aquí contradice la política, manda la política (§0.2).
metadata:
  version: 2.2.0
  category: engineering-process
---

# Protocolo de ingeniería senior — runbook operativo

> **Este documento no define reglas.** Las reglas están en la política (`system-engineering-policy`),
> que es normativa; aquí está el orden de trabajo, las listas de comprobación y algún ejemplo de las
> plantillas. Ante cualquier discrepancia, manda la política (§0.2 de la política). Los bloques y
> tablas completas se copian de la política, no se reescriben aquí.

## Arranque (cualquier modo)
- [ ] Política cargada (§1.2).
- [ ] PROYECTO ACTIVO con ruta absoluta, o CONSULTA temática sin archivos (§14.1, §14.5).
- [ ] Restricciones de proyecto leídas una vez: `AGENTS.md`/`README`/`CONTRIBUTING` y `.clean/` si existe (§9.5).
      Si declara restricción de alcance total → bloque `RESTRICCIÓN DE PROYECTO ENCONTRADA` (§9.5).
- [ ] MODO declarado (§1.1) · CRITICIDAD si es FIX/DOCS (§2.0) · REQUISITO con criterio de aceptación si es FIX (§2.0.1).
- [ ] Alcance del turno: si el pedido trae varias unidades, listarlas y ejecutar **una** (§13).

## MODO FIX (§2)
- [ ] REQUISITO: pedido + criterio de aceptación observable (§2.0.1).
- [ ] EVIDENCIA: una fila por archivo, con lectura real, "¿completo?" y caducidad (§2.1).
- [ ] DIAGNÓSTICO con confianza (HECHO/INFERENCIA/HIPÓTESIS); si no es HECHO, agotar la verificación barata antes de implementar (§2.2).
- [ ] Decisiones deliberadas buscadas antes de tocar nada (§9.2) → bloque si aparece.
- [ ] SOLUCIÓN PROPUESTA / ALCANCE / FUERA DE ALCANCE (§2.3); lo detectado fuera se reporta, no se ejecuta (§2.3.1).
- [ ] Si el cambio se aplica con scripts, regex o sustituciones masivas: copia o repo limpio, inventario antes/después y **releer el fichero** — el resto del contenido no puede cambiar (§2.4).
- [ ] VERIFICACIÓN: compilación o chequeo estático + **al menos una fila que pruebe comportamiento** + fila de docs de proyecto (§2.4).
- [ ] Declaración obligatoria: `verificación independiente: EJECUTADA (subagente <id> con solo REQUISITO + diff | método distinto: <comando>) | NO EJECUTADA (motivo)` en PRODUCCIÓN; **NO EJECUTADA ⇒ INCOMPLETE**; en blanco = INCOMPLETE (§2.0, §2.4).
- [ ] En PRODUCCIÓN: **suite completa si existe** (no un solo test o smoke) + **vuelta atrás declarada** (§11); la independencia no es omisible (§2.0).
- [ ] `CONSIDERADO Y DESCARTADO` explícito + ESTADO (§2.4).

## MODO ARQUITECTURA (§4)
- [ ] CONTEXTO DEL PROYECTO completo; la vida útil esperada gobierna cuánta arquitectura se justifica (§4.1).
- [ ] DECISIONES DE ARQUITECTURA: una fila por patrón/capa añadido, con alternativa y costo aceptado (§4.2). YAGNI/KISS por defecto.
- [ ] ESTRUCTURA + CONTRATOS entre módulos (§4.3).
- [ ] Línea base del §4.4 (incluye la doc mínima: README con objetivo/build/test, CHANGELOG y AGENTS.md con los comandos).
- [ ] VERIFICACIÓN DE DISEÑO (§4.5) y **esperar confirmación** antes de implementar, salvo autorización en el mismo pedido.
- [ ] Al implementar, cada archivo pasa a las reglas de FIX (§2).

## Transversal

### Antes de cada commit (§2.4)
- [ ] Regenerar los artefactos derivados (paquetes, índices, zips) → **suite completa** → commit.
- [ ] **Nunca se commitea con una prueba en rojo**; si falla, se corrige antes.

### Entorno del usuario (§11)
- [ ] Instalar, actualizar o desinstalar herramientas; borrar o mover ficheros fuera del PROYECTO ACTIVO; tocar variables de entorno o el PATH: **confirmación explícita previa** y vuelta atrás declarada.
- [ ] "Comprobar si hay versión nueva" **no** autoriza a actualizar. El resultado se comprueba con el comando real.

### Decisiones deliberadas (§9)
- [ ] Antes de proponer cambiar, reemplazar o "modernizar": buscar razón documentada (§9.1-§9.2) → bloque `DECISIÓN DELIBERADA ENCONTRADA`.
- [ ] Si parece obsoleta: se propone con la razón original a la vista, nunca se ejecuta (§9.3).
- [ ] Restricción de alcance total (no de un elemento): una lectura por proyecto, activa el resto de la sesión (§9.5).

### Sesiones concurrentes (§12)
- [ ] `git status` (o tickets pendientes) antes de la evidencia en CRITICIDAD PRODUCCIÓN o con aprobación por tickets; repetir antes de cada paso si es multi-paso de PRODUCCIÓN (§12).
- [ ] Sin repo git: declararlo y preguntar si se procede sin el control (§12).

### Tareas multi-paso (§13)
- [ ] Lista con estados al inicio; `EN CURSO`/`HECHO`/`BLOQUEADO` en tiempo real, sin agrupar al final (§13).
- [ ] Cada paso conserva las reglas de su modo: la lista es visibilidad, no un atajo (§13).

### Rigor en toda respuesta (§16)
- [ ] Afirmaciones factuales con evidencia (§16.1) · negaciones absolutas con el método usado (§16.2) · "conté" frente a "estimé" (§16.3) · auto-revisión antes de enviar (§16.4).
- [ ] Comprobaciones: solo métodos ya probados; una nueva se prueba con un caso conocido, declara qué NO comprueba y se guarda como prueba del repositorio; si contradice al método oficial, **gana el oficial** (§16.6).
- [ ] Barridos (renombrados, movimientos): inventario antes y después, cierre a 0 (§16.7).
- [ ] Mejoras numéricas con cifra antes/después, método y unidad; indicadores de cierre si es PRODUCCIÓN o proceso (§16.8).
- [ ] Análisis sin tocar código = mismo rigor (§16.5).
- [ ] Docs de proyecto: inventario con `git diff --name-only HEAD`, grep de los términos cambiados en toda la doc y tabla `| Archivo | Sección | Qué cambió | Cómo lo verificaste |` (§16.5).

### Cierre (§15.4)
- [ ] La respuesta termina con `FIN DE PROCESO` cuando cierra una tarea.

## Ejemplos (solo ilustrativos)
Filas de ejemplo para la tabla de decisiones de §4.2:

| Decisión | Alternativas consideradas | Por qué esta | Costo que acepto |
|---|---|---|---|
| Capa de repositorio sobre el ORM | acceso directo desde los servicios | aísla el dominio del proveedor de datos | una capa más de indirección; +N archivos |
| Bus de eventos interno frente a llamadas directas | llamadas directas síncronas | desacopla módulos que evolucionan a ritmos distintos | trazabilidad de eventos; logging adicional |
