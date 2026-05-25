# Completion Report

Use this reference to close retained plan execution with an explicit state. A
completion report is evidence packaging, not a free-form summary.

Treat `completion-report.md` and `evidence-envelope.md` as late-stage packaging artifacts. Update them when the current validator, diff, and item-level evidence set is stable enough to report, not after every intermediate patch.

## Source Patterns

- Comparative source: `tmp/external-comparison/compound-engineering-plugin/plugins/compound-engineering/skills/ce-work/references/shipping-workflow.md`.
- Comparative source: `tmp/external-comparison/hotl-plugin/docs/contracts/execution-report-output.md`.
- Adopt completion semantics only. Do not import external runtime reporting.

## Completion States

| State | Criteria |
| --- | --- |
| `SHIPPED` | All in-scope ledger items are implemented or intentionally closed, validators passed, required evidence envelope coverage exists, and the completion report is filled. |
| `APPLIED_UNVERIFIED` | Edits were applied, but required validator, review, or evidence coverage is missing. |
| `PARTIAL` | Some in-scope items remain incomplete or intentionally deferred. |
| `BLOCKED` | A real blocker prevents correct continuation. |
| `ROLLED_BACK` | Applied work was reverted or superseded by a different safe state. |

`SHIPPED` requires passed validators, a completed report, and no open
source-item ledger rows. Non-trivial retained plans also require an evidence
envelope or equivalent item-level evidence for every requested or source item.
If validators or evidence coverage cannot run, or any row remains `PENDING`,
`PARTIAL`, `NOT_DONE`, `UNVERIFIABLE`, or `BLOCKED`, use
`APPLIED_UNVERIFIED`, `PARTIAL`, or `BLOCKED` with the explicit gap.

## Required Fields

- Active phase and owner.
- Completion state.
- Files changed.
- Items completed.
- Intentional non-actions.
- Validators or tests run.
- Evidence envelope.
- Source-item ledger status.
- Evidence gaps.
- Residual risks.
- Lessons status, including `added`, `codified`, or `none`.
- Follow-up suggestions separated from required work.

## Evidence Envelope

For non-trivial retained plans, include or link an evidence envelope. The
envelope must map each `02-source-item-ledger.md` row, retained-plan item, or
reconstructed `done-*` item to a status, evidence path or command, and route.

Before assigning `SHIPPED`, compare promised work with observed delivery. Use
the source-item ledger, current diff, touched files, validators, and explicit
non-actions. A summary that says an item was done is not evidence.

Do not churn the evidence envelope after every local slice when the validator output is still moving. Refresh it when the retained-plan state is coherent enough to support the reported completion state.

Minimum fields:

- Source item or source `done-*` file.
- Ledger item id when available.
- Reconstructed item when the original numbered plan file was already removed.
- Intended observable acceptance, such as diff, file state, validator assertion,
  manual check, or explicit non-action.
- Status using `DONE`, `PARTIAL`, `NOT_DONE`, `CHANGED`, or `UNVERIFIABLE`.
- Evidence path, artifact, or command.
- Route for unresolved or intentionally deferred work.

If a `done-*` marker lacks enough item-level evidence and no independent file,
diff, or validator evidence exists, mark the item `UNVERIFIABLE` instead of
claiming `SHIPPED`.

If the ledger is absent or stale and cannot be reconstructed from source plan
files, `done-*` files, and reachable artifacts, mark the completion state
`PARTIAL` or `APPLIED_UNVERIFIED`; do not claim `SHIPPED`.

## Review Tiers

| Tier | Trigger | Minimum lenses |
| --- | --- | --- |
| `light` | Up to 2 files or text-only changes with low blast radius. | `internal-code-review` where code exists, plus concise contract check. |
| `standard` | Multi-file changes with workflow, tests, or adjacent contracts. | Always-on review lenses from `review-lenses.md`. |
| `deep` | Always-on guidance, wrapper agents, validators, or cross-family contracts. | Always-on, cross-cutting, stack-specific lenses, plus scope drift check. |

## Template

```text
Completion Report
Active phase and owner: <phase, owner>
State: SHIPPED | APPLIED_UNVERIFIED | PARTIAL | BLOCKED | ROLLED_BACK
Files changed: <paths>
Completed items: <items>
Intentional non-actions: <items or none>
Validators: <commands and outcomes>
Evidence envelope: <path or item-level evidence summary>
Source-item ledger: <all rows closed, gaps listed, or unavailable>
Evidence gaps: <gaps or none>
Residual risks: <risks or none>
Lessons: added | codified in <owner> | none - <short reason>
Follow-up suggestions: <separate optional ideas>
```
