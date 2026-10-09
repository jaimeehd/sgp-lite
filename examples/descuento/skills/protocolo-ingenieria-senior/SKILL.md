---
name: protocolo-ingenieria-senior
description: Procedimiento obligatorio antes de leer, diagnosticar, editar o diseñar código, configuración o arquitectura en cualquier repositorio — tabla de evidencia, diagnóstico con nivel de confianza, alcance mínimo, decisiones deliberadas documentadas, verificación con estado DONE/INCOMPLETE/BLOCKED, chequeo de sesiones concurrentes y seguimiento de tareas multi-paso. Complementa a la política de ingeniería (skill `system-engineering-policy`, `system_prompt.md` inyectada, o `docs/system-engineering-policy.SKILL.md` en el repo del kit), que es normativa. Invocar ante cualquier bug fix, refactor, nueva función, módulo o subsistema, elección de stack/patrón, o propuesta de arquitectura.
---

# Protocolo de ingeniería senior — procedimiento completo

> Complemento operativo de la política de ingeniería (`system-engineering-policy`, `system_prompt.md` inyectada, o `docs/system-engineering-policy.SKILL.md` en el repo del kit), que es normativa: identidad, prohibiciones duras, prioridad de decisión, contraste, ambigüedad, confirmación y anclaje de proyecto viven allí. Cubre §2 (FIX), §4 (ARQUITECTURA), §9, §12, §13 y §16 de la política; si esas secciones cambian, revisar este skill. Es la plantilla operativa: qué tabla llenar, qué declarar, en qué orden, antes de tocar cualquier archivo.

---

## 2. MODO FIX

### 2.0 Criticidad declarada (ajusta el rigor, no lo elimina)

Antes de la tabla de evidencia, declara en una línea el radio de impacto del sistema que se toca:

```
CRITICIDAD: PRODUCCIÓN/USUARIO FINAL | HERRAMIENTA INTERNA RECURRENTE | SCRIPT DESCARTABLE
```

No exime ninguna regla de §2 — solo ajusta la profundidad de §2.4 y permite la vía ligera de más abajo: en PRODUCCIÓN/USUARIO FINAL, DONE exige test o smoke test ejecutado; en HERRAMIENTA INTERNA o SCRIPT DESCARTABLE los bloques pueden condensarse, pero la evidencia no se omite. Ante duda genuina, trátalo como PRODUCCIÓN por defecto — el rigor se sube por declaración explícita a la baja, nunca se asume bajo por conveniencia.

**Auditoría independiente en PRODUCCIÓN.** Una tabla de EVIDENCIA bien formateada no prueba que los datos sean correctos. Antes de DONE, la tabla debe verificarse contra el repo real por una sesión o subagente independiente cuando sea factible; si no lo es, se declara `verificación independiente: NO EJECUTADA`.

**Vía ligera.** Si CRITICIDAD es HERRAMIENTA INTERNA o SCRIPT DESCARTABLE, y no hay decisión deliberada (§9) ni casilla marcada del CONTRASTE (§8.1), los bloques DIAGNÓSTICO/SOLUCIÓN/VERIFICACIÓN pueden condensarse en pocas líneas — evidencia y criticidad siguen siendo obligatorias. No aplica a PRODUCCIÓN/USUARIO FINAL.

### 2.1 Regla dura: evidencia antes de editar

No emitas ninguna edición sin haber producido antes, en este turno o en uno visible de la conversación, una tabla de evidencia que cubra cada archivo que la edición toca. Si no la tienes, tu única acción permitida es generar las lecturas necesarias para construirla.

```
EVIDENCIA
| Archivo | Líneas leídas | ¿Completo? | Hallazgo relevante |
|---|---|---|---|
| ruta/a.cs | 1-240 (total 240) | sí | usa X para Y; consumido por Z en línea 88 |
| ruta/b.cs | 1-60 de 400 | NO — parcial | solo el método donde aparece el síntoma |
```

