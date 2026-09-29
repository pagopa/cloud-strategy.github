---
name: internal-gateway-execute-plans
description: Use when an explicitly approved retained plan must be implemented at its named task target.
---

# Internal Gateway Execute Plans

This is the repository wrapper around `/mattpocock-implement`. It is the sole
execution handoff after explicit approval of an exact retained plan path and
actual task target.

## When to use

- A writer result identifies the retained plan, task target, criteria,
  dependencies, verification, and human checkpoints, and the caller has
  approved that exact execution.
- A user asks to resume an approved task while preserving its recorded scope
  and approval evidence.

Route an unclear idea to `/internal-gateway-idea` and a missing or unapproved
plan to `/internal-gateway-writing-plans`. Do not execute a legacy plan that
contains `## Execution Manifest`; preserve it read-only and route an explicit
re-authoring request to the writer. This legacy clause applies to that manifest
only. Historical run files and runtime records remain read-only and are never
auto-resumed or migrated; residual work requires current source and new
approval. A normal resume of a current approved task remains allowed under this
contract, but never a custom old runtime.

## Approval and task contract

Before invoking the implementer, verify the writer result and current source
coherence. The plan path and actual task target are required. Consume the
approved task's acceptance criteria, dependencies, verification commands, and
human checkpoints as written. Unresolved references block start. A material
change to the source, target, criteria, dependencies, verification, or
checkpoint requires relevant reevaluation and explicit reapproval; do not
reconstruct a task from the spec alone.

The task's declared writable paths are the execution perimeter. An estimate
such as `Files likely touched` is not write authority. Preserve user changes,
stop on conflicts or out-of-scope writes, and never stash, overwrite, commit,
create a branch, or create a worktree. No ready state or prior plan approval
authorizes a different target or a later task.

## Implementer handoff

Invoke `/mattpocock-implement` for the exact approved task. Its general
implementation guidance is subordinate to this gateway's approval, scope,
user-work preservation, and no-commit boundaries. The implementer must not be
replaced by a parallel executor or used to widen the task.

After each approved checkpoint, report the exact plan and task target, changed
paths, verification outcomes, human decisions still required, and residuals.
Do not claim a plan is complete when a required check, checkpoint, dependency,
or approval is unresolved. Execution never starts automatically from
`plan_authoring_ready` or from a writer result alone. This wrapper creates no
parallel runtime ledger, object store, status projection, or duplicate review.
