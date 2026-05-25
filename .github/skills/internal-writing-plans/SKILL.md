---
name: internal-writing-plans
description: Use when repository-owned work needs a retained numbered plan under tmp/superpowers/<clear-action-or-task-name>/ and the plan must follow the local Italian-content execution-plan contract.
---

# Internal Writing Plans

## Referenced skills

This index lists every other skill that this file asks the agent to load, route
to, compare against, or delegate to.

- `internal-executing-plans`: repository-local application owner for approved retained plans.
- `internal-gateway-critical-master`: critical challenge owner before writing non-trivial or governance-sensitive retained plans.
- `superpowers-brainstorming`: alternate owner for general design or spec work under `tmp/superpowers/specs/`.
- `superpowers-writing-plans`: imported plan-authoring depth subordinate to the local retained-plan contract.

Use this skill as the repository-owned wrapper for plan authoring in this
repository.

Treat `superpowers-writing-plans` as imported depth and keep repo-local drift
fixes narrow. This skill owns when a plan is retained, where it lives, how files
are split, which file names are valid, what language the content uses, and what
must stay outside the execution loop.

## When to use

- Writing or rewriting a retained repository-owned execution plan under `tmp/superpowers/` when the work is non-banal.
- Retaining a plan because the work crosses turns, spans multiple macro-categories, needs handoff, tracking, or provenance, or carries tradeoffs or uncertainties that should stay reviewable.
- Converting a monolithic or overgrown plan into the local numbered-plan structure.
- Converting a strategic, review-only, or monolithic retained plan into an executable retained plan without losing source decisions.
- Preparing a plan that will later be executed by `internal-executing-plans`.

## When not to use

- General design or spec work under `tmp/superpowers/specs/`; use `superpowers-brainstorming` when that workflow is relevant.
- Clear, local, quick, or banal tasks whose next steps fit in chat.
- Local execution with no retained plan artifact.
- Imported or sync-managed planning assets; do not edit `superpowers-*` skills to impose this policy.

## Local retained-plan contract

- Create or reuse a retained plan folder under `tmp/superpowers/<clear-action-or-task-name>/` only when the plan needs to survive the current turn.
- Treat the plan being created or rewritten as the only retained-plan corpus in scope.
- Do not inspect sibling retained plan folders to infer scope, copy structure, or collect context unless the user explicitly names them for comparison or reuse.
- When another retained plan is valid evidence, name its exact path in `Budget lettura` and explain why; otherwise leave other `tmp/` plans out of scope.
- Keep planning ephemeral in chat when the task is clear, local, quick, or banal.
- Retain a plan only when at least one of these is true: the work crosses turns, spans multiple macro-categories, needs handoff, tracking, or provenance, or includes tradeoffs or uncertainties that should stay reviewable.
- Use English file names for every new or rewritten retained plan file. The plan content is Italian by default unless the user explicitly asks for another language.
- Start every retained plan with `01-change-summary.md`. This file is only a short summary of the modifications the plan proposes, the problem they solve, and why that direction is worth approval.
- Keep `01-change-summary.md` concise enough to review quickly. Do not put the file-role map, reading budget, full execution checklist, long rationale, unresolved questions, or copied repository context in it.
- For non-trivial retained plans, create `02-source-item-ledger.md` immediately after the summary. It is the control and traceability file for the folder.
- `02-source-item-ledger.md` must declare `clarification required`, `clarification satisfied`, or `clarification not applicable` before the plan can move to execution.
- Use `clarification required` when unresolved user-only decisions can change scope, owner, target state, validation, rollout, or anti-scope. Stop before writing executable plan content until those decisions are answered or the user explicitly accepts the recommended defaults.
- Use `clarification satisfied` only when the relevant decisions were answered or explicitly accepted in the active loop, the user gave a closure or proceed signal, the answers still match the current plan scope, and no user-only decision needs another loop.
- Use `clarification not applicable` only when the work is concrete, mechanical, or fully recoverable from repository evidence.
- For non-trivial or ambiguous retained plans, `02-source-item-ledger.md` must include a lightweight spec baseline: objective, assumptions that affect delivery, success criteria, boundaries or anti-scope, validation path, and open questions or `none`.
- Before writing a non-trivial or governance-sensitive retained plan, use `internal-gateway-critical-master` to challenge the proposed target, anti-scope, owner, validation path, and main tradeoff. If the outcome is `reformulate-plan` or `continue-critical`, resolve that result before writing plan files. If the plan is simple or mechanical, record critical challenge as not applicable in the ledger.
- Success criteria must be concrete enough to verify. Reframe vague goals into observable conditions when repository evidence supports it, or move the uncertainty to `questions.md` before execution.
- Action verbs such as compress, rewrite, refactor, harden, align, simplify, or validate must have observable acceptance evidence. Name the expected diff, target file state, validator assertion, or explicit non-action before execution.
- `02-source-item-ledger.md` must include the smallest useful reading path: what to inspect first, which evidence pass proves the plan is still valid, and which files can be deferred.
- `02-source-item-ledger.md` must map every source item to one of: executable change, adaptation in another plan file, intentional non-action, deferred follow-up, rejection, or blocker.
- Each ledger row must include a stable item id, source item, intended observable change, evidence class, acceptance evidence, status, and route. Initial statuses are usually `PENDING`.
- The ledger must name intended observable evidence for every executable item:
  diff evidence, file evidence, validator evidence, manual evidence, or an
  explicit validation gap.
