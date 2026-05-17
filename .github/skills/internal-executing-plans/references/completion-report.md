# Completion Report

Use this reference to close retained plan execution with an explicit state. A
completion report is evidence packaging, not a free-form summary.

## Source Patterns

- Comparative source: `tmp/external-comparison/compound-engineering-plugin/plugins/compound-engineering/skills/ce-work/references/shipping-workflow.md`.
- Comparative source: `tmp/external-comparison/hotl-plugin/docs/contracts/execution-report-output.md`.
- Adopt completion semantics only. Do not import external runtime reporting.

## Completion States

| State | Criteria |
| --- | --- |
| `SHIPPED` | All in-scope items are implemented or intentionally closed, validators passed, and the completion report is filled. |
| `APPLIED_UNVERIFIED` | Edits were applied, but required validator, review, or evidence coverage is missing. |
| `PARTIAL` | Some in-scope items remain incomplete or intentionally deferred. |
| `BLOCKED` | A real blocker prevents correct continuation. |
| `ROLLED_BACK` | Applied work was reverted or superseded by a different safe state. |

`SHIPPED` requires passed validators and a completed report. If validators cannot
run, use `APPLIED_UNVERIFIED`, `PARTIAL`, or `BLOCKED` with the explicit gap.

## Required Fields

- Active phase and owner.
- Completion state.
- Files changed.
- Items completed.
- Intentional non-actions.
- Validators or tests run.
- Evidence gaps.
- Residual risks.
- Follow-up suggestions separated from required work.

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
Evidence gaps: <gaps or none>
Residual risks: <risks or none>
Follow-up suggestions: <separate optional ideas>
```
