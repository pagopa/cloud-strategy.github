---
name: internal-writing-plans
description: Use when repository-owned work needs a retained numbered plan under tmp/superpowers/<clear-action-or-task-name>/ and the plan must follow the local Italian-default execution-plan contract.
---

# Internal Writing Plans

Use this skill as the repository-owned wrapper for plan authoring in this repository.

Treat `superpowers-writing-plans` as imported depth and keep any repo-local drift fixes narrow. This skill adds the local contract for when a plan is retained, where it lives, how numbered files are split, what language they use, and what must stay outside the execution loop.

## When to use

- Writing or rewriting a retained repository-owned execution plan under `tmp/superpowers/` when the work is non-banal.
- Retaining a plan because the work crosses turns, spans multiple macro-categories, needs handoff, tracking, or provenance, or carries tradeoffs or uncertainties that should stay reviewable.
- Converting a monolithic or overgrown plan into the local numbered-plan structure.
- Preparing a plan that will later be executed by `internal-executing-plans`.

## When not to use

- General design or spec work under `tmp/superpowers/specs/`; use `superpowers-brainstorming` when that workflow is relevant.
- Clear, local, quick, or banal tasks whose next steps fit in chat.
- Local execution with no retained plan artifact.
- Imported or sync-managed planning assets; do not edit `superpowers-*` skills to impose this policy.

## Local retained-plan contract

- Create or reuse a retained plan folder under `tmp/superpowers/<clear-action-or-task-name>/` only when the plan needs to survive the current turn.
- Keep planning ephemeral in chat when the task is clear, local, quick, or banal.
- Retain a plan only when at least one of these is true: the work crosses turns, spans multiple macro-categories, needs handoff, tracking, or provenance, or includes tradeoffs or uncertainties that should stay reviewable.
- Start every retained plan with `01-riassunto-direzione-e-decisione.md` so the user can understand the full direction and decide before execution.
- `01-riassunto-direzione-e-decisione.md` must be exhaustive enough to explain the target state, tradeoffs, execution shape, validation path, and the decision the user is being asked to make.
- The summary file must also include the smallest useful reading path: what to inspect first, which evidence pass proves the plan is still valid, and which files can be deferred.
- After the summary file, use `02-esecuzione.md` when one executable macro-category is enough.
- When the work spans more than one executable macro-category, continue with `02-...`, `03-...`, and later numbered files by category, for example `02-implementazione.md`, `03-validazione.md`, and `04-rollout.md`.
- Do not keep one monolithic plan file when the work spans multiple macro-categories.
- Write those plan files in Italian by default unless the user explicitly asks for another language.
- Keep unresolved questions, doubts, and user decisions in `dubbi-e-domande.md`.
- `dubbi-e-domande.md` is not an execution-plan file and must stay outside the plan-and-apply loop.
- Use `done-*`, `evidence-envelope.md`, and `completion-report.md` only as execution-state artifacts after `apply-plan`; do not use them as authoring files.
- Use `references/scope-challenge.md` before approving non-trivial retained plans
  for execution.
- Use `references/plan-review-gate.md` when plan clarity, coherence,
  validability, or evidence needs a lightweight review before handoff.

## File-role conventions

- Treat `01-riassunto-direzione-e-decisione.md` as the control file for the folder. Read it first for generic requests such as "analyze this plan", "review this plan", "write this plan", or "apply this plan".
- In that summary file, include `Uso consigliato` with the next expected treatment, such as `review`, `apply-plan`, `resume`, or `rewrite`.
- In that summary file, include `Mappa file e ruolo` so the reader can classify each file as summary, execution, validation, rollout, questions, or status artifact without guessing.
- Treat `dubbi-e-domande.md` as the only place for unresolved questions and user decisions.
- Treat `done-*`, `evidence-envelope.md`, and `completion-report.md` as status artifacts that describe applied work, not pending plan intent.
- If the summary file or file-role map is missing, the retained plan is not executor-friendly yet and should be revised before `apply-plan`.

## Token And Reading Discipline