Una fila "¿Completo? NO" no es neutra: obliga a declarar en el diagnóstico qué riesgo introduce esa lectura parcial y por qué se acepta, o a completar la lectura antes de continuar. No se permite ninguna fila basada en convención de nombres o de framework sin lectura real: lo no leído no entra a la tabla y por tanto no puede usarse como hecho.

**Re-lectura obligatoria si el archivo pudo cambiar.** Una fila caduca si (1) una edición sobre ese archivo falla o se aplica parcialmente — relee antes de reintentar; o (2) hubo otra acción entre lectura y edición que pudo modificarlo (otra edición, herramienta externa, autofix). En ambos casos, relee antes de continuar — nunca se asume que "seguía igual".

**Archivos nuevos.** Si el FIX requiere crear un archivo que no existe, no hay líneas que leer en él — su fila de evidencia se marca `(nuevo, no existe)` en vez de un rango de líneas. Eso no exime la tabla: el archivo o los archivos existentes que van a consumir/importar el nuevo sí necesitan su propia fila, con lectura real, igual que cualquier otro — no se mezcla la evidencia de dos archivos distintos en una sola celda.

### 2.2 Diagnóstico

```
DIAGNÓSTICO
- Causa: [una oración, basada solo en filas de la tabla]
- Confianza: HECHO | INFERENCIA | HIPÓTESIS
- Si INFERENCIA o HIPÓTESIS: verificación más barata para subirla a HECHO = [acción concreta]
```

Nunca implementes sobre INFERENCIA o HIPÓTESIS sin intentar antes su verificación más barata. Si no es posible con la evidencia disponible, no se implementa asumiendo que "probablemente" es correcta — se aplica §10: se declara qué falta y se pregunta. Solo HECHO autoriza implementar sin ese paso.

### 2.3 Cambio mínimo

```
SOLUCIÓN PROPUESTA: [1-2 líneas]
ALCANCE: [archivos que cambian, nada más]
FUERA DE ALCANCE (y por qué no se toca): [lista corta]
```

No se refactoriza, limpia ni reorganiza nada fuera del alcance declarado, aunque sea una mejora obvia. Se anota aparte, no se ejecuta. No se elimina un workaround, guard clause o comentario de advertencia sin haber investigado por qué existe (historial, changelog, documentación) y sin citar esa fuente en la tabla de evidencia.

### 2.3.1 Hallazgos fuera de la solicitud (dentro o fuera del proyecto activo)

Si detecto un bug, mejora o problema fuera de lo pedido en este turno — mismo archivo, otro módulo, u otro proyecto — la única acción permitida es informarlo, nunca corregirlo ni "aprovechar para arreglarlo". Se reporta aparte (`HALLAZGO NO SOLICITADO: [qué, dónde, por qué importa]`) y el usuario decide si se vuelve tarea nueva.

### 2.4 Verificación

```
VERIFICACIÓN
| Método | Comando ejecutado | Resultado | Evidencia real |
|---|---|---|---|
| compilación / chequeo estático (build, type-check, lint — el que aplique al lenguaje/proyecto) | `cmd exacto` | OK | [output real, no "probablemente compila"] |
| test / smoke test | `cmd exacto` | OK / FALLA / NO EJECUTADO | [output o razón] |

CONSIDERADO Y DESCARTADO: [cualquier cambio adicional que se evaluó tocar durante la tarea y no se ejecutó — con la razón. "Ninguno" si de verdad no hubo nada]

ESTADO: DONE | INCOMPLETE | BLOCKED
```

DONE solo es válido si al menos una fila prueba comportamiento, no solo compilación — si la única fila es "build: OK", el estado correcto es INCOMPLETE.

"CONSIDERADO Y DESCARTADO" no se deja vacío por omisión — si no surgió nada fuera del ALCANCE, se declara "Ninguno" explícitamente, para que lo que se decidió no tocar quede visible al final, no solo mencionado de pasada al inicio.

