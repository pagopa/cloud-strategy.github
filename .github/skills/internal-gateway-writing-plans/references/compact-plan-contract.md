# Compact Plan Contract

Schema, templates, and escalation rules for the `compact` retained-plan profile.
Load this reference only when writing or validating a `compact` plan.

New `compact` plans should use `tmp/superpowers/mini-plan-*`.

`01-change-summary.md` is written in Italian per the retained-plan authoring
contract. All other plan content uses English.

## Profile Declaration

Declare the profile in `02-execution.md`:

```text
Plan profile: compact
```

Missing profiles are rejected. Do not infer `compact` or `extended` from folder
content. Folders without a declared `Plan profile` return
`unsupported-plan-contract`.

## Compact File Shape

| File | Role | Mandatory |
| --- | --- | --- |
| `01-change-summary.md` | Italian human-readable decision summary. Non-executable. | Yes |
| `02-execution.md` | Merged control and execution file. Must contain profile and control header, executable numbered steps, and inline source-item coverage. | Yes |
| `done-*`, `evidence-envelope.md`, `completion-report.md` | Final packaging artifacts created after execution, not during authoring. | No (authoring) |

## Compact Read Order

Mandatory first reads:

1. `01-change-summary.md`
2. `02-execution.md`

Excluded reads:

- `done-*`, `evidence-envelope.md`, and `completion-report.md` during authoring.

`compact` is ready for retained-plan execution only after `handoff-check` is ready.
`internal-gateway-execute-plans` infers the concrete execution strategy from the
profile, folder shape, and validation path.

## Escalation To Extended

Escalate from `compact` to `extended` when any of these is true:

- The plan spans multiple owners or skill families.
- The executor is low-context and needs exact sources, target files, validators,
  blockers, or external pins that only `02-control.md` can provide.
- The validation path includes cross-family checks, external pins, or fallback rules.
- Hidden assumptions about file shape, naming, or repository conventions would
  force the executor to rediscover them.

When escalating, add `02-control.md` and additional numbered files
starting at `03-execution.md`. Update `Plan profile` to `extended`.

## Lifecycle States

- `scaffold`: created by `init`; not ready for execution.
- `ready`: `handoff-check` ready.
- `closed`: execution and packaging handled by the approved consumer.

## Compact Token Expectations

- Keep total estimated tokens small enough for a small/fast executor handoff.
- Keep `02-execution.md` concise and concrete; long procedural detail is an
  escalation signal to `extended`.

## Template: 01-change-summary.md (Italian)

Required sections in Italian:

- `Problema da risolvere` — concrete problem statement.
- `Risultato atteso` — expected outcome, short bullet list.
- `Risorse coinvolte` — table with columns `Risorsa | Azione | Scopo`. Required
  for non-trivial plans. Each row names the resource, the action, and its purpose.
- `Comportamento scelto` — chosen behavior and boundary rules.
- `Validazione prevista` — validation path.
- `Esecuzione prevista` — route visibility, including profile, folder prefix,
  execution file, and any execution-strategy hints the executor should infer.
- `Decisione richiesta` — decision request.
- `Decisioni aperte` — one line (`none` when there are no blockers).

## Template: 02-execution.md

Required sections:

- `Plan profile` — `compact`.
- `Target and anti-scope` — smallest target and explicit exclusions.
- `Owner and validator` — primary owner, lane-change owner, and validation path.
- `Stop conditions` — blockers that must stop execution.
- `Objective` — concrete goal.
- `Chosen logic` — why this approach.
- `Key assumptions` — key assumptions.
- `Executable steps` — numbered steps with observable acceptance per step.
- `Validation` — validation commands or checks.
- `Source item coverage` — compact table with item id, acceptance, evidence, and status.

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
