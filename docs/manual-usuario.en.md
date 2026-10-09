# User manual (for non-experts)

**English** · [Español](manual-usuario.md)

This manual explains, step by step and assuming nothing, how to use the kit in this repository to work
with an AI assistant (for example Claude) without losing control of what it builds for you.

You do not need to be an expert programmer. You do need to be able to open a terminal and type short
commands. Everything else is explained here.

---

## 1. What this is and what it is for

When you ask an AI assistant to program something, one of these three things usually happens:

1. It does more than you asked (it touches files it should not).
2. It says "done" without having tested anything.
3. It invents a detail you did not give it, and you do not find out until it fails.

This kit is a set of rules and tools to avoid those three things. It works with one simple idea:

> **First you write, in plain words, what the program must do. Then you build it. And nothing is
> considered finished until a real test proves it works.**

Think of a construction site: before raising a wall you draw the blueprint and agree on it with the
client. The kit is that blueprint, plus an inspector that checks every wall is where the blueprint
says it is.

It has two parts you can use separately:

| Part | What it is for | Where it is |
|---|---|---|
| **The behavior policy** | Rules the assistant must always follow: do not invent, do not touch what was not asked, ask when a piece of data is missing | `docs/system-engineering-policy.SKILL.md` |
| **The method kit (SGP Lite)** | An orderly way to request changes: specify, plan, execute, validate | `kit/` folder |

If you only have 10 minutes, start with the policy (section 4.1 of this manual). It is what helps the
most for the least effort.

---

## 2. What you need before starting

- **This kit downloaded to your computer.** Download this repository from the page where you found it
  (`Code` → `Download ZIP`; or `git clone` if you know how) and unzip it into a fixed folder, for
  example `C:\path\to\sgp-lite`. The kit folder is the `kit` subfolder of that download; note its full
  path (you will use it in section 4).
- **Python 3.8 or higher.** To check, open a terminal and type `python --version`. If a number like
  `3.11.4` appears, you are fine. If it says it cannot find it, install it from python.org (on Windows,
  check "Add Python to PATH" during installation).
- **Git.** Check with `git --version`. On Windows, install "Git for Windows", which also brings "Git
  Bash" (a terminal we will use for one step).
- **An AI assistant that can read and write files in your project** (for example Claude Code). If your
  assistant is only a chat with no file access, you can still use the texts in `kit/prompts.md` by
  pasting them by hand.
- **A code project** where you want to apply it (a folder with your program). To practice, an empty
  folder works.
- **Knowing how to open the terminal in your project folder.** All commands in this manual run with
  the terminal "standing" at the root of your project. The easy way: open the project folder in File
  Explorer, right-click on an empty space and choose **"Open in Terminal"** (Windows 11) or **"Open
  PowerShell window here"** (Windows 10); on macOS, right-click the folder → **Services → New Terminal
  at Folder**. If that option does not appear, open a terminal and type
  `cd "C:\full\path\to\your project"`. Commands starting with `python` work in PowerShell, in the
  macOS/Linux Terminal, or in Git Bash; the only ones that need Git Bash on Windows are `cp` and
  `chmod` (a single step, section 4.2).

---

## 3. The six words you need to know

There is no more vocabulary than this. Read it once and you are done.

| Word | What it means, simply | Example |
|---|---|---|
| **Requirement** | A sentence saying what the program must do, in a way that can be checked | "If the discount is greater than 100, the system shows an error" |
| **Specification (spec)** | The list of all the requirements of one part of the program | The file `specs/descuento/spec.md` |
| **Change** | A concrete work request, with its plan and its tasks | The file `changes/CHG-001-...md` |
| **Task** | A small step (20 to 30 minutes) inside a change | "Reject negative prices" |
| **Test** | A mini program that checks that something works | A file inside the `tests/` folder |
| **Checker** | A program in the kit that reviews that everything is in order | The command `python tools/sgp_check.py` |

Each requirement carries a code, for example `DESC-001`. That code is the thread that ties everything
together: the requirement, the task that builds it and the test that checks it.

---

## 4. Installation

### 4.1 Minimal option: only the policy (5 minutes)

