---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs a retained numbered plan under tmp/superpowers/<clear-action-or-task-name>/ and the plan must follow the local English-content execution-plan contract.
---

# Internal Gateway Writing Plans

## Referenced skills

- `internal-gateway-simple-task`: approved `compact` plan consumer.
- `internal-gateway-execute-plans`: approved `extended` plan consumer.

Repository-owned wrapper for retained plan authoring. This skill owns retained
plan creation, profile selection, where the plan lives, file names, content
language, and the authoring-to-execution handoff contract.

## When to use

- Retaining a plan because work crosses turns, needs explicit tracking, or must
  stop before execution.
- Converting a monolithic or overgrown plan into the local numbered-plan
  structure.
- Preparing a plan for `internal-gateway-simple-task` or
  `internal-gateway-execute-plans`.

## When not to use

- Clear, local, quick tasks whose next steps fit in chat and do not need a
  retained artifact.
- Substantive ideation before a plan; use `internal-gateway-idea-brainstorming`.
- Editing imported `superpowers-*` skills.

## Profile Selection

Choose the smallest profile that safely fits the work. Declare the profile in
`02-source-item-ledger.md` under `Plan profile`.

| Profile | When | Required files |
| --- | --- | --- |
| `compact` | Single owner, concrete target, one validation path, low-to-medium risk, and one execution lane. | `01-change-summary.md`, `02-source-item-ledger.md`, `03-execution.md`, `questions.md` |
| `extended` | Cross-family changes, higher risk, low-context executor, multiple validators, or multi-slice execution state. | Compact files plus `04-implementation-contract.md`, additional numbered files by category (`05-...`). |

Do not use `compact` when the executor needs exact sources, target files,
validators, blockers, or external pins that only `04-implementation-contract.md`
can provide.

## Core Contract

- Create the plan under `tmp/superpowers/<clear-action-or-task-name>/`.
- Use English file names. `01-change-summary.md` is written in Italian; all
  other plan files use English.
- `01-change-summary.md`: Italian human-readable decision summary with
  `Problema da risolvere`, `Risultato atteso`, `Risorse coinvolte` table
  (`Risorsa | Azione | Scopo`), `Comportamento scelto`, `Validazione prevista`,
  and `Decisione richiesta`.
- `02-source-item-ledger.md`: control file with `Recommended use`,
  `Plan profile`, `Recommended consumer`, `File map and role`, clarification
  gate status, `Initial evidence pass`, `Reading budget`, target, anti-scope,
  owner, validator, stop conditions, and `Source item ledger`.
- `Recommended consumer`: `internal-gateway-simple-task` for `compact`;
  `internal-gateway-execute-plans` for `extended`.
- `03-execution.md`: first executable file.
- `questions.md`: user-only decisions only. Write `- none` when nothing remains.
- `04-implementation-contract.md` is required for every `extended` plan.
- `done-*`, `evidence-envelope.md`, and `completion-report.md` are packaging
  artifacts only. Do not create them during authoring.

## Workflow

1. Decide: retained plan or chat.
2. Choose folder name and write `01-change-summary.md` in Italian.
3. Write `02-source-item-ledger.md` with profile, recommended consumer, and
   source-item coverage.
4. Run the clarification gate when user decisions remain.
5. Choose profile and consumer together.
6. For `extended`, write `04-implementation-contract.md`.
7. Write executable numbered files in order.
8. Create `questions.md` with `- none` or open user-only decisions.
9. Run scope challenge and plan review gate for non-trivial plans.

## Validation

- Plan lives under `tmp/superpowers/<clear-action-or-task-name>/`.
- `01-change-summary.md` is Italian; other plan files are English.
- `02-source-item-ledger.md` exists with profile, recommended consumer, and
  source-item coverage.
- `Recommended consumer` matches the declared profile.
- `04-implementation-contract.md` exists for every `extended` plan.
- `questions.md` exists and stays separate from executable files.

## Common mistakes

- Retaining a plan for work that should stay in chat.
- Omitting the recommended consumer.
- Using `compact` when execution actually needs an implementation contract.
- Creating `done-*` markers during authoring.
