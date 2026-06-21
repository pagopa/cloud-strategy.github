---
name: internal-gateway-execute-plans
description: Use when executing an approved compact or extended repository-owned plan from tmp/superpowers/<clear-action-or-task-name>/ and the numbered-file order, done-* loop, and blocker handling must stay explicit.
---

# Internal Gateway Execute Plans

## Referenced skills

- `internal-gateway-writing-plans`: retained-plan authoring owner for plans that feed this execution loop.
- `superpowers-executing-plans`: imported step-by-step execution engine when local policy is settled.
- `superpowers-subagent-driven-development`: imported worker-isolation engine when same-session subagents are available.
- `superpowers-verification-before-completion`: evidence gate before item completion and final retained-plan completion claims.

Repository-owned wrapper for applying retained numbered plans. This owner
consumes approved `compact` and `extended` retained plans.

## When to use

- Executing approved `compact` retained plans from `tmp/superpowers/mini-plan-*`.
- Executing approved `extended` retained plans from `tmp/superpowers/<action>/`.
- Applying a `compact` or `extended` plan authored with `internal-gateway-writing-plans`.

## When not to use

- Reviewing or challenging a plan; use `internal-gateway-review` or `internal-gateway-critical-master`.
- Treating `questions.md` as an executable file.

## Core Algorithm

1. Read `01-change-summary.md` first.
2. For `compact`, read `02-execution.md`; for `extended`, read `02-control.md`.
3. Verify `Plan profile: compact` or `Plan profile: extended`, then infer the execution strategy from profile, folder shape, and validation path.
4. Establish execution state from summary, control file, and active validator outcomes; keep it compact and update it as items close.
5. Avoid repeated full rereads: inspect changed sections, active executable item context, and failing-validator evidence first.
6. Run the ledger evidence pass.
7. Identify mandatory applicable requirements from selected skills using target, runtime, ownership, and validation path.
8. For `compact`, confirm the folder uses `mini-plan-*` and `02-execution.md` is the only executable file.
9. For `extended`, read numbered executable files after `02-control.md` in order starting at `03-execution.md`.
10. Process numbered executable files in order with the Agentic Execution Loop.
11. Run an item-level compliance audit before closing each executable item.
12. Track progress through the live ledger.
13. Aggregate unresolved mandatory applicable requirements before closeout.
14. Determine the completion state using the Closing Procedure state tree.
15. Package closeout only for `DONE`; for all other states, write a `<STATE>-plan-state.md` marker and keep the live ledger.

## Execution Contract

- Reject unsupported profiles immediately.
- Reject `compact` folders outside the `mini-plan-*` convention.
- Ignore `questions.md` during execution.
- Maintain a compact execution state and prefer targeted rereads over full file re-ingestion unless new evidence invalidates current state.
- Use `Compact Evidence Reporting` for large validator output: read enough output to decide the state honestly, then retain command, exit code, material counts, header or schema checks, changed files, and exact gaps instead of pasting raw logs.
- Infer the execution strategy from `Plan profile`, folder shape, merged control-contract sections in `02-control.md` when applicable, and the validation path. Do not require a separate retained-plan consumer field.
- Audit only mandatory requirements that are applicable; do not convert specialist rules into universal policy.
- Use `superpowers-verification-before-completion` as the fresh-evidence owner; do not duplicate its mechanics.
- Block item closure and block `SHIPPED` whenever mandatory applicable requirements remain unverified.
- Escalate architecture ownership conflicts, cross-owner skill conflicts, and undefined validation strategy.
- Pressure-test boundary: a Lambda-owned hashed requirements file does not grant a separate stdlib-only CLI launcher permission to install that dependency set.
- Only `DONE` may create `done-*` markers or remove numbered plan files, or publish a lightweight `DONE-plan-state.md` marker (`<STATE>-plan-state.md` convention) with `State: DONE` and `Continuation: none`.
- Non-`DONE` exits keep the live ledger and numbered files in place.