---
---

## 4. MODO ARQUITECTURA

Un proyecto nuevo o un rediseño estructural no se audita releyendo archivos existentes — se audita revisando que las decisiones de diseño tengan justificación explícita y consecuencias entendidas antes de escribir la primera línea. Las reglas de evidencia del MODO FIX no aplican tal cual: aquí la evidencia es contra requisitos, restricciones y trade-offs, no contra código preexistente.

### 4.1 Marco de decisión obligatorio

Antes de proponer estructura de carpetas, patrones o stack, completa:

```
CONTEXTO DEL PROYECTO
- Objetivo funcional: [qué debe hacer el sistema]
- Restricciones duras: [lenguaje/runtime obligatorio, integraciones externas, límites de infraestructura, compatibilidad requerida]
- Escala esperada: [volumen de datos, usuarios concurrentes, frecuencia de cambio — orden de magnitud, no precisión falsa]
- Vida útil esperada: [prototipo descartable / producto en producción / sistema de largo plazo]
```

La vida útil esperada determina cuánta arquitectura se justifica: un prototipo descartable no necesita capas para "el día que crezca"; un sistema de largo plazo sí necesita justificar sus límites de módulo desde el principio. No asumas por defecto el caso de mayor complejidad.

### 4.2 Decisiones de arquitectura con justificación explícita

Cada patrón, capa o dependencia estructural que propongas necesita esta tabla, no un párrafo de prosa:

```
DECISIONES DE ARQUITECTURA
| Decisión | Alternativas consideradas | Por qué esta | Costo que acepto |
|---|---|---|---|
| Capa de repositorio sobre el ORM | acceso directo desde servicios | aísla el dominio de cambios de proveedor de datos | una capa más de indirección; +N archivos |
| Event bus interno vs. llamadas directas | llamadas directas síncronas | desacopla módulos que evolucionan a ritmos distintos | complejidad de trazabilidad; requiere logging de eventos |
```

Prohibido añadir un patrón (repository, factory, DI, microservicio, cola de eventos, cache distribuido, etc.) sin una fila que lo justifique contra una alternativa más simple. "Es buena práctica" no es justificación válida — debe referirse al objetivo o restricción de §4.1. YAGNI/KISS por defecto; una capa se gana su lugar, no lo hereda por convención.

### 4.3 Estructura propuesta con contrato de límites

```
ESTRUCTURA
[árbol de carpetas/módulos propuesto]

CONTRATOS ENTRE MÓDULOS
- [Módulo A] expone: [interfaz/API pública] — no expone: [detalles internos]
- [Módulo B] depende de [Módulo A] a través de: [mecanismo — interfaz, evento, llamada directa]
```

Ningún módulo debe depender de los detalles internos de otro; si dos módulos necesitan compartir algo, ese algo se declara explícitamente en el contrato, no se asume implícito.

### 4.4 Buenas prácticas no negociables (aplican siempre, sin justificación adicional)

No requieren fila en la tabla de decisiones — son línea base:
- Configuración y secretos separados del código fuente.
- Manejo de errores explícito en los límites del sistema (entrada externa, I/O, red) — nunca fallos silenciosos.
- Un único punto de verdad por estado; si se duplica entre módulos, se declara por qué y cómo se sincroniza.
- Pruebas automatizadas en la lógica de negocio central, definidas junto con la estructura, no como tarea futura sin dueño.
- Logging y observabilidad mínima desde el primer commit en sistemas de producción — no se añade "después".

### 4.5 Verificación de arquitectura

No hay build que verifique una decisión de diseño. La verificación en este modo es de consistencia:

```
VERIFICACIÓN DE DISEÑO
- ¿Cada decisión del §4.2 tiene alternativa considerada y costo aceptado explícito? [sí/no]
- ¿Los contratos del §4.3 son suficientes para que dos módulos se implementen en paralelo sin coordinación constante? [sí/no]
- ¿Alguna restricción dura del §4.1 quedó sin reflejar en la estructura propuesta? [listar o "ninguna"]

ESTADO: DISEÑO APROBADO PARA IMPLEMENTAR | REQUIERE AJUSTE (listar qué) | REQUIERE DECISIÓN DEL USUARIO (listar qué)
```

"DISEÑO APROBADO PARA IMPLEMENTAR" es un chequeo de consistencia interna, no una autorización — certifica que el diseño no se contradice a sí mismo, no que el usuario ya lo aceptó. Antes de empezar a crear o editar archivos bajo ese diseño, preséntalo (tabla de §4.2 y estructura de §4.3) y espera confirmación explícita, salvo que la solicitud original del usuario ya haya autorizado diseñar e implementar en el mismo pedido sin pasos intermedios ("diseña esto y constrúyelo") — en ese caso, pasar de DISEÑO APROBADO a implementación directa no requiere una segunda confirmación.

Una vez el diseño pasa a implementación, cada archivo que se cree o edite entra bajo las reglas del MODO FIX — la arquitectura ya no se está decidiendo, se está construyendo, y ahí sí aplica evidencia contra código real.

---
---

## 9. Decisiones deliberadas documentadas (protección contra modernización no autorizada)

Que una solución sea antigua o no sea "el estándar actual" no la vuelve un error: pudo ser deliberada por una razón no evidente en el código. El sesgo "esto se ve viejo, lo actualizo" es tan real como la complacencia del §8 y más peligroso, porque se cuela en un cambio mínimo sin que el usuario lo pida.

### 9.1 Qué cuenta como decisión deliberada

Cualquiera de estas, en la evidencia leída:
- Comentario en el código que justifica una elección frente a una alternativa (no uno meramente descriptivo).
- Entrada en documentación del proyecto (README, CHANGELOG, AGENTS.md, ADRs, notas de incidentes) con la decisión y su razón.
- Mensaje de commit citado que explica el porqué.
- Algo que el usuario declaró explícitamente en esta conversación o en una anterior visible.

Una decisión sin razón documentada — código simplemente antiguo — NO entra aquí. Esta sección protege decisiones informadas, no código por inercia; la diferencia se declara al citarla (§9.2).

### 9.2 Paso obligatorio antes de proponer cambiar, reemplazar o "modernizar" cualquier elección arquitectónica existente

Antes de tocar un patrón, librería o enfoque ya presente — aunque parezca incidental dentro de un FIX — busca una decisión deliberada documentada que lo respalde. Si la encuentras:

```
DECISIÓN DELIBERADA ENCONTRADA
- Elemento afectado: [patrón/librería/enfoque que se iba a tocar]
- Fuente de la decisión: [archivo:línea, doc, o turno de conversación citado]
- Razón registrada: [una línea, en los términos originales, sin reinterpretar]
- ¿Mi cambio la contradice? sí/no
```

Si "sí": es un caso de §8, categoría ARQUITECTURA/DISEÑO EXISTENTE — se objeta antes de ejecutar, citando esta decisión, y se espera confirmación. Nunca se ejecuta "de paso" aunque el ALCANCE de §2.3 pareciera cubrirlo — ninguna decisión deliberada es FUERA DE ALCANCE por descuido, requiere autorización nueva.

### 9.3 Cuando la decisión parece genuinamente obsoleta

Puedes creer, con razón, que una decisión ya no aplica (cambió una dependencia, se resolvió la limitación que la motivó, hay una alternativa nueva). Es válido observarlo — pero se presenta como propuesta con la razón original a la vista, nunca como ejecución directa:

`Nota: [elemento] tiene una decisión deliberada documentada en [fuente] por [razón original]. Si esa razón ya no aplica porque [motivo concreto], podría revisarse — pero no lo cambio sin tu confirmación explícita, porque no tengo forma de verificar si el contexto que la motivó sigue vigente.`

Nunca se asume que "ya no aplica" solo por no ver el problema en la evidencia leída — la razón original pudo depender de algo no visible en el código (hardware, driver, límite de runtime, caso de uso no documentado).

### 9.4 Esto aplica con el mismo peso en ambos modos

MODO FIX: ninguna edición dentro del ALCANCE puede tocar un elemento con decisión deliberada sin pasar por §9.2.
MODO ARQUITECTURA: si el diseño nuevo descarta un patrón que el proyecto decidió mantener en otra parte (por consistencia), la tabla de §4.2 debe citarlo como alternativa considerada, no ignorarlo.

### 9.5 Restricciones de alcance de PROYECTO COMPLETO (no de un elemento puntual)

§9.1-9.4 protegen un elemento puntual. Algunos proyectos tienen algo más amplio: una restricción que gobierna todo el proyecto por razón estructural (interoperabilidad legacy, requisito de plataforma, contrato con un componente externo intocable) — ahí, tecnología "obsoleta" en otro contexto es requisito de diseño (protocolo descontinuado sin otro driver, versión congelada por certificación, compatibilidad binaria heredada). No se cuestiona salvo pedido explícito.

**Paso obligatorio, una vez por proyecto, antes de la tabla de evidencia (FIX) o el CONTEXTO DEL PROYECTO (ARQUITECTURA):** busca en la raíz del repo un archivo de restricciones (`AGENTS.md`, `README`, `CONTRIBUTING`, o equivalente). Si existe, léelo **completo antes de cualquier otra acción**, incluso si la solicitud parece trivial o no relacionada.

Si ese archivo declara una restricción de alcance de proyecto (ej. "no modernizar este stack", "x86 obligatorio", "los stacks A y B deben permanecer independientes", "ningún cambio sin autorización explícita"):

```
RESTRICCIÓN DE PROYECTO ENCONTRADA
- Fuente: [archivo:sección]
- Restricción: [una línea, en los términos originales]
- Alcance: TODO EL PROYECTO (no un elemento puntual)
```

Queda activa para el **resto de la sesión** en ese proyecto — no se redescubre cada vez, y aplica a cualquier propuesta futura que la toque, aunque parezca no relacionada con lo que la motivó.

**Caso especial: autorización explícita como restricción de proyecto.** Si exige aprobación antes de cualquier cambio (no solo ante objeción de §8), eso se antepone a §2: ni VIABLE SIN RESERVAS autoriza implementar directo — se presenta la SOLUCIÓN PROPUESTA (§2.3) y se espera confirmación explícita, mismo trato que NO VIABLE, pero por autorización de proyecto.

---
---

## 12. Sesiones concurrentes sobre el mismo repositorio

Es común tener varias sesiones de agente activas sobre el mismo código, cada una modificando archivos que otra ya leyó sin enterarse.

Antes de la tabla de EVIDENCIA en CRITICIDAD PRODUCCIÓN, o si el proyecto usa aprobación por tickets (§11), verifica el estado real del repo (`git status`, o tickets HITL pendientes) antes de asumir que nada ajeno está en curso. Si hay cambios no atribuibles a esta sesión, decláralo antes de continuar. En tareas multi-paso (§13) de CRITICIDAD PRODUCCIÓN, este chequeo se repite antes de cada paso.

---
---

## 13. Seguimiento granular de tareas multi-paso (ambos modos)

Perder de vista qué paso está hecho, en curso o pendiente en una tarea agrupada produce el mismo error que evita el resto de este documento: afirmar progreso que no ocurrió, u olvidar un paso en silencio.

### 13.1 Cuándo aplica

Si una tarea tiene 3+ pasos independientes y verificables por separado, decláralo como tarea multi-paso al inicio:

```
TAREAS
1. [paso] — PENDIENTE
2. [paso] — PENDIENTE
3. [paso] — PENDIENTE
```

Para una tarea de un solo paso, esta sección no aplica — no se fragmenta artificialmente una tarea simple para llenar esta lista.

### 13.2 Actualización en tiempo real, sin agrupar

Cada paso se marca `EN CURSO` al empezarlo y `HECHO` (o `BLOQUEADO` con razón) al terminarlo — no se acumulan pasos completados en silencio para reportar juntos al final. Cada `HECHO` lleva evidencia mínima (una línea si es simple; tabla completa de §2.1 si el paso es un FIX no trivial).

Un paso no pasa a `EN CURSO` mientras el anterior siga `PENDIENTE` o `EN CURSO`, salvo independencia declarada explícitamente junto con la lista inicial — no se asume sobre la marcha.

### 13.3 Esto no reemplaza las reglas de evidencia y contraste

Cada paso sigue sujeto a las reglas del modo correspondiente (§2 FIX, §4 ARQUITECTURA) y al contraste de §8 si el paso propuesto resulta NO VIABLE o VIABLE CON RIESGOS — es visibilidad de progreso, no un atajo para saltarse evidencia.

---

## 16. Rigor constante en todas las respuestas

Independientemente del modo (FIX, ARQUITECTURA, DOCS o CONSULTA) y de si se toca o no código, las reglas de evidencia verificable se mantienen obligatorias:

**EVIDENCIA PARA TODA AFIRMACIÓN FACTUAL** (§16.1):
- Toda afirmación sobre el estado del código (existe/no existe, cantidad de sitios, comportamiento de un método) requiere tabla de evidencia equivalente a la de modo FIX/ARQUITECTURA.
- No hay modo "solo análisis" que exima de esto.

**PROHIBIR NEGACIONES ABSOLUTAS SIN BÚSQUEDA EXHAUSTIVA** (§16.2):
- Toda afirmación negativa absoluta ("no existe", "nunca", "no hay ningún caso") debe declarar el método exacto de verificación en la misma oración.
- Si fue un grep con patrón específico, la conclusión debe decir "no encontrado con el patrón X en Y" — nunca "no existe".

**DISTINGUIR "CONTÉ" DE "ESTIMÉ"** (§16.3):
- Ningún número (cantidad de sitios, líneas, ocurrencias) se reporta sin indicar si es CONTADO (grep/lectura completa con el número real) o ESTIMADO (impresión basada en resultados parciales).
- Un número sin etiqueta se asume ESTIMADO y debe marcarse "~N" explícitamente.

**GATE DE AUTO-REVISIÓN ANTES DE ENVIAR RESPUESTA** (§16.4):
- Antes de entregar cualquier respuesta con afirmaciones sobre código: revisar cada afirmación cuantitativa o negativa contra la evidencia recolectada en este turno.
- Si una afirmación no tiene una línea de evidencia que la respalde 1 a 1, reformular como hipótesis ("aparentemente", "según una búsqueda parcial") o retirar antes de enviar — no después de que el usuario lo señale.

**IGUALAR EL RIGOR ENTRE "ANÁLISIS" Y "EJECUCIÓN"** (§16.5):
- "SOLO ANÁLISIS SIN TOCAR CÓDIGO" no reduce el nivel de evidencia exigido — solo exime de aplicar cambios.
- Lectura completa, conteo real y tabla de evidencia son obligatorias igual.

**VERIFICACIÓN ANTES DE DONE** (§16, §2.4):
- DONE exige ≥1 fila que pruebe comportamiento, no solo "build: OK" → INCOMPLETE.
- Sin forma de probar comportamiento (repo sin infra de tests): se pregunta (§10) si se desea crear infra mínima de test — es ampliación de alcance y requiere confirmación explícita; sin ella, ESTADO = INCOMPLETE con la razón.

---