- The ledger is the coverage lock. Do not retire, delete, or replace a source strategic artifact until every source item has a ledger row and a destination or explicit non-action.
- After the ledger file, use `03-execution.md` when one executable macro-category is enough.
- When the work spans more than one executable macro-category, continue with `03-...`, `04-...`, and later numbered files by category, for example `03-implementation.md`, `04-validation.md`, and `05-rollout.md`.
- Do not keep one monolithic plan file when the work spans multiple macro-categories.
- For executable work, make dependency order, acceptance criteria, and verification checkpoints explicit enough that a later executor can prove each item before moving it to `done-*`.
- Acceptance criteria must disallow clarification-only completion for executable verbs. If a step says to compress, rewrite, refactor, harden, align, or simplify, the plan must say what observable change proves it.
- For each executable step, name the acceptance condition, verification path, and target files or owner when known. Keep steps small enough to verify without mixing unrelated owners or cleanup.
- Keep unresolved questions, doubts, and user decisions in `questions.md`.
- `questions.md` is not an execution-plan file and must stay outside the plan-and-apply loop.
- Use `done-*`, `evidence-envelope.md`, and `completion-report.md` only as execution-state artifacts after `apply-plan`; do not use them as authoring files.
- Use `references/scope-challenge.md` before approving non-trivial retained plans for execution.
- Use `references/plan-review-gate.md` when plan clarity, coherence, validability, or evidence needs a lightweight review before handoff.

## File-role conventions

- Treat `01-change-summary.md` as the first human-review file. Read it first for generic requests such as "analyze this plan", "review this plan", "write this plan", or "apply this plan".
- Treat `02-source-item-ledger.md` as the control, file-role, evidence-budget, and source-item coverage owner for the folder.
- Treat `02-source-item-ledger.md` as the traceability owner for strategic-to-operational conversions.
- In `02-source-item-ledger.md`, include `Uso consigliato` with the next expected treatment, such as `review`, `apply-plan`, `resume`, or `rewrite`.
- In `02-source-item-ledger.md`, include `Mappa file e ruolo` so the reader can classify each file as summary, ledger, execution, validation, rollout, questions, or status artifact without guessing.
- Treat `questions.md` as the only place for unresolved questions and user decisions.
- Treat `done-*`, `evidence-envelope.md`, and `completion-report.md` as status artifacts that describe applied work, not pending plan intent.
- For legacy folders, read `01-riassunto-direzione-e-decisione.md`, `02-matrice-operativa.md`, `02-esecuzione.md`, and `dubbi-e-domande.md` only as backward-compatible inputs. New or rewritten plans must use English file names.
- If the summary file, ledger, or file-role map is missing from a non-trivial plan, the retained plan is not executor-friendly yet and should be revised before `apply-plan`.

