# Completion Report

Use this reference to close retained plan execution with an explicit state. A
completion report is evidence packaging, not a free-form summary.

Treat `completion-report.md` and `evidence-envelope.md` as late-stage packaging artifacts. Update them when the current validator, diff, and item-level evidence set is stable enough to report, not after every intermediate patch.

## Source Patterns

- Comparative source: `tmp/external-comparison/compound-engineering-plugin/plugins/compound-engineering/skills/ce-work/references/shipping-workflow.md`.
- Comparative source: `tmp/external-comparison/hotl-plugin/docs/contracts/execution-report-output.md`.
- Adopt completion semantics only. Do not import external runtime reporting.

## Profile Gate

Before any completion-phase validation, verify the `Plan profile` is `compact`
or `extended`. Unsupported or missing profiles return `unsupported-plan-contract`
and the completion attempt stops.

`compact` execution remains owned by `internal-gateway-simple-task`. Shared
closeout validation uses this completion contract and does not imply compact
execution ownership transfer.

When packaged folders no longer include `02-source-item-ledger.md`, the
completion report should include `Plan profile: compact` or
`Plan profile: extended` so profile validation remains deterministic.

## Completion States

| State | Criteria | Folder behavior | Continuation |
| --- | --- | --- | --- |
| `SHIPPED` | All in-scope ledger items are implemented or intentionally closed, validators passed, required evidence envelope coverage exists, no numbered plan files remain, and the completion report is filled. | Create matching `done-*` markers and remove numbered plan files only after the evidence envelope and report are stable. | `none` |
| `APPLIED_UNVERIFIED` | Edits were applied, but required validator, review, or evidence coverage is missing. | Keep numbered plan files and the live ledger in place. Do not create new `done-*` markers. | `continuing` or `waiting` |
| `PARTIAL` | Some in-scope items remain incomplete or intentionally deferred. | Keep numbered plan files and the live ledger in place. Do not create new `done-*` markers. | `continuing` or `waiting` |
| `BLOCKED` | A real blocker prevents correct continuation. | Keep numbered plan files and the live ledger in place. Do not create new `done-*` markers. Record the blocker and next-step package. | `waiting` |
| `ROLLED_BACK` | Applied work was reverted or superseded by a different safe state. | Keep numbered plan files and the live ledger in place unless a later `SHIPPED` package supersedes the folder. Do not create new `done-*` markers for the rolled-back state. | `waiting` or `none` |
| `CANCELLED` | Explicitly evidenced as `INTENTIONAL_NON_ACTION` with documented reason. Not a substitute for missing evidence. | Keep numbered plan files and the live ledger in place. Do not create new `done-*` markers. Record the cancellation rationale in the completion report. | `none` |

`SHIPPED` requires passed validators, a completed report, no numbered plan files,
and no open source-item ledger rows. Non-trivial retained plans also require an
evidence envelope or equivalent item-level evidence for every requested or source item.
If validators or evidence coverage cannot run, or any row remains `PENDING`,
`PARTIAL`, `NOT_DONE`, `UNVERIFIABLE`, or `BLOCKED`, use
`APPLIED_UNVERIFIED`, `PARTIAL`, or `BLOCKED` with the explicit gap.
Only `SHIPPED` is a close-package state. Every other state is a live-folder
state and must preserve the retained plan for resume or manual continuation.

`CANCELLED` is accepted only when the plan was explicitly abandoned by user
decision and the cancellation is recorded as `INTENTIONAL_NON_ACTION` with a
documented reason in the ledger. Otherwise the ledger row remains open and
the state is `PARTIAL` or `BLOCKED`.

When the state is not `SHIPPED`, the report must also declare:

- `Continuation`: `continuing` or `waiting`.
- `User action required`: mandatory when `Continuation` is `waiting`.
- `Next-step package`: `Owner`, `Scope`, `Action`, `Validation`, and `Risk`.

## Required Fields

- Active phase and owner.
- Completion state.
- Plan profile.
- Continuation.
- User action required.
- Files changed.
- Items completed.
- Intentional non-actions.
- Validators or tests run.
- Evidence envelope.
- Source-item ledger status.
- Evidence gaps.
- Residual risks.
- Lessons status, including `added`, `codified`, or `none`.
- Next-step package.
- Follow-up suggestions separated from required work.

## Evidence Envelope

For non-trivial retained plans, include or link an evidence envelope. The
envelope must map each `02-source-item-ledger.md` row, retained-plan item, or
reconstructed `done-*` item to a status, evidence path or command, and route.

Before assigning `SHIPPED`, compare promised work with observed delivery. Use the source-item ledger, current diff, touched files, validators, and explicit non-actions. When `04-implementation-contract.md` is required, compare it with the touched files, validators, blocker handling, and any required external pin or fallback. Report any gap under `Evidence gaps` or `Residual risks`. A summary that says an item was done is not evidence.

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

If the completion state is `APPLIED_UNVERIFIED`, `PARTIAL`, `BLOCKED`,
`ROLLED_BACK`, or `CANCELLED`, do not use the report as permission to remove numbered plan files
or the live ledger. Those states document a live retained-plan folder, not a
physical close package.

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
State: SHIPPED | APPLIED_UNVERIFIED | PARTIAL | BLOCKED | ROLLED_BACK | CANCELLED
Continuation: none | continuing | waiting
User action required: <exact required user/external action, or none>
Files changed: <paths>
Completed items: <items>
Intentional non-actions: <items or none>
Validators: <commands and outcomes>
Evidence envelope: <path or item-level evidence summary>
Source-item ledger: <all rows closed, gaps listed, or unavailable>
Evidence gaps: <gaps or none>
Residual risks: <risks or none>
Lessons: added | codified in <owner> | none - <short reason>
Next-step package: Owner=<...>; Scope=<...>; Action=<...>; Validation=<...>; Risk=<...>
Follow-up suggestions: <separate optional ideas>
```
