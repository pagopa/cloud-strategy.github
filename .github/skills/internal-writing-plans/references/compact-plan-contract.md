# Compact Plan Contract

Schema, templates, and escalation rules for the `compact` retained-plan profile.
Load this reference only when writing or validating a `compact` plan.

Plan content defaults to English per the repository authoring policy. The
templates below describe the required structure and field names; actual plan
content uses English.

## Profile Declaration

Declare the profile in `02-source-item-ledger.md`:

```text
Plan profile: compact
```

## Compact File Shape

| File | Role | Mandatory |
| --- | --- | --- |
| `01-change-summary.md` | Concise change summary: problem, proposed changes, rationale, validation, decision request. ~10 bullets. | Yes |
| `02-source-item-ledger.md` | Control file with `Recommended use`, `Plan profile`, `File map and role`, clarification gate, evidence pass, budget, target, anti-scope, owner, validator, stop conditions, source-item ledger table. | Yes |
| `03-execution.md` | First and only executable file. Uses the executable numbered-file shape: `Objective`, `Chosen logic`, `Key assumptions`, `Executable steps`, `Validation`. | Yes |
| `questions.md` | User-only decisions. Write `- none` when nothing remains. | Yes |
| `done-*`, `evidence-envelope.md`, `completion-report.md` | Final packaging artifacts created after execution, not during authoring. | No (authoring) |

## Escalation To Extended

Escalate from `compact` to `extended` when any of these is true:

- The plan spans multiple owners or skill families.
- The executor is low-context and needs exact sources, target files, validators,
  blockers, or external pins that only `04-implementation-contract.md` can provide.
- The validation path includes cross-family checks, external pins, or fallback rules.
- Hidden assumptions about file shape, naming, or repository conventions would
  force the executor to rediscover them.

When escalating, add `04-implementation-contract.md` and additional numbered files
by category (`05-...`). Update `Plan profile` to `extended`.

## Template: 01-change-summary.md

Required sections (headings in English per the plan-content language default):

- `Problem to solve` — concrete problem statement.
- `Proposed changes` — proposed changes, 3–5 bullets.
- `Why this path` — rationale, 1–2 bullets.
- `Validation` — validation path.
- `Decision requested` — decision request.

## Template: 03-execution.md

Required sections:

- `Objective` — concrete goal.
- `Chosen logic` — why this approach.
- `Key assumptions` — key assumptions.
- `Executable steps` — numbered steps with observable acceptance per step.
- `Validation` — validation commands or checks.

## Template: questions.md

```text
# Questions

- none
```

## Ledger Row Template

| ID | Source item | Observable acceptance | Evidence class | Acceptance evidence | Status | Route |

- `ID`: stable item identifier (e.g., `RP-01`).
- `Source item`: what was requested or what must change.
- `Observable acceptance`: diff, file state, validator assertion, manual check, or
  explicit non-action.
- `Evidence class`: diff, file, validator, manual, gap.
- `Acceptance evidence`: concrete command, path, or condition.
- `Status`: `PENDING` initially.
- `Route`: which plan file or explicit non-action owns this item.

## Legacy Folder Classification

Folders without a declared `Plan profile` are classified as `legacy`. Legacy
folders follow backward-compatible reading rules defined in
`internal-executing-plans/references/legacy-plan-compatibility.md`. Do not require
`compact` or `extended` fields in legacy folders.
