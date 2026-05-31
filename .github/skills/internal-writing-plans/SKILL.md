---
name: internal-writing-plans
description: Use when repository-owned work needs a retained numbered plan under tmp/superpowers/<clear-action-or-task-name>/ and the plan must follow the local English-content execution-plan contract.
---

# Internal Writing Plans

## Referenced skills

This index lists every other skill that this file asks the agent to load, route
to, compare against, or delegate to.

- `internal-executing-plans`: repository-local application owner for approved retained plans.
- `superpowers-brainstorming`: alternate owner for general design or spec work under `tmp/superpowers/specs/`.
- `superpowers-writing-plans`: imported plan-authoring depth subordinate to the local retained-plan contract.

Repository-owned wrapper for retained plan authoring. Treat `superpowers-writing-plans`
as imported depth; keep repo-local drift narrow. This skill owns when a plan is
retained, where it lives, file names, content language, and the authoring-to-handoff
contract.

## When to use

- Retaining a plan because work crosses turns, spans multiple macro-categories,
  needs handoff, tracking, or carries tradeoffs or uncertainties that should stay
  reviewable.
- Converting a monolithic or overgrown plan into the local numbered-plan structure.
- Preparing a plan for `internal-executing-plans`.

## When not to use

- Clear, local, quick tasks whose next steps fit in chat.
- General design or spec work; use `superpowers-brainstorming`.
- Editing imported `superpowers-*` skills.

## Profile Selection

Choose the smallest profile that safely fits the work. Declare the profile in
`02-source-item-ledger.md` under `Plan profile`.

| Profile | When | Required files |
| --- | --- | --- |
| `compact` (default) | Single owner, concrete target, clear validation, low-to-medium risk. | `01-change-summary.md`, `02-source-item-ledger.md`, `03-execution.md`, `questions.md` |
| `extended` | Risk, multi-owner, hidden assumptions, low-context executor, or cross-family changes. | Compact files plus `04-implementation-contract.md`, additional numbered files by category (`05-...`). |
| `legacy` | Folder without a declared profile. | Classified on read via `references/compact-plan-contract.md` and `internal-executing-plans/references/legacy-plan-compatibility.md`. |

Do not use `compact` when the executor needs exact sources, target files,
validators, blockers, or external pins that only `04-implementation-contract.md`
can provide. Escalation rules live in `references/compact-plan-contract.md`.

## Core Contract

- Create the plan under `tmp/superpowers/<clear-action-or-task-name>/`.
- Use English file names. Plan content is English by default.
- `01-change-summary.md`: concise proposed-change summary with problem, rationale,
  validation path, and decision request. Keep to ~10 bullets.
- `02-source-item-ledger.md`: control file with `Recommended use`, `Plan profile`,
   `File map and role`, clarification gate status, `Initial evidence pass`,
   `Reading budget`, target, anti-scope, owner, validator, stop conditions, and
   `Source item ledger` table.
- Ledger table: stable item id, source item, observable acceptance, evidence class,
  acceptance evidence, status, route per row.
- Clarification gate: `clarification required` (unresolved user decisions block
  executable content), `clarification satisfied`, or `clarification not applicable`
  (concrete, mechanical work).
- `03-execution.md`: first executable file. Add `05-...` etc. when span exceeds one
  macro-category; `04-implementation-contract.md` stays reserved as the support
  contract.
- `questions.md`: user-only decisions only. Write `- none` when nothing remains.
  Excluded from the execution loop.
- For `extended` profile: `04-implementation-contract.md` lists exact sources,
  target files, patch intent, validation order, blockers, external pins, and final
  report format.
- `done-*`, `evidence-envelope.md`, `completion-report.md` are final packaging
  artifacts only; do not create them during authoring.
- Use `references/scope-challenge.md` before approving non-trivial plans.
- Use `references/plan-review-gate.md` before handoff.

## Workflow

1. Decide: retained plan or chat.
2. Choose folder name, write `01-change-summary.md`.
3. Write `02-source-item-ledger.md` with all fields, gate status, profile, and
   source items.
4. Run clarification gate when user decisions remain; stop before executable
   content until resolved or explicitly accepted.
5. Choose profile. For `extended`, write `04-implementation-contract.md`.
6. Write executable numbered files in order, keeping sections compact.
7. Create `questions.md` with `- none` or open decisions.
8. Run scope challenge and plan review gate for non-trivial plans.
9. Emit a Decision Brief before handoff to `internal-executing-plans`.

Schema, templates, and escalation details are in `references/compact-plan-contract.md`.

## Validation

- Plan is retained only when justified beyond the current turn.
- Plan lives under `tmp/superpowers/<clear-action-or-task-name>/`.
- English file names; English plan content.
- `01-change-summary.md` is concise and not overloaded with control details.
- `02-source-item-ledger.md` exists with profile, all required fields, and
  source-item coverage.
- Clarification gate status is declared.
- `04-implementation-contract.md` exists for every `extended` plan.
- `questions.md` exists, separate from executable files.
- `done-*` artifacts exist only after execution packaging.
- Scope challenge and plan review gate were applied before handoff.

## Common mistakes

- Retaining a plan for a task that should stay in chat.
- Overloading `01-change-summary.md` with control details or execution checklists.
- Omitting `02-source-item-ledger.md` or source-item coverage.
- Omitting `04-implementation-contract.md` for an `extended` plan.
- Creating `done-*` markers during authoring instead of final packaging.
- Reading sibling retained plans without explicit `Reading budget`.
- Treating `questions.md` as optional or as an executable file.
