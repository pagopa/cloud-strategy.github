---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs a retained numbered plan under tmp/superpowers/<clear-action-or-task-name>/ and the plan must follow the local English-content execution-plan contract.
---

# Internal Gateway Writing Plans

## Referenced skills

- `internal-gateway-simple-task`: concrete single-lane execution owner when no retained plan is needed.
- `internal-gateway-execute-plans`: retained-plan execution owner that infers execution strategy from profile, folder shape, and validation path.

Repository-owned wrapper for retained plan authoring. This skill owns retained
plan creation, profile selection, where the plan lives, file names, content
language, and the authoring-to-execution handoff contract. It does not select a
separate execution consumer field inside the retained plan.

## When to use

- Retaining a plan because work crosses turns, needs explicit tracking, or must
  stop before execution.
- Converting a monolithic or overgrown plan into the local numbered-plan
  structure.
- Preparing a retained plan for execution handoff.

## When not to use

- Clear, local, quick tasks whose next steps fit in chat and do not need a
  retained artifact.
- Substantive ideation before a plan; use `internal-gateway-idea-brainstorming`.
- Editing imported `superpowers-*` skills.

## Profile Selection

Choose the smallest profile that safely fits the work. Declare the profile in
`02-source-item-ledger.md` under `Plan profile`.

`init` creates a scaffold only. A retained plan is execution-ready only after
`handoff-check` returns ready and `questions.md` is `- none`.

New `compact` plans should use `tmp/superpowers/mini-plan-*`.

| Profile | When | Required files |
| --- | --- | --- |
| `compact` | Single owner, concrete target, one validation path, low-to-medium risk, and one execution lane. Best fit for small/fast executors after positive handoff validation. | `01-change-summary.md`, `02-source-item-ledger.md`, `03-execution.md`, `questions.md` |
| `extended` | Cross-family changes, higher risk, lower-context execution, multiple validators, or multi-slice execution state. Thinking-first profile with explicit control files and deterministic read order. | Compact files plus `04-implementation-contract.md`, additional numbered files by category (`05-...`). |

Do not use `compact` when the executor needs exact sources, target files,
validators, blockers, or external pins that only `04-implementation-contract.md`
can provide.

## Core Contract

- Create the plan under `tmp/superpowers/<clear-action-or-task-name>/`.
- Use English file names. `01-change-summary.md` is written in Italian; all
  other plan files use English.
- For debugging, drift, or data-mismatch work, produce a compact diagnosis
  capsule before the retained plan: symptom, target artifact, compared
  sources or layers, cheapest falsifier, and stop rule. Keep it in chat or the
  request context; do not create another retained file for it.
- `01-change-summary.md`: Italian human-readable decision summary with
  `Problema da risolvere`, `Risultato atteso`, `Risorse coinvolte` table
  (`Risorsa | Azione | Scopo`), `Comportamento scelto`, `Validazione prevista`,
  `Esecuzione prevista`, and `Decisione richiesta`.
- `02-source-item-ledger.md`: control file with `Recommended use`,
  `Plan profile`, `File map and role`, clarification
  gate status, `Initial evidence pass`, `Reading budget`, target, anti-scope,
  owner, validator, stop conditions, and `Source item ledger`.
- `03-execution.md`: first executable file.
- `questions.md`: user-only decisions only. Write `- none` when nothing remains.
- `04-implementation-contract.md` is required for every `extended` plan.
- `done-*`, `evidence-envelope.md`, and `completion-report.md` are packaging
  artifacts only. Do not create them during authoring.

## Workflow

1. Decide: retained plan or chat.
2. For debugging, drift, or data-mismatch work, write the diagnosis capsule
   before `01-change-summary.md`.
3. For new plans, run bundle-local `init` first to create the scaffold.
4. Choose folder name and write `01-change-summary.md` in Italian.
5. Write `02-source-item-ledger.md` with profile and source-item coverage.
6. Run the clarification gate when user decisions remain.
7. For `extended`, write `04-implementation-contract.md`.
8. Write executable numbered files in order.
9. Create `questions.md` with `- none` or open user-only decisions.
10. Run scope challenge and plan review gate for non-trivial plans.
11. Run `audit` first, then run `handoff-check`; execute only when ready.
12. Treat token warnings as review inputs for compression or split decisions, not as proof of measured savings.

## Validation

- Plan lives under `tmp/superpowers/<clear-action-or-task-name>/`.
- `01-change-summary.md` is Italian; other plan files are English.
- `02-source-item-ledger.md` exists with profile and source-item coverage.
- The diagnosis capsule exists before authoring when debugging, drift, or
  data-mismatch work is being retained.
- `04-implementation-contract.md` exists for every `extended` plan.
- `questions.md` exists and stays separate from executable files.

## Common mistakes

- Retaining a plan for work that should stay in chat.
- Skipping the diagnosis capsule and turning an unproven mismatch into a
  retained plan.
- Using `compact` when execution actually needs an implementation contract.
- Creating `done-*` markers during authoring.