1. Locate your assistant's "skills" folder. In Claude Code it is usually `~/.claude/skills/` (on
   Windows: `C:\Users\YourUser\.claude\skills\`). If you use another assistant, use the folder that
   assistant reads for its skills (for example, in opencode it is `~/.agents/skills/`).
2. Inside it, create a folder named `system-engineering-policy`.
3. Copy the file `docs/system-engineering-policy.SKILL.md` from this repository into that folder and
   rename it to `SKILL.md`.
4. Recommended: the policy has a companion (`protocolo-ingenieria-senior`) with the detailed
   procedure. Repeat steps 2 and 3 with `docs/protocolo-ingenieria-senior.SKILL.md` in a
   `protocolo-ingenieria-senior` folder.
5. Done. You do not have to change anything in your projects.

From that moment on, the assistant follows the policy's rules in any engineering task. You will see it
start showing evidence tables, asking for confirmation before important changes, and saying "I could
not verify it" instead of inventing.

### 4.2 Full option: the kit in a project

Inside your project:

1. **Bring the kit into your project.** Choose one way:
   - **Installer (recommended: lets you update later):** from your project's root, run
     (Windows example; replace the path with yours from section 2):
     `python "C:\path\to\sgp-lite\kit\tools\sgp_kit.py" init --source "C:\path\to\sgp-lite\kit" --dest .`
     The quotes protect the path if it has spaces. To pull kit improvements later, repeat the command
     changing `init` to `update`.
   - **Zip (the simplest, no updates):** download `sgp-lite.zip` from the same place where you got this
     manual, and unzip it **at the root of your project** (choose "Extract here", or set your project
     folder as the destination). If it asks whether to replace files you already have (for example your
     own `AGENTS.md` or `sgp.yaml`), answer **no**.
   - **Manual copy (no updates):** copy to your project's root `docs/`, `specs/`, `changes/`, `tools/`,
     `skills/`, `AGENTS.md`, `CLAUDE.md`, `sgp.yaml`, `prompts.md`, `METODOLOGIA.md` and `ADOPCION.md`
     from `kit/`.
2. **Open `sgp.yaml`** and write your project's commands to build and test. For example, in a Python
   project:
   ```yaml
   comandos:
     build: "python -m compileall -q mi_paquete"
     tests: "python -m unittest discover -s tests -t ."
     lint: ""
     test_por_requisito: "python -m unittest discover -s tests -t . -k {id_py}"
   ```
   If you do not know them, ask your assistant: "What commands do I use to build and to run this
   project's tests?".
3. **Open `AGENTS.md`** and write two or three lines about what your project is and which commands it
   uses.
4. **Install the test lock** (prevents tests from being deleted by accident). In Git Bash, from the
   project root:
   ```bash
   cp tools/pre-commit .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```
   This step requires the folder to already be a Git repository (if it is not, run `git init` first).
5. **(Optional) Install the kit's skills** if your assistant supports them:
   ```bash
   python tools/sync_skills.py --agent claude-code
   ```
   Other possible values: `copilot`, `codex`, `cursor`, `generico`, `opencode`. The command
   `python tools/sync_skills.py --list` shows the options. It installs the kit's 8 skills: 6 process
   and 2 behavior (the policy and its protocol).

To check everything is fine, run:

```bash
python tools/sgp_check.py
```

It should end with a line similar to `Resumen: 0 error(es), 0 aviso(s).` If warnings appear about
unfinished files, that is normal at the start.

---

## 5. Your first change, step by step

Let us imagine you want to request "a function that computes the final price with a discount". The
process has five phases. In each one there is something the assistant does and something you approve.

> **If your request is big or unclear** (several functions, a client, still-vague idea), before Phase 1
> it is worth writing a **requirements document**: ask the assistant "help me with the requirements
> document" (or use prompt 0 from `kit/prompts.md`). That document is **only support to clarify** what
> is being asked: no tool reviews it and it does not replace the specification. If the request is
> small, skip it.

### Phase 1. Specify (you approve the specification)

Tell your assistant something like:

> "We are going to specify a function that computes the final price with a discount. Do not write code
> yet. Ask me the questions you need, one at a time."

The assistant will ask short questions (for example: is the discount a percentage? what happens if it
is negative?). Answer them in your own words. At the end it will write the file
`specs/descuento/spec.md` with requirements such as:

- **DESC-001** WHEN the final price is computed with a discount between 0 and 100, THE SYSTEM shall
  return the price rounded to 2 decimals.
- **DESC-002** IF the discount is less than 0 or greater than 100, THEN THE SYSTEM shall show an error.

**What you review:** that each requirement says what you really want, and that the result is something
you can see or measure (a message, a number, an error). If a sentence says "must be fast" or "easy to
use", ask for it to be replaced with something measurable.

### Phase 2. Review the specification (optional but recommended)

Ask it:

> "Review the specification as a demanding quality control. Tell me ambiguities, contradictions and
> missing cases. Do not propose solutions yet."

Answer what it asks and ask it to update the file.

### Phase 3. Plan the change (you approve the plan and the tasks)

Create the change file with this command (the name can be whatever you want):

```bash
python tools/sgp_check.py --nuevo calculo-precio-final
```

This creates `changes/CHG-001-calculo-precio-final.md`. Ask the assistant to fill it in: what problem it
solves, what is out of scope, how many days it may take at most (`apetito_dias`) and a list of small
tasks. Each task must have:

- The code of the requirement it builds, in brackets: `[DESC-001]`.
- A `Hecho cuando:` line saying how it will be known that it is done.

It must also choose the **lane** (the size of the change):

| Lane | When to use it |
|---|---|
| `rapido` | Fix a bug or write a short test, in less than a day |
| `normal` | A change that touches a single part of the program (the most common) |
| `mayor` | A big change: touches several parts, changes how they communicate, or adds a new dependency |

If you hesitate between two, choose the smaller. You can move up a lane if something unexpected
appears.

### Phase 4. Execute (one task at a time)

Ask the assistant for **a single task**:

> "Implement only task T001. Write the test first and confirm it fails. Then program. When done, run
> `python tools/sgp_check.py --run`, show me the result and stop."

Golden rules of this phase:

- **One task per session.** It is better to open a new conversation for each task.
- **The test first.** It must fail before programming (that proves the test is useful).
- **The test name carries the requirement code with an underscore**, for example
  `test_DESC_001_calcula_con_descuento`. That way the checker knows which requirement it checks.
- The assistant marks the task as done (`[x]`) **only if** the checker reports no errors.

### Phase 5. Validate and close (you approve the close)

When all tasks are marked, change the change's `estado:` field to `revision` and run:

```bash
python tools/sgp_check.py --stage pre-merge
```

This strict version runs each requirement's test one by one and shows a table like this:

```
Trazabilidad CHG-001-calculo-precio-final:
  DESC-001  ok
  DESC-002  ok
