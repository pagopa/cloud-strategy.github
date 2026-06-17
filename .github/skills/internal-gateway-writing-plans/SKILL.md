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
`02-execution.md` for `compact` and `02-control.md` for `extended` under
`Plan profile`.

`init` creates a scaffold only. A retained plan is execution-ready only after
`handoff-check` returns ready.

New `compact` plans should use `tmp/superpowers/mini-plan-*`.

| Profile | When | Required files |
| --- | --- | --- |
| `compact` | Single owner, concrete target, one validation path, low-to-medium risk, and one execution lane. Best fit for small/fast executors after positive handoff validation. | `01-change-summary.md`, `02-execution.md` |
| `extended` | Cross-family changes, higher risk, lower-context execution, multiple validators, or multi-slice execution state. Thinking-first profile with explicit control files and deterministic read order. | `01-change-summary.md`, `02-control.md`, `03-execution.md`, additional numbered files by category (`04-...`). |

Do not use `compact` when the executor needs exact sources, target files,
validators, blockers, or external pins that only `02-control.md`
can provide.

## Core Contract

- Create the plan under `tmp/superpowers/<clear-action-or-task-name>/`.
- Use English file names. `01-change-summary.md` is written in Italian; all
  other plan files use English.
- For debugging, drift, or data-mismatch work, produce a compact diagnosis
  capsule before retained-plan authoring starts: symptom, target artifact,
  compared sources or layers, cheapest falsifier, and stop rule. Keep it only
  in chat or request context; do not create another retained file for it.
- `01-change-summary.md`: Italian human-readable decision summary with
  `Problema da risolvere`, `Risultato atteso`, `Risorse coinvolte` table
  (`Risorsa | Azione | Scopo`), `Comportamento scelto`, `Validazione prevista`,
  `Esecuzione prevista`, and `Decisione richiesta`.
- `02-execution.md` for `compact` must include these exact headings:
  `Plan profile`, `Target and anti-scope` (with `### Target` and
  `### Anti-scope`), `Owner and validator`, `Stop conditions`, `Objective`,
  `Chosen logic`, `Key assumptions`, `Executable steps`, `Validation`, and
  `Source item coverage`.
- `02-execution.md` executable steps use numbered items with explicit labels:
  `Target:`, `Acceptance:`, `Validation:`, and `Fallback:`.
- `02-control.md` for `extended`: control file with `Recommended use`,
  `Plan profile`, `File map and role`, clarification gate status,
  `Initial evidence pass`, `Reading budget`, target, anti-scope, owner,
  validator, stop conditions, and `Source item ledger`.
- Preserve known-context handoff quality in `Initial evidence pass` and `Reading budget` so executors can avoid repeated broad rereads.
- `03-execution.md`: first executable file for `extended`.
- For `extended`, implementation-contract sections are merged into `02-control.md`
  with these exact headings: `Sources`, `Candidate targets`,
  `Validation commands`, `Blockers and fallback rules`, and `External pins`.
- Apply a say-once rule: each control fact (target, owner, validator, blockers,
  pins, and source-item coverage) is written once in the owning file, and step
  files do not restate target/owner/validator.
- Keep profile token weight explicit: `compact` stays small/fast with two files;
  `extended` keeps control weight in `02-control.md` and execution weight in
  numbered step files.
- `done-*`, `evidence-envelope.md`, and `completion-report.md` are packaging
  artifacts only. Do not create them during authoring.

## Workflow

1. Decide: retained plan or chat.
2. For debugging, drift, or data-mismatch work, write the diagnosis capsule
   before `01-change-summary.md`.
3. For new plans, run bundle-local `init` first to create the scaffold.
4. Choose folder name and write `01-change-summary.md` in Italian.
5. For `compact`, write `02-execution.md` with profile, control header, steps,
  and source-item coverage.
6. For `extended`, write `02-control.md` with profile, control facts, merged
  implementation-contract sections, and source-item coverage.
7. Run the clarification gate when user decisions remain.
8. For `extended`, write executable numbered files in order starting with
  `03-execution.md`.
9. Keep each executable file scoped to its slice and validation path so executors can run targeted rereads.
10. Fold open-user decisions into one summary line instead of a separate
  `questions.md` file for `compact`.
11. Run scope challenge and plan review gate for non-trivial plans.
12. Run `audit` first, then run `handoff-check`; execute only when ready.
13. Treat token warnings as review inputs for compression or split decisions, not as proof of measured savings.

## Validation

- Plan lives under `tmp/superpowers/<clear-action-or-task-name>/`.
- `01-change-summary.md` is Italian; other plan files are English.
- `compact` uses `01-change-summary.md` + `02-execution.md` only.
- `compact` `02-execution.md` uses the exact validator headings and step labels.
- `extended` uses `01-change-summary.md`, `02-control.md`, and
  `03-execution.md` plus optional higher-numbered slices.
- The diagnosis capsule exists before authoring when debugging, drift, or
  data-mismatch work is being retained, and it stays in chat/request context.
- `extended` includes merged contract sections in `02-control.md`.
- Step files do not restate target, owner, or validator.

## Common mistakes

- Retaining a plan for work that should stay in chat.
- Skipping the diagnosis capsule and turning an unproven mismatch into a
  retained plan.
- Using `compact` when execution actually needs an implementation contract.
- Creating `done-*` markers during authoring.
