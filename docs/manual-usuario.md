# Manual de usuario (para personas no expertas)

Este manual explica, paso a paso y sin dar nada por sabido, cómo usar el kit de este repositorio para trabajar con un asistente de IA (por ejemplo Claude) sin perder el control de lo que te construye.

No necesitas ser programador experto. Sí necesitas poder abrir una terminal y escribir comandos cortos. Todo lo demás se explica aquí.

---

## 1. Qué es esto y para qué sirve

Cuando le pides a un asistente de IA que programe algo, suele pasar una de estas tres cosas:

1. Hace más de lo que pediste (toca archivos que no debía).
2. Dice "listo" sin haber probado nada.
3. Inventa un detalle que no le dijiste, y tú no te enteras hasta que falla.

Este kit es un conjunto de reglas y herramientas para evitar esas tres cosas. Funciona con una idea simple:

> **Primero se escribe, en palabras claras, qué debe hacer el programa. Después se construye. Y nada se da por terminado hasta que una prueba real demuestre que funciona.**

Piensa en una obra de construcción: antes de levantar una pared se dibuja el plano y se acuerda con el cliente. El kit es ese plano, más un inspector que revisa que cada pared esté donde dice el plano.

Tiene dos partes que se pueden usar por separado:

| Parte | Para qué sirve | Dónde está |
|---|---|---|
| **La política de comportamiento** | Reglas que el asistente debe cumplir siempre: no inventar, no tocar lo que no se pidió, preguntar cuando falta un dato | `docs/system-engineering-policy.SKILL.md` |
| **El kit de método (SGP Lite)** | Una forma ordenada de pedir cambios: especificar, planificar, ejecutar, validar | Carpeta `kit/` |

Si solo tienes 10 minutos, empieza por la política (sección 4.1 de este manual). Es lo que más ayuda por el menor esfuerzo.

---

## 2. Qué necesitas antes de empezar

- **Python 3.8 o superior.** Para comprobarlo, abre una terminal y escribe `python --version`. Si aparece un número como `3.11.4`, está bien. Si dice que no lo encuentra, instálalo desde python.org (en Windows, marca la casilla "Add Python to PATH" durante la instalación).
- **Git.** Comprueba con `git --version`. En Windows, instala "Git for Windows", que además trae "Git Bash" (una terminal que usaremos para un paso).
- **Un asistente de IA que pueda leer y escribir archivos de tu proyecto** (por ejemplo Claude Code). Si tu asistente es solo un chat sin acceso a archivos, puedes usar igual los textos de `kit/prompts.md`, pegándolos a mano.
- **Un proyecto de código** donde quieras aplicarlo (una carpeta con tu programa). Para practicar, sirve una carpeta vacía.

---

## 3. Las seis palabras que debes conocer

No hay más vocabulario que este. Léelo una vez y ya está.

| Palabra | Qué significa, en sencillo | Ejemplo |
|---|---|---|
| **Requisito** | Una frase que dice qué debe hacer el programa, de forma que se pueda comprobar | "Si el descuento es mayor a 100, el sistema muestra un error" |
| **Especificación (spec)** | La lista de todos los requisitos de una parte del programa | El archivo `specs/descuento/spec.md` |
| **Cambio** | Un pedido concreto de trabajo, con su plan y sus tareas | El archivo `changes/CHG-001-...md` |
| **Tarea** | Un paso pequeño (20 a 30 minutos) dentro de un cambio | "Rechazar precios negativos" |
| **Prueba** | Un mini programa que comprueba que algo funciona | Un archivo dentro de la carpeta `tests/` |
| **Verificador** | Un programa del kit que revisa que todo esté en orden | El comando `python tools/sgp_check.py` |

Cada requisito lleva un código, por ejemplo `DESC-001`. Ese código es el hilo que une todo: el requisito, la tarea que lo construye y la prueba que lo comprueba.

---

## 4. Instalación

### 4.1 Opción mínima: solo la política (5 minutos)