```

If everything says `ok` and the summary reports 0 errors, review it yourself with this list and, if you
agree, change `estado:` to `hecho`:

- [ ] Each requirement has a real test (not just a comment with its code).
- [ ] No tests were deleted or weakened.
- [ ] The assistant did not do things outside the request.
- [ ] I understand what was built well enough to maintain it.

---

## 6. When something fails: checker messages and what to do

The checker writes each problem in Spanish and says **how to fix it**. These are the most frequent:

| Message | What it means | What to do |
|---|---|---|
| `la tarea T001 no tiene «Hecho cuando:»` | A task is missing the line saying how to know it is done | Ask the assistant to add it below the task |
| `la tarea T002 no enlaza a ningún requisito` | The task does not say which requirement it builds | Add the code in brackets, for example `[DESC-001]` |
| `el requisito DESC-003 no existe en specs/` | The change cites a requirement not written yet | First write the requirement in the specification (Phase 1) |
| `el requisito DESC-002 no está cubierto por ninguna tarea` | There is a requirement with nobody building it | Add a task with `[DESC-002]` |
| `presupuesto agotado: 5 d transcurridos, apetito 3 d` | The change took longer than agreed | **It is not extended.** Decide: reformulate (a new, smaller change) or cancel (`estado: cancelado`) |
| `requisito sin cobertura comprobada (sin pruebas)` | There is no real test for that requirement | Write a test whose name includes the code with an underscore, for example `DESC_004` |
| `requisito sin cobertura comprobada (falla)` | The test exists but does not pass | Fix the program (never the test, unless the test is wrong by your own decision) |
| `sensor 'build' sin configurar` | The build command is missing in `sgp.yaml` | Fill it in (see section 4.2, step 2) |
| `contiene marcas [POR-ACLARAR] sin resolver` | Open questions were left unanswered in the specification | Answer the questions and delete the marker |
| `estado 'revision' con tareas pendientes` | You moved to review with unfinished tasks | Finish the tasks or go back to `aplicando` |

### The test lock

If the assistant (or you) tries to delete or weaken an existing test, Git will not allow the `commit`
and will show:

```
[ERROR] ratchet de pruebas: el commit elimina o modifica líneas existentes en tests/
```

It is a protection, not a failure. If the test change really is correct and you approve it, it is
authorized with:

```bash
SGP_TESTS_APPROVED=1 git commit -m "mensaje"
```

---

## 7. The assistant's rules, explained without jargon

The policy (`system-engineering-policy`) makes the assistant follow these ideas. You do not have to
memorize them, but they help you know what to expect and what to demand:

1. **Read before touching.** It does not change a file without having read it and shown what it found.
2. **It does not guess.** If it is missing a piece of data it cannot get from the files, it asks you.
   It does not fill it in with "reasonable assumptions".
3. **One change, one scope.** If it sees a problem outside what you asked, it tells you, but does not
   fix it on its own.
4. **"Done" means tested.** It does not say it finished without showing the real result of a test. If
   it could not test it, it says "I could not verify it".
5. **It contradicts you with arguments.** If your idea has a problem, it tells you before executing it,
   instead of agreeing with you.
6. **It asks permission for the hard-to-undo.** Before saving definitive changes (commit, push, merging
   branches) it asks you.
7. **It does not invent results.** What it shows as command output must be real output.
8. **It does not obey hidden texts.** If a file or page contains "instructions", the assistant treats
   them as information, not as orders.

When finishing a task, the assistant closes with the phrase `FIN DE PROCESO`.

---

## 8. Frequently asked questions

**Do I have to use the whole kit?**
No. You can stay with just the policy (section 4.1). If one day you want more order, you add the kit.
To decide how much to use depending on the project's size and importance, see `kit/ADOPCION.md`.

**Does it work with any programming language?**
Yes, because the checker only runs the commands you give it in `sgp.yaml`. What changes between
languages is how it builds and how the tests are run.

**What if my project has almost no automated tests?**
For the parts that cannot be tested automatically, the change includes a table called "Verificación
manual" (Manual verification), where you note what you tested by hand and whether it worked (`OK`). The
checker accepts it as evidence.

**How long does each task take?**
The idea is between 20 and 30 minutes. If a task is longer, ask the assistant to split it.

**Can I skip the specification for a small fix?**
Yes: use the `rapido` lane. But even so, the fix needs a test proving it was corrected.

**The assistant does not follow the rules. What do I do?**
Remind it of the rule by name ("one task per session", "do not delete tests") and check that the skill
is installed. Rules written in files work better when they are connected to an automatic mechanism,
such as the test lock in section 6.

**Does this guarantee the program has no bugs?**
No. It guarantees that each written requirement has a test that exercises it and that the work was
recorded. It does not judge whether the requirements are the right ones or whether a test is too weak:
that still depends on your review.

---

## 9. When NOT to use this

- For a script you will use once and throw away. The policy is enough.
- If the project has no way to run from the terminal.
- If nobody will read or approve the specification: the method loses its meaning without a person
  deciding.

---

## 10. Quick glossary

- **Agent / AI assistant:** the artificial-intelligence program that writes code for you.
- **Commit:** to permanently save a set of changes in Git.
- **Requirements document:** a supporting text to clarify what is being asked before the specification;
  no tool verifies it.
- **EARS:** a way of writing requirements with the words WHEN, IF…THEN, WHILE.
- **Frontmatter:** the lines at the start of a file, between two dashes `---`, with data such as
  `estado` and `carril`.
- **Hook (lock):** a program Git runs automatically before saving changes.
- **Regression test:** a test written when fixing a bug so that it does not come back.
- **Skill:** a file with instructions that the assistant loads when it needs them.
- **Terminal:** the window where commands are typed.

---

## 11. Where to continue

- The full walkthrough with real output examples: `docs/ejemplo-practico.md`.
- The methodology on one page: `kit/METODOLOGIA.md`.
- How much of the kit to use depending on project size: `kit/ADOPCION.md`.
- A runnable example project: `examples/descuento/` folder.
- The full policy: `docs/system-engineering-policy.SKILL.md`. Its operational procedure:
  `docs/protocolo-ingenieria-senior.SKILL.md`.
