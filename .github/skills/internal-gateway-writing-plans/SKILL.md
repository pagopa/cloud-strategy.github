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
| `extended` | Cross-family changes, higher risk, lower-context execution, multiple validators, or multi-slice execution state. Soft-limit profile: use judgment-based size review with completeness over compression, explicit control files, and deterministic read order. | `01-change-summary.md`, `02-control.md`, `03-execution.md`, additional numbered files by category (`04-...`). |

### Plan Profile Selection Guard

Escalate to `extended` when completeness or context-discipline risk is material:
cross-skill token-discipline changes; exports, generated reports, or datasets
with non-trivial reconciliation; validator-impacting contract changes;
external API contracts (credentials, pagination, retries, schema pinning);
executive-facing output; multiple validators; or synced always-on guidance
edits.

Do not use `compact` when the executor needs exact sources, target files,
validators, blockers, or external pins that only `02-control.md`
can provide.

If `compact` is still chosen near one of those edges, the plan must record the
contrary evidence that keeps one owner, one execution lane, and one validation
path sufficient despite lower-context execution.

## Explicit Constraints

- Create retained plans under `tmp/superpowers/<clear-action-or-task-name>/`.
- New `compact` folders must use `tmp/superpowers/mini-plan-*`.
- Use English file names. Write `01-change-summary.md` in Italian. Write all
  other plan files in English.
- Keep `01-change-summary.md` as a compressed, non-executable decision capsule.
  Target at most 300 estimated tokens. Use only these required sections:
  `Problema da risolvere`, `Risultato atteso`, `Risorse coinvolte`,
  `Decisione richiesta`, and `Decisioni aperte`.
- `Risorse coinvolte` keeps the `Risorsa | Azione | Scopo` table. Use one row
  per materially changed resource group, not one row per file when that would
  duplicate `02-execution.md` or `02-control.md`.
- Do not put chosen logic, validation detail, execution route notes, source-item
  coverage, blockers, or implementation-contract detail in `01-change-summary.md`.
  Put those facts in `02-execution.md` for `compact` or `02-control.md` for
  `extended`.
- `01-change-summary.md` must still preserve `counter-validation-critical facts`:
  observable result criteria without which the user cannot verify whether the
  plan really covers the request. These are result facts, not execution detail.
  Keep them in `Risultato atteso` or `Risorse coinvolte`.
- Do not compress away concrete contract facts that materially define the
  requested result, such as column order, new columns, required fields,
  must-never-be-empty conditions, blocking diagnostics, repaired data gaps,
  row-count or no-data-loss invariants, or user-visible output-contract
  changes.
- Compact plans have a 2,000 estimated-token total budget measured as
  `ceil(UTF-8 bytes / 4)` across plan Markdown files. Keep `02-execution.md`
  under 1,500 estimated tokens. Treat warnings as required review inputs.
- For `extended`, treat token warnings as review inputs for completeness and
  slicing. Prefer splitting into numbered files over compression.
- `compact` uses exactly `01-change-summary.md` and `02-execution.md` during
  authoring. `extended` uses `01-change-summary.md`, `02-control.md`,
  `03-execution.md`, and optional higher numbered files.

## Core Contract

- For debugging, drift, or data-mismatch work, produce a compact diagnosis
  capsule before retained-plan authoring starts: symptom, target artifact,
  compared sources or layers, cheapest falsifier, and stop rule. Keep it only
  in chat or request context; do not create another retained file for it.
- `01-change-summary.md`: compressed Italian decision capsule following
  `Explicit Constraints`.
- Distinguish execution detail from `counter-validation-critical facts`.
  Execution detail covers route, commands, source-item ids, file-by-file steps,
  fallback logic, and validator order; those stay out of `01-change-summary.md`.
  `Counter-validation-critical facts` are the user-observable end-state facts
  needed to verify coverage at a glance, and they stay in `Risultato atteso`
  or `Risorse coinvolte`.
- When the plan changes output, schema, or data behavior, do not collapse the
  result into generic phrases such as `rispetta il nuovo schema`, `aggiorna gli
  output`, or `corregge i dati` if the request depends on concrete facts like
  first columns, field order, newly added columns, never-empty fields,
  blocking diagnostics, repaired row ranges, or row-count invariants.
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
- For `extended`, recommend adding deep companion files only when justified by
  triggers, and keep them as recommendations (not ERROR-level required files):
  `data-contract.md` for reconciled datasets and schema mappings,
  `validation-runbook.md` for multi-validator troubleshooting or rollback paths,
  and API/schema pin notes when external dependencies or credentials drive risk.
- Apply a say-once rule: each control fact (target, owner, validator, blockers,
  pins, and source-item coverage) is written once in the owning file, and step
  files do not restate target/owner/validator.
- Keep profile token weight explicit: `compact` stays within the 2,000-token
  total budget with a compressed `01`; `extended` keeps control weight in
  `02-control.md` and execution weight in numbered step files.
- `done-*`, `evidence-envelope.md`, and `completion-report.md` are packaging
  artifacts only. Do not create them during authoring.

## Workflow

1. Decide: retained plan or chat.
2. For debugging, drift, or data-mismatch work, write the diagnosis capsule
   before `01-change-summary.md`.
3. For new plans, run bundle-local `init` first to create the scaffold.
4. Choose folder name and write the compressed `01-change-summary.md` in Italian,
   preserving the user-visible `counter-validation-critical facts` needed to
   verify coverage without reading the control file.
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
13. Treat token warnings as review inputs, not as proof of measured savings. For
  `extended`, prefer splitting into numbered files over compression, and never
  compress away source pins, schema contracts, validation rules, stop
  conditions, or failure-investigation steps.

## Validation

- Plan lives under `tmp/superpowers/<clear-action-or-task-name>/`.
- `01-change-summary.md` is Italian, compressed, and contains only the required
  decision-capsule sections.
- `01-change-summary.md` preserves the most important
  `counter-validation-critical facts` in `Risultato atteso` or
  `Risorse coinvolte` when the plan changes output, schema, or data behavior.
- `compact` uses `01-change-summary.md` + `02-execution.md` only.
- `compact` stays under the 2,000 estimated-token total budget, or the warning
  was resolved by compression or escalation.
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
- Compressing away user-visible contract facts from `01-change-summary.md` and
  leaving only generic schema or output wording that prevents
  counter-validation.
- Creating `done-*` markers during authoring.