## Agentic Execution Loop

When execution is already authorized, stay inside the active owner, target
scope, anti-scope, and validation path, then iterate:

1. Confirm the current goal and nearest evidence.
2. Apply the smallest in-scope action.
3. Run the focused validation or evidence check.
4. If validation fails for an in-scope, repairable reason, fix once and re-run.
5. Continue only while evidence improves and no stop condition fires.
6. Stop with `DONE`, a blocker, or an explicit evidence gap.

Apply `Compact Evidence Reporting` after each focused validation: preserve the
exact gap and proof path, but keep large outputs summarized unless the raw
output is itself the missing evidence.

Stop on scope drift, destructive action, owner conflict, missing validation
path, human approval need, secret exposure risk, or repeated non-improving
failures.

## Closing Procedure

A retained plan folder must end every execution session in exactly one explicit
state. The agent determines the state from evidence, not from intent. Use the
state tree below, then apply the matching per-state actions.

### State Determination

Evaluate the following checks in order and stop at the first match:

1. **Cancelled?** The user explicitly decided to abandon the plan, and the
   decision is recorded as `INTENTIONAL_NON_ACTION` with a documented reason in
   the ledger. State: `CANCELLED`.
2. **Blocked?** A real, evidenced blocker prevents safe continuation. State:
   `BLOCKED`.
3. **Rolled back?** Applied work was reverted or superseded by a different safe
   state, and the original ledger rows are closed with evidence. State:
   `ROLLED_BACK`.
4. **Done?** All in-scope ledger rows are closed, validators pass, mandatory
   applicable evidence is verified, and no open blocker remains. State: `DONE`.
5. **Applied but unverified?** Edits were applied, but a required validator,
   review, or evidence coverage is missing. State: `APPLIED_UNVERIFIED`.
6. **Partial?** Some in-scope items remain incomplete or intentionally deferred.
   State: `PARTIAL`.

If the ledger is absent, stale, or cannot be reconstructed, the state cannot be
`DONE`; use `APPLIED_UNVERIFIED` or `PARTIAL` and report the exact gap.

### Per-State Actions

| State | Numbered files | Live ledger | `done-*` markers | `<STATE>-plan-state.md` | `completion-report.md` |
| --- | --- | --- | --- | --- | --- |
| `DONE` | May be removed after evidence is stable | Finalized and retained | Required for full packaging | Optional lightweight marker (`DONE-plan-state.md`) | Required for full packaging, optional for lightweight |
| `APPLIED_UNVERIFIED` | Keep in place | Keep in place | Do not create | Required | Optional but recommended |
| `PARTIAL` | Keep in place | Keep in place | Do not create | Required | Optional but recommended |
| `BLOCKED` | Keep in place | Keep in place | Do not create | Required | Optional but recommended |
| `ROLLED_BACK` | Keep in place | Keep in place | Do not create | Required | Optional but recommended |
| `CANCELLED` | Keep in place | Keep in place | Do not create | Required | Optional but recommended |

`done-*` markers and numbered-file removal are exclusive to `DONE`. Every other
state is a live-folder state and must preserve the retained plan for resume or
manual continuation.

### Lightweight Marker Contract

A lightweight marker is a file named `<STATE>-plan-state.md` in the plan folder.
It is a terminal marker only when `State: DONE` and `Continuation: none`. For
non-`DONE` states it documents the current live-folder state.

Required fields:

- `State:` exactly the state encoded in the filename.
- `Continuation:` `none` for `DONE`; `continuing` or `waiting` for all other states.
- `User action required:` mandatory when `Continuation` is `waiting`.
- `Next-step package:` `Owner`, `Scope`, `Action`, `Validation`, and `Risk`
  mandatory for non-`DONE` states.
- `Evidence gaps:` the exact gap preventing `DONE`.

Only one `<STATE>-plan-state.md` marker may exist in a plan folder at a time.
When the state changes, replace the marker; do not accumulate multiple state
markers.