## Token And Reading Discipline

- Classify the folder before broad reading: `draft-to-review`, `write-or-rewrite`, `approved-to-apply`, `resume`, `completed-status`, or `unknown`.
- Do a short evidence pass before reading many files. Limit the first pass to target existence, the riskiest claim in the summary or ledger, and the nearest validator or explicit validation gap.
- For retained artifacts under `tmp/`, use `rg --no-ignore` or an equivalent ignored-file-aware search when checking claims.
- Put the evidence pass and first-read budget in `02-source-item-ledger.md` under `Evidence pass iniziale` and `Budget lettura`.
- Make `Budget lettura` exclusive: list the current plan files and any exact external artifacts allowed, and state that sibling retained plans are out of scope when not listed.
- Coverage before compression: when rewriting an existing strategic or monolithic plan, extract the source items first and preserve them in `02-source-item-ledger.md` before shortening, splitting, or deleting the source artifact.
- Observable acceptance before execution: convert broad verbs into measurable evidence while the plan is still cheap to fix, not after the executor has already closed `done-*` files.
- Prefer the smallest useful retained plan shape: brief summary, source-item ledger, current execution or backlog, and validation. Add more numbered files only for independent macro-categories.
- Run the clarification gate only after the evidence pass when real user decisions remain, then declare the gate status. Do not ask questions that repository evidence can answer.
- Keep deferred improvements, retrospectives, and lessons separate from executable steps unless they are required for the requested outcome.

## Numbered-file shape

- Optimize retained plan files for scanability and decision review rather than exhaustive prose.
- Prefer explicit headings and short bullets; avoid long paragraphs.
- Keep rationales brief and avoid duplicating context already captured in `AGENTS.md`, `.github/copilot-instructions.md`, or neighboring repository-owned assets.

### Change summary file

- `01-change-summary.md` must include only these headings:
- `Problema da risolvere`
- `Modifiche proposte`
- `Perche questa strada`
- `Validazione`
- `Decisione richiesta`
- Keep it to the shortest useful form, usually no more than 10 bullets total.

### Source item ledger file

- `02-source-item-ledger.md` must include these headings:
- `Uso consigliato`
- `Mappa file e ruolo`
- `Clarification gate`
- `Critical challenge`
- `Evidence pass iniziale`
- `Budget lettura`
- `Target e anti-scope`
- `Owner e validator`
- `Stop conditions`
- `Source item ledger`
- The ledger table must preserve every requested or source item with stable ids before executable files are finalized.

### Executable numbered files

- Each executable numbered file after the ledger file must include these headings:
- `Obiettivo`
- `Logica scelta`
- `Assunzioni chiave`
- `Passi eseguibili`
- `Validazione`
- Treat `01-change-summary.md` and `02-source-item-ledger.md` as numbered control files, not executable task lists. During `apply-plan`, use them for classification, coverage, and evidence, then close them through the same `done-*` evidence loop when the folder completes.
- Keep each section to 5-7 bullets when practical.
- Keep bullets to 1-2 lines when practical.
- Make each executable step easy to challenge, verify, or remove without rewriting the whole file.

## Relationship to OBRA

- Use this skill first for repository-owned planning policy.
- Reuse `superpowers-writing-plans` only for the remaining plan-authoring mechanics that do not conflict with the local contract.
- If the plan will be executed in the same repository-owned workflow, hand off to `internal-executing-plans` instead of routing directly to `superpowers-executing-plans`.