- Classify the folder before broad reading: `draft-to-review`, `write-or-rewrite`, `approved-to-apply`, `resume`, `completed-status`, or `unknown`.
- Do a short evidence pass before reading many files. Limit the first pass to target existence, the riskiest claim in the summary, and the nearest validator or explicit validation gap.
- For retained artifacts under `tmp/`, use `rg --no-ignore` or an equivalent ignored-file-aware search when checking claims.
- Put the evidence pass and first-read budget in `01-riassunto-direzione-e-decisione.md` under `Evidence pass iniziale` and `Budget lettura`.
- Prefer the smallest useful retained plan shape: summary, current execution or backlog, and validation. Add more numbered files only for independent macro-categories.
- Use `grill-me` only after the evidence pass when real user decisions remain. Do not ask questions that repository evidence can answer.
- Keep deferred improvements, retrospectives, and lessons separate from executable steps unless they are required for the requested outcome.

## Numbered-file shape

- Optimize retained plan files for scanability and decision review rather than exhaustive prose.
- Prefer explicit headings and short bullets; avoid long paragraphs.
- Keep rationales brief and avoid duplicating context already captured in `AGENTS.md`, `.github/copilot-instructions.md`, or neighboring repository-owned assets.

### Summary control file

- `01-riassunto-direzione-e-decisione.md` must include these headings:
- `Obiettivo`
- `Direzione proposta`
- `Decisione richiesta`
- `Uso consigliato`
- `Mappa file e ruolo`
- `Evidence pass iniziale`
- `Budget lettura`
- `Validazione`
- `Stop conditions`

### Executable numbered files

- Each executable numbered file after the summary control file must include these headings:
- `Obiettivo`
- `Logica scelta`
- `Assunzioni chiave`
- `Passi eseguibili`
- `Validazione`
- Treat `01-riassunto-direzione-e-decisione.md` as a numbered control file, not as an executable task list. During `apply-plan`, use it for classification and evidence, then close it through the same `done-*` evidence loop when the folder completes.
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
3. Write `01-riassunto-direzione-e-decisione.md` first and use it to state direction, decision request, recommended treatment, file-role map, evidence pass, and reading budget before detailed plan files exist.
4. Define the executable macro-categories next and choose the smallest post-summary file shape that fits the work.
5. Use `02-esecuzione.md` when one executable macro-category is enough, or create one numbered plan file per category when more than one macro-category exists.
6. Give each numbered file the shape above and keep every section compact.
7. Put open questions and decision requests only in `dubbi-e-domande.md`.
8. Keep executable next steps in the numbered plan files without mixing unresolved questions into them.
9. Run the scope challenge and plan review gate when the retained plan is
   non-trivial or will be handed to `internal-executing-plans`.

## Validation

- The plan exists only when retained planning is justified beyond the current turn.
- The plan lives under `tmp/superpowers/<clear-action-or-task-name>/`.
- `01-riassunto-direzione-e-decisione.md` exists and acts as the control file for the retained plan.
- The summary file is exhaustive enough for the user to decide whether to approve, challenge, rewrite, or apply the plan.
- The summary file declares `Uso consigliato` and `Mappa file e ruolo`.
- The summary file declares `Evidence pass iniziale` and `Budget lettura`.
- `02-esecuzione.md` is used when one executable macro-category is enough; `02-...`, `03-...`, `04-...` style plan files exist when more than one executable macro-category exists.
- Plan files are in Italian unless the user asked otherwise.
- The numbered files follow the local shape contract with explicit headings and short bullets.
- `dubbi-e-domande.md` exists when needed and remains separate from executable plan files.
- Non-trivial retained plans can answer the scope challenge fields: target,
  anti-scope, owner, validator, and stop conditions.
- The plan does not rely on imported `superpowers-*` skills as the policy owner; any repo-local drift fix stays narrow and subordinate to this wrapper.

## Common mistakes

- Creating a retained plan artifact for a clear, local, quick task that should stay in chat.
- Skipping `01-riassunto-direzione-e-decisione.md` or making it too thin to support a decision.
- Omitting the initial evidence pass or reading budget, causing the next agent to read the whole folder before knowing the lane.
- Writing the whole plan in one Markdown file.
- Writing long narrative paragraphs or duplicating canonical context instead of keeping the plan scannable.
- Mixing executable checklist items with open questions.
- Putting the plan under `docs/` instead of `tmp/superpowers/`.
- Switching the whole repository to Italian instead of keeping the exception local to plan files.