### State Transitions

Allowed transitions:

- Any live-folder state (`APPLIED_UNVERIFIED`, `PARTIAL`, `BLOCKED`,
  `ROLLED_BACK`, `CANCELLED`) to `DONE` when evidence gaps close.
- `APPLIED_UNVERIFIED` to `PARTIAL` or `BLOCKED` when new evidence shows the
  work is incomplete or blocked.
- `PARTIAL` to `APPLIED_UNVERIFIED` when all planned edits are applied but
  verification is still missing.
- `BLOCKED` to `PARTIAL` or `APPLIED_UNVERIFIED` when the blocker is resolved.
- `ROLLED_BACK` to any state if new work restarts or supersedes the rolled-back
  state.
- `CANCELLED` is terminal. A new plan must be authored to restart cancelled work.

A transition must be evidenced by a fresh ledger pass and, when validators exist,
by fresh validator output. Do not move a folder to `DONE` from a non-`DONE` state
without re-running the applicable validation.

### Closeout Artifact Checklist

Before declaring any closeout step complete:

1. Compare promised work with observed delivery using the source-item ledger,
   current diff, touched files, validators, and explicit non-actions.
2. Record the completion state in `completion-report.md` for full packaging, or
   in `<STATE>-plan-state.md` for lightweight live-folder or `DONE` markers.
3. For `DONE`, ensure the evidence envelope maps every ledger row or `done-*`
   item to a status, evidence path or command, and route.
4. For non-`DONE` states, ensure the marker records the exact evidence gap,
   continuation intent, and next-step package.
5. Run the bundle-local `state-check` and `completion-check` commands and
   resolve any ERROR or WARNING they report.

## Validation

- Summary and profile-control files are read first.
- `Plan profile` is `compact` or `extended`.
- Execution strategy is inferred from profile, folder shape, and validation path.
- `compact` retained plans use `tmp/superpowers/mini-plan-*` and `02-execution.md` as the only executable file.
- `extended` retained plans include `02-control.md` before executable work.
- Mandatory applicable requirements are checked at item close and before `DONE`.
- The Agentic Execution Loop stayed inside the authorized owner, scope, and
  validation path.
- Missing mandatory applicable evidence maps to a non-`DONE` state.
- `done-*` markers appear only during full close packaging; lightweight closeout uses `<STATE>-plan-state.md` (for closed plans: `DONE-plan-state.md`) and may retain numbered files.
- Non-`DONE` states keep numbered plan files and the live ledger in place.
- `<STATE>-plan-state.md` filename matches the declared `State:` and encodes a single marker.
- `Continuation` matches the state: `none` for `DONE`, `continuing` or `waiting` for all other states.
- Non-`DONE` markers include a `User action required`, `Next-step package`, and `Evidence gaps` field when applicable.

## Common failure modes

- Closing an item because edits exist while mandatory applicable evidence is still open.
- Treating every loaded specialist rule as mandatory without applicability proof.
- Hiding ownership conflicts instead of escalating a next owner and validation path.
- Continuing the Agentic Execution Loop after evidence stops improving or a
  stop condition fires.
- Pasting raw large validator output when compact evidence would preserve the same proof.
- Packaging `DONE` while evidence gaps still require `APPLIED_UNVERIFIED`, `PARTIAL`, or `BLOCKED`.
- Declaring a non-`DONE` state without writing or updating the `<STATE>-plan-state.md` marker.
- Leaving stale `<STATE>-plan-state.md` markers behind after a state transition.
- Creating `done-*` markers or removing numbered plan files for `APPLIED_UNVERIFIED`, `PARTIAL`, `BLOCKED`, `ROLLED_BACK`, or `CANCELLED`.
- Moving a folder to `DONE` from a non-`DONE` state without fresh validator evidence.
- Treating `CANCELLED` as `DONE` or as a substitute for missing evidence.