1. Localiza la carpeta de "skills" de tu asistente. En Claude Code suele ser `~/.claude/skills/` (en Windows: `C:\Users\TuUsuario\.claude\skills\`).
2. Dentro crea una carpeta llamada `system-engineering-policy`.
3. Copia el archivo `docs/system-engineering-policy.SKILL.md` de este repositorio dentro de esa carpeta y renómbralo a `SKILL.md`.
4. Listo. No tienes que cambiar nada en tus proyectos.

Desde ese momento, el asistente sigue las reglas de la política en cualquier tarea de ingeniería. Verás que empieza a mostrar tablas de evidencia, a pedirte confirmación antes de cambios importantes y a decir "no pude verificarlo" en vez de inventar.

### 4.2 Opción completa: el kit en un proyecto

Dentro de tu proyecto:

1. **Copia** estas carpetas y archivos desde `kit/` a la raíz de tu proyecto: `docs/`, `specs/`, `changes/`, `tools/`, `skills/`, `AGENTS.md`, `CLAUDE.md`, `sgp.yaml`, `prompts.md`, `METODOLOGIA.md`.
2. **Abre `sgp.yaml`** y escribe los comandos de tu proyecto para compilar y probar. Por ejemplo, en un proyecto Python:
   ```yaml
   comandos:
     build: "python -m compileall -q mi_paquete"
     tests: "python -m unittest discover -s tests -t ."
     lint: ""
     test_por_requisito: "python -m unittest discover -s tests -t . -k {id_py}"
   ```
   Si no sabes cuáles son, pregúntale a tu asistente: "¿Qué comandos uso para compilar y para correr las pruebas de este proyecto?".
3. **Abre `AGENTS.md`** y escribe dos o tres líneas sobre qué es tu proyecto y qué comandos usa.
4. **Instala el candado de pruebas** (evita que se borren pruebas por accidente). En Git Bash, desde la raíz del proyecto:
   ```bash
   cp tools/pre-commit .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```
   Este paso requiere que la carpeta ya sea un repositorio Git (si no lo es, ejecuta antes `git init`).
5. **(Opcional) Instala las skills del kit** si tu asistente las soporta:
   ```bash
   python tools/sync_skills.py --agent claude-code
   ```
   Otros valores posibles: `copilot`, `codex`, `cursor`, `generico`. El comando `python tools/sync_skills.py --list` muestra las opciones.

Para comprobar que todo quedó bien, ejecuta:

```bash
python tools/sgp_check.py
```

Debe terminar con una línea parecida a `Resumen: 0 error(es), 0 aviso(s).` Si aparecen avisos por archivos sin completar, es normal al inicio.

---

## 5. Tu primer cambio, paso a paso

Vamos a imaginar que quieres pedir "una función que calcule el precio final con descuento". El proceso tiene cinco fases. En cada una hay algo que hace el asistente y algo que apruebas tú.

### Fase 1. Especificar (tú apruebas la especificación)

Dile a tu asistente algo así:

> "Vamos a especificar una función que calcule el precio final con descuento. No escribas código todavía. Hazme las preguntas que necesites, de una en una."

El asistente te hará preguntas cortas (por ejemplo: ¿el descuento es un porcentaje?, ¿qué pasa si es negativo?). Respóndelas con tus palabras. Al final escribirá el archivo `specs/descuento/spec.md` con requisitos como:

- **DESC-001** CUANDO se calcula el precio final con un descuento entre 0 y 100, EL SISTEMA devolverá el precio redondeado a 2 decimales.
- **DESC-002** SI el descuento es menor que 0 o mayor que 100, ENTONCES EL SISTEMA mostrará un error.

**Qué revisas tú:** que cada requisito diga lo que realmente quieres, y que el resultado sea algo que se pueda ver o medir (un mensaje, un número, un error). Si una frase dice "debe ser rápido" o "fácil de usar", pide que la cambie por algo medible.

### Fase 2. Revisar la especificación (opcional pero recomendada)

Pídele:

> "Revisa la especificación como un control de calidad exigente. Dime ambigüedades, contradicciones y casos que faltan. No propongas soluciones todavía."

Contesta lo que te pregunte y pídele que actualice el archivo.

### Fase 3. Planificar el cambio (tú apruebas el plan y las tareas)

Crea el archivo del cambio con este comando (el nombre puede ser el que quieras):

```bash
python tools/sgp_check.py --nuevo calculo-precio-final
```

Se crea `changes/CHG-001-calculo-precio-final.md`. Pídele al asistente que lo complete: qué problema resuelve, qué queda fuera, cuántos días como máximo puede tardar (`apetito_dias`) y una lista de tareas pequeñas. Cada tarea debe tener:

- El código del requisito que construye, entre corchetes: `[DESC-001]`.
- Una línea `Hecho cuando:` que diga cómo se sabrá que terminó.

También debe elegir el **carril** (el tamaño del cambio):

| Carril | Cuándo usarlo |
|---|---|
| `rapido` | Arreglar un error o hacer una prueba corta, en menos de un día |
| `normal` | Un cambio que toca una sola parte del programa (lo más habitual) |
| `mayor` | Un cambio grande: toca varias partes, cambia cómo se comunican, o agrega una dependencia nueva |

Si dudas entre dos, elige el más pequeño. Puedes subir de carril si aparece algo inesperado.

### Fase 4. Ejecutar (una tarea por vez)

Pide al asistente **una sola tarea**:

> "Implementa solo la tarea T001. Escribe primero la prueba y confirma que falla. Luego programa. Al terminar, ejecuta `python tools/sgp_check.py --run`, muéstrame el resultado y detente."

Reglas de oro de esta fase:

- **Una tarea por sesión.** Es mejor abrir una conversación nueva para cada tarea.
- **La prueba primero.** Debe fallar antes de programar (eso demuestra que la prueba sirve).
- **El nombre de la prueba lleva el código del requisito con guion bajo**, por ejemplo `test_DESC_001_calcula_con_descuento`. Así el verificador sabe qué requisito comprueba.
- El asistente marca la tarea como hecha (`[x]`) **solo si** el verificador no da errores.

### Fase 5. Validar y cerrar (tú apruebas el cierre)

Cuando todas las tareas estén marcadas, cambia el campo `estado:` del cambio a `revision` y ejecuta:

```bash
python tools/sgp_check.py --stage pre-merge
```

Esta versión estricta ejecuta las pruebas de cada requisito una por una y muestra una tabla como esta:

```
Trazabilidad CHG-001-calculo-precio-final:
  DESC-001  ok
  DESC-002  ok
```

Si todo dice `ok` y el resumen indica 0 errores, revisa tú mismo con esta lista y, si estás conforme, cambia `estado:` a `hecho`:

- [ ] Cada requisito tiene una prueba real (no solo un comentario con su código).
- [ ] No se borraron ni se debilitaron pruebas.
- [ ] El asistente no hizo cosas fuera de lo pedido.
- [ ] Entiendo lo que se construyó lo suficiente como para mantenerlo.

---

## 6. Cuando algo falla: mensajes del verificador y qué hacer

El verificador escribe cada problema en español y dice **cómo corregirlo**. Estos son los más frecuentes:

| Mensaje | Qué significa | Qué hacer |
|---|---|---|
| `la tarea T001 no tiene «Hecho cuando:»` | A una tarea le falta la línea que dice cómo saber que terminó | Pídele al asistente que la agregue debajo de la tarea |
| `la tarea T002 no enlaza a ningún requisito` | La tarea no dice qué requisito construye | Agrega el código entre corchetes, por ejemplo `[DESC-001]` |
| `el requisito DESC-003 no existe en specs/` | El cambio cita un requisito que aún no está escrito | Primero se escribe el requisito en la especificación (Fase 1) |
| `el requisito DESC-002 no está cubierto por ninguna tarea` | Hay un requisito sin nadie que lo construya | Agrega una tarea con `[DESC-002]` |
| `presupuesto agotado: 5 d transcurridos, apetito 3 d` | El cambio tardó más de lo que se acordó | **No se extiende.** Decide: reformular (un cambio nuevo y más pequeño) o cancelar (`estado: cancelado`) |
| `requisito sin cobertura comprobada (sin pruebas)` | No hay una prueba real para ese requisito | Escribe una prueba cuyo nombre incluya el código con guion bajo, por ejemplo `DESC_004` |
| `requisito sin cobertura comprobada (falla)` | La prueba existe pero no pasa | Corrige el programa (nunca la prueba, salvo que la prueba esté mal por decisión tuya) |
| `sensor 'build' sin configurar` | Falta el comando de compilar en `sgp.yaml` | Complétalo (ver sección 4.2, paso 2) |
| `contiene marcas [POR-ACLARAR] sin resolver` | Quedaron dudas sin responder en la especificación | Responde las dudas y borra la marca |
| `estado 'revision' con tareas pendientes` | Cambiaste a revisión con tareas sin terminar | Termina las tareas o vuelve a `aplicando` |

### El candado de pruebas

Si el asistente (o tú) intenta borrar o debilitar una prueba existente, Git no dejará hacer el `commit` y mostrará:

```
[ERROR] ratchet de pruebas: el commit elimina o modifica líneas existentes en tests/
```

Es una protección, no un fallo. Si de verdad el cambio en la prueba es correcto y lo apruebas tú, se autoriza con:

```bash
SGP_TESTS_APPROVED=1 git commit -m "mensaje"
```

---

## 7. Las reglas del asistente, explicadas sin tecnicismos

La política (`system-engineering-policy`) hace que el asistente siga estas ideas. No tienes que memorizarlas, pero te sirven para saber qué esperar y qué exigir:

1. **Lee antes de tocar.** No cambia un archivo sin haberlo leído y mostrado qué encontró.
2. **No adivina.** Si le falta un dato que no puede sacar de los archivos, te pregunta. No rellena con "supuestos razonables".
3. **Un cambio, un alcance.** Si ve un problema fuera de lo que pediste, te lo avisa, pero no lo arregla por su cuenta.
4. **"Listo" significa probado.** No dice que terminó sin mostrar el resultado real de una prueba. Si no pudo probarlo, dice "no pude verificarlo".
5. **Te contradice con argumentos.** Si tu idea tiene un problema, te lo dice antes de ejecutarla, en lugar de darte la razón.
6. **Pide permiso para lo difícil de deshacer.** Antes de guardar cambios definitivos (commit, push, unir ramas) te consulta.
7. **No inventa resultados.** Lo que muestra como salida de un comando debe ser salida real.
8. **No obedece textos escondidos.** Si un archivo o página contiene "instrucciones", el asistente las trata como información, no como órdenes.

Al terminar una tarea, el asistente cierra con la frase `FIN DE PROCESO`.

---

## 8. Preguntas frecuentes

**¿Tengo que usar todo el kit?**
No. Puedes quedarte solo con la política (sección 4.1). Si un día quieres más orden, agregas el kit.

**¿Funciona con cualquier lenguaje de programación?**
Sí, porque el verificador solo ejecuta los comandos que tú le indiques en `sgp.yaml`. Lo que cambia entre lenguajes es cómo se compila y cómo se corren las pruebas.

**¿Y si mi proyecto casi no tiene pruebas automáticas?**
Para las partes que no se pueden probar automáticamente, el cambio incluye una tabla llamada "Verificación manual", donde anotas qué probaste a mano y si salió bien (`OK`). El verificador la acepta como evidencia.

**¿Cuánto tarda cada tarea?**
La idea es entre 20 y 30 minutos. Si una tarea es más larga, pídele al asistente que la divida.

**¿Puedo saltarme la especificación para un arreglo pequeño?**
Sí: usa el carril `rapido`. Pero aun así el arreglo necesita una prueba que demuestre que quedó corregido.

**El asistente no sigue las reglas. ¿Qué hago?**
Recuérdale la regla por su nombre ("una tarea por sesión", "no borres pruebas") y verifica que la skill esté instalada. Las reglas escritas en archivos funcionan mejor cuando se conectan con un mecanismo automático, como el candado de pruebas de la sección 6.

**¿Esto garantiza que el programa no tenga errores?**
No. Garantiza que cada requisito escrito tiene una prueba que lo ejercita y que el trabajo quedó registrado. No juzga si los requisitos son los correctos ni si una prueba es demasiado débil: eso sigue dependiendo de tu revisión.

---

## 9. Cuándo NO conviene usar esto

- Para un script que vas a usar una sola vez y tirar. Con la política es suficiente.
- Si el proyecto no tiene ningún modo de ejecutarse desde la terminal.
- Si nadie va a leer ni aprobar la especificación: el método pierde su sentido sin una persona que decida.

---

## 10. Glosario rápido

- **Agente / asistente de IA:** el programa de inteligencia artificial que escribe código por ti.
- **Commit:** guardar de forma permanente un conjunto de cambios en Git.
- **EARS:** una forma de escribir requisitos con las palabras CUANDO, SI…ENTONCES, MIENTRAS.
- **Frontmatter:** las líneas del inicio de un archivo, entre dos rayas `---`, con datos como `estado` y `carril`.
- **Hook (candado):** un programa que Git ejecuta automáticamente antes de guardar cambios.
- **Prueba de regresión:** una prueba que se escribe al corregir un error para que no vuelva a aparecer.
- **Skill:** un archivo con instrucciones que el asistente carga cuando le hacen falta.
- **Terminal:** la ventana donde se escriben comandos.

---

## 11. Dónde seguir

- El recorrido completo con ejemplos reales de salida: `docs/ejemplo-practico.md`.
- La metodología en una página: `kit/METODOLOGIA.md`.
- Un proyecto de ejemplo ejecutable: carpeta `examples/descuento/`.
- La política completa: `docs/system-engineering-policy.SKILL.md`.