## Workflow

1. Decide first whether retained planning is justified or whether in-chat planning is enough.
2. Choose a clear task folder name under `tmp/superpowers/`.
3. Run the critical challenge before writing plan files when the retained plan is non-trivial or governance-sensitive.
4. Write `01-change-summary.md` first with only the concise modification summary and approval decision.
5. Write `02-source-item-ledger.md` next with file roles, evidence pass, reading budget, gate status, critical challenge status, source items, and observable acceptance.
6. If the input is an existing strategic, review-only, or monolithic plan, lock source-item coverage in the ledger before defining later execution phases.
7. Define the executable macro-categories next and choose the smallest post-ledger file shape that fits the work.
8. Use `03-execution.md` when one executable macro-category is enough, or create one numbered plan file per category when more than one macro-category exists.
9. Give each numbered file the shape above and keep every section compact.
10. Put open questions and decision requests only in `questions.md`.
11. Keep executable next steps in the numbered plan files without mixing unresolved questions into them.
12. Run the scope challenge and plan review gate when the retained plan is non-trivial or will be handed to `internal-executing-plans`.

## Validation

- The plan exists only when retained planning is justified beyond the current turn.
- The plan lives under `tmp/superpowers/<clear-action-or-task-name>/`.
- Every new or rewritten retained plan file name is English.
- `01-change-summary.md` exists and contains only a concise proposed-change summary, rationale, validation path, and decision request.
- `02-source-item-ledger.md` exists and acts as the control and coverage file for the retained plan.
- For non-trivial retained plans, the ledger declares `clarification required`, `clarification satisfied`, or `clarification not applicable`.
- Non-trivial or governance-sensitive retained plans run `internal-gateway-critical-master` before plan files are written, or record why critical challenge is not applicable.
- The ledger declares `Uso consigliato`, `Mappa file e ruolo`, `Evidence pass iniziale`, and `Budget lettura`.
- The ledger's `Budget lettura` confines future readers to this plan and exact named evidence; other retained plan folders are excluded unless specifically indicated.
- The ledger includes every source/requested item with item id, observable acceptance, evidence class, status, and route.
- `03-execution.md` is used when one executable macro-category is enough; `03-...`, `04-...`, `05-...` style plan files exist when more than one macro-category exists.
- Strategic-to-operational conversions preserve source-item coverage through `02-source-item-ledger.md` before the source artifact is retired.
- The source strategic artifact is not deleted, replaced, or compressed beyond recognition until the ledger maps each source item to a destination or explicit non-action.
- Plan content is in Italian unless the user asked otherwise.
- The numbered files follow the local shape contract with explicit headings and short bullets.
- `questions.md` exists when needed and remains separate from executable plan files.
- Non-trivial retained plans can answer the scope challenge fields: target, anti-scope, owner, validator, and stop conditions.
- The plan does not rely on imported `superpowers-*` skills as the policy owner; any repo-local drift fix stays narrow and subordinate to this wrapper.

## Common mistakes

- Creating a retained plan artifact for a clear, local, quick task that should stay in chat.
- Turning `01-change-summary.md` into a long control file instead of a concise summary of proposed modifications.
- Omitting `02-source-item-ledger.md`, causing the executor to lose the original item list after active files are emptied or deleted.
- Omitting the initial evidence pass or reading budget, causing the next agent to read the whole folder before knowing the lane.
- Compressing or deleting a strategic source plan before extracting the source-item ledger.
- Reading sibling retained plans to "understand context" when the user only passed one plan folder.
- Writing the whole plan in one Markdown file.
- Writing long narrative paragraphs or duplicating canonical context instead of keeping the plan scannable.
- Mixing executable checklist items with open questions.
- Putting the plan under `docs/` instead of `tmp/superpowers/`.
- Using Italian file names even though only plan content should default to Italian.
- Switching the whole repository to Italian instead of keeping the exception local to plan content.
