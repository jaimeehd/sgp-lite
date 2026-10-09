# From waterfall SDLC to continuous development with AI agents

> How the classic stages of the software lifecycle (requirements → specification →
> stages → tests → deployment → maintenance) were compressed into a continuous,
> change-by-change cycle, and which concrete mechanisms replace each stage when the one
> building is mostly an AI agent.

**English** · [Español](README.md)

[![CI](https://github.com/jaimeehd/sgp-lite/actions/workflows/ci.yml/badge.svg)](https://github.com/jaimeehd/sgp-lite/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

This repo started from a real session working with an AI agent on the design of a project-management
system, comparing it against industry tools (GitHub Spec Kit, OpenSpec, BMAD-METHOD) and against a
personal engineering policy already in use. The result was not "the definitive tool" — it was a map
of what replaces what, a minimal template (`kit/`) to apply it, and the full engineering policy
(`docs/system-engineering-policy.SKILL.md`) which ended up, in practice, proving almost every point
of the mapping below.

## The mapping

| Traditional SDLC | What used to happen | Equivalent with an AI agent | Concrete mechanism |
|---|---|---|---|
| **Requirements document** | Written once, at the start of the project | Becomes a **requirement per change**, not per project: written every time there is a request, with an observable acceptance criterion | `REQUISITO` section before touching code; one-question-at-a-time interview |
| **Specification document** | Derived from the previous one; defined modules and contracts | **Lives in the repo** (`specs/`), not in a separate document; read and updated on every change, never "finished" | Requirements in EARS format with an ID, versioned in git |
| **Project stages** | Sequential phases (analysis → design → build) | **Modes triggered by the task**, not by the calendar | FIX / ARQUITECTURA / DOCS / CONSULTA — or, more simply, lanes by size (fast / normal / major) |
| **Tasks per stage** | Assigned to people, tracked manually | 20-30 min tasks per agent session, each with a **verifiable success criterion** | "Done when: \<observable condition\>" |
| **Deliverables per stage** | Design documents, code, test cases | **Executed evidence**, not descriptions: real command output, never invented | Never declare something finished without showing the real output of a command |
| **Tests (at the end)** | A separate phase, after "finishing" the build | **Simultaneous with each task**: the test is written before the code | Red → green per task; real traceability (run each requirement's test, don't just search for its name in the code) |
| **Deployment to production** | A single event, at the end of the project | One release per small change, with **criticality declared from the start** that decides how much rigor it demands | Production / internal tool / throwaway script — not everything weighs the same |
| **Bug fixing** | A phase after deployment, with its own flow | The **same mechanism as building**, just narrower | A "fast" lane: a bug reproduced with a regression test, without the ceremony of a new requirement |
| **Maintenance** | Final phase, often neglected — "nobody updates the docs" | **Not a phase**: the spec never stops being alive because every future change re-reads it before touching anything | Documented decisions (ADR) so a decision already made and discarded is not repeated |

## The real difference, not cosmetic

In the traditional model the risk was that **building was slow and correcting the course was
expensive** — that is why so much was invested in specifying before writing code. With an AI agent,
building is cheap and fast; the risk flipped: **the danger is that the agent builds fast and badly,
without anyone noticing.**

That is why the mechanisms that matter today are not "write more documentation", they are:

- that nothing is considered finished without a real test proving it,
- that whatever is missing is asked, never inferred,
- that nothing outside the current request is touched,
- that decisions are not lost in a spoken conversation nobody reads again.

What did **not** change: a human has to approve before committing (commit, merge, release), and
architecture decisions are still documented to avoid repeating mistakes. AI did not make that
unnecessary — it made it more urgent, because now decisions are made more often and faster than
before.

## What is in this repo

> **First time, or not an expert?** Start with [`docs/manual-usuario.en.md`](docs/manual-usuario.en.md):
> it explains everything step by step, assuming nothing.

```text
.
├── README.md                    — this document
├── README.en.md                 — English version
├── sgp-lite.zip                 — the kit, zipped and ready to unzip into your project (alternative to the installer)
├── docs/
│   ├── manual-usuario.md                — step-by-step manual for non-experts (Spanish)
│   ├── manual-usuario.en.md             — same manual, in English
│   ├── ejemplo-practico.md              — a real walkthrough, with captured command output (not simulated)
│   ├── system-engineering-policy.SKILL.md — full engineering policy (evidence before editing,
│   │                                         verifiable DONE, no inferring, nothing outside scope,
│   │                                         confirmation before committing changes). Installable as-is
│   │                                         as an Agent Skill in any compatible agent.
│   └── protocolo-ingenieria-senior.SKILL.md — operational procedure of the policy (evidence table,
│                                             confidence-graded diagnosis, minimal scope, DONE verification)
├── kit/                         — minimal template applicable to any repo (SGP Lite)
│   ├── METODOLOGIA.md           — the methodology on one page
│   ├── ADOPCION.md              — how much of the kit to use depending on project size/criticality
│   ├── docs/constitution.md     — non-negotiable principles, each with how it is verified
│   ├── docs/requerimientos/     — requirements-document template (optional, documentation only)
│   ├── specs/                   — where the current requirements live
│   ├── changes/                 — template for a change (proposal + tasks + progress)
│   ├── skills/                  — 8 Agent Skills (6 process + 2 behavior) installable in your agent
│   ├── prompts.md               — the 6 process steps as prompts, for agents without skill support
│   └── tools/
│       ├── sgp_check.py         — checker: structure, real traceability, budget, test ratchet
│       ├── sgp_kit.py           — installs and UPDATES the kit in a project (init/update/status)
│       ├── sgp_zip.py           — builds sgp-lite.zip (same file list as the installer)
│       ├── sync_skills.py       — installs the skills into your agent's path
│       └── pre-commit           — git hook that blocks deleted or weakened tests
└── examples/
    └── descuento/                — a real, end-to-end runnable project (see docs/ejemplo-practico.md)
```

### Kit vs. policy — how they relate

`kit/` (SGP Lite) solves the *change cycle*: spec → tasks → verification → close, with a checker
that runs in any CI. `docs/system-engineering-policy.SKILL.md` solves the *agent's behavior within
each task*: what evidence it demands before editing, when something counts as "done", when it must
ask instead of inferring, and when it must ask for your confirmation before committing. They are
complementary — you can use one without the other, or both together: the policy governs step 4
(execute a task) of the kit in more depth than the kit defines on its own.

### Getting started

```bash
cd kit
python tools/sgp_check.py --help
python -m unittest tools/test_sgp_check.py -v   # 29 tests of the checker itself
```

To install the kit in your own repo, follow `kit/LEEME.md`. If you prefer not to use the installer,
unzip `sgp-lite.zip` at the root of your project (or copy the files by hand). The zip is regenerated
with `python kit/tools/sgp_zip.py --source kit --dest sgp-lite.zip` whenever the kit changes.

## Implementation procedure

Recommended order to adopt this in a real repo, from least to most commitment. Each step is optional
with respect to the next — you can stop at any of them and still be in a useful state. If you are
unsure **how much** to use depending on your project's size or criticality, start with
[`kit/ADOPCION.md`](kit/ADOPCION.md).

### Step 0 — Only the behavior policy (cheapest, touches nothing in the repo)

1. Copy `docs/system-engineering-policy.SKILL.md` into your agent's skills folder
   (e.g. `~/.claude/skills/system-engineering-policy/SKILL.md` for Claude Code). The kit also ships it
   in `kit/skills/system-engineering-policy/`, together with its companion protocol
   (`protocolo-ingenieria-senior`); `sync_skills.py` (Step 2) installs both along with the others.
2. It requires no new file in the working repo. It governs the agent's *behavior* (evidence before
   editing, verifiable DONE, no inferring, staying in scope) in any task, without a spec methodology.
3. Valid as a single starting point — it is the piece with the most impact for the least cost.

### Step 1 — Minimal kit in a repo (spec methodology)

1. Install the kit with the updater (recommended, lets you pull improvements later):
   `python <kit>/tools/sgp_kit.py init --source <kit> --dest .` from your repo's root, where `<kit>`
   is the path to the kit folder (e.g. `../sgp-lite/kit`). To pull improvements later:
   `python <kit>/tools/sgp_kit.py update --source <kit> --dest .`.
   (Manual alternative: unzip `sgp-lite.zip` at the repo root, or copy `kit/docs/`, `kit/specs/`,
   `kit/changes/`, `kit/tools/`, `kit/skills/`, `kit/AGENTS.md`, `kit/CLAUDE.md`, `kit/sgp.yaml`,
   `kit/prompts.md`, `kit/METODOLOGIA.md`, `kit/ADOPCION.md`.)
2. Edit `docs/constitution.md`, `AGENTS.md` and the commands in `sgp.yaml` (build, tests, lint,
   `test_por_requisito`) for your stack.
3. Install the hook: `cp tools/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`.

### Step 2 — Kit skills (if your agent supports Agent Skills)

```bash
python tools/sync_skills.py --agent claude-code   # or copilot, codex, cursor, generico, opencode
```

Installs the 6 process skills (`sgp-documento-requerimientos`, `sgp-especificar`, `sgp-qa-spec`,
`sgp-planificar-cambio`, `sgp-ejecutar-tarea`, `sgp-validar-cerrar`) and the 2 behavior skills
(`system-engineering-policy` and `protocolo-ingenieria-senior`). If your agent does not support
skills, use the 6 process steps as prompts from `kit/prompts.md`; the 2 behavior skills have no prompt.

### Step 3 — First real change

> If the request is big or unclear, start with the **requirements document** (prompt 0 / skill
> `sgp-documento-requerimientos`): a supporting text to clarify what is being asked before specifying.
> It is documentation only; if the request is small, skip it.

1. Specify: one-question-at-a-time interview → `specs/<domain>/spec.md` with EARS requirements and an
   ID (`DOM-001`).
2. QA the spec: ambiguities, contradictions, edge cases, conflicts with the constitution.
3. Plan: `python tools/sgp_check.py --nuevo <name>` → fill in the proposal, completion criteria and
   20-30 min tasks with "Done when: ...".
4. Execute: one task per session, test red before code, `sgp_check.py --run` at the end of each one.
5. Validate and close: `sgp_check.py --stage pre-merge` (real per-requirement traceability, not just
   by name) before approving the merge.

See `docs/ejemplo-practico.md` for this same procedure run end to end, with the real output of each
command.

### Step 4 — Repeat and adjust

There is no final phase. Every future change repeats Step 3 and re-reads `specs/` before touching
anything — so the specification never goes stale. Adjust `sgp.yaml` (iteration budget, review limit)
based on what your own usage shows you need.

## Why this is not "the right way"

The evidence base on spec-driven development with AI is still young — Thoughtworks has it in its
Radar in the *Assess* ring (worth exploring, not adopting blindly) as of this writing. This repo
documents a mapping and a template that worked in one concrete case, with its tests and its runnable
example — not a universal recipe. Adjust it with your own evidence before trusting it for production.

## Sources and reference practices

- Thoughtworks Technology Radar — *Spec-driven development* and *OpenSpec*
- GitHub Spec Kit, Kiro (specs with EARS notation), BMAD-METHOD (hints by complexity)
- Böckeler, *Harness engineering for coding agent users* (Martin Fowler blog) — guides vs. sensors
- Anthropic, *Effective harnesses for long-running agents*
- DORA — 2025 report on AI-assisted development
- The open Agent Skills standard (agentskills.io)

None of these sources is cited as a final authority; they were contrasted with each other and several
are blogs or community repositories, not official standards.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) (tests you must run, regenerating the zip, ratchet rules)
and [`SECURITY.md`](SECURITY.md) (the kit's trust boundary). For security issues, use the repo's
private advisory; for everything else, open an issue.

## License

MIT — see [`LICENSE`](LICENSE). Use it, adapt it, break it and tell me what did not work.
