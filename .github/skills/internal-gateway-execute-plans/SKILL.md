---
name: internal-gateway-execute-plans
description: "Use when executing or resuming an approved repository-owned retained plan under tmp/superpowers/plans/."
---

# Internal Gateway Execute Plans

## Bundle References

- `references/execution-contract.md` — repository hooks around the delegated execution loop.
- `references/status-contract.md` — status transition table, required headings, and exact sibling filenames.
- `scripts/plan_execution.py` — read-only stdlib-only CLI for plan binding, status shape, resume safety, and completion readiness.

## Referenced skills

- `/superpowers-executing-plans` owns critical plan review, todo tracking, task execution, and its core stop behavior.
- `/internal-tdd` owns executable-behavior test-first guidance at the local task gate.
- `/superpowers-verification-before-completion` owns final evidence before completion claims.
- `/addyosmani-code-simplification` is conditional and may be loaded only when the approved task explicitly authorizes simplification.

## When to use

- Execute or resume an approved retained plan under `tmp/superpowers/plans/`.
- Apply repository-local preflight, task hooks, status handling, and closeout around the delegated core loop.

## When not to use

- Writing, reformulating, reviewing, or challenging a plan.
- Running same-chat work that is not driven by an approved retained plan.
- Changing imported execution behavior or replacing the delegated core workflow.

## Gateway boundary

The gateway is a repository-owned extension of `/superpowers-executing-plans`. The
delegated owner supplies the core review, todo, execution, and stop loop. Keep
only these local responsibilities here:

- bind the exact plan path and explicit approval state;
- compute the SHA-256 fingerprint, run dirty-worktree preflight, and capture
  the plan-required validation baseline;
- apply task-level `/internal-tdd` and evidence hooks;
- classify failures, attempt bounded recovery, and preserve the baseline/final delta;
- enforce the no-Git-mutation policy;
- replace the exact `DONE`, `PARTIAL`, `BLOCKED`, or `NEEDS_REVIEW` sibling;
- run resume and completion checks through `scripts/plan_execution.py`.

## Delegation checkpoints

Before loading `/superpowers-executing-plans`, bind the retained plan, record
approval, fingerprint the plan, capture the workspace baseline, and run the
plan's broad baseline validation. At each
task boundary, load `/internal-tdd` when the task changes executable or
evaluable behavior and require its red-first evidence before implementation.
After each delegated task, run the plan's focused validation, retain fresh
evidence, classify failures, and attempt bounded recovery while evidence
improves. Pre-existing or unrelated broad failures do not stop independent
tasks. Load `/superpowers-verification-before-completion` before any positive
completion claim; load `/addyosmani-code-simplification` only when explicitly
authorized by the plan.

On pause or resume, preserve the plan fingerprint and use the status and resume
checks from `scripts/plan_execution.py`. At closeout, run the required broader
validation with the same commands used at baseline, record the baseline/final
delta, verify `git diff --check`, and write exactly one status sibling according
to `references/status-contract.md`. Always provide a concise user-facing report
with the outcome, changed work, validation, blocker or gap, recovery attempts,
and exact next action.

## No-Commit Rule

Do not run `git add`, `git commit`, `git push`, `git merge`, or another Git
mutation while executing, pausing, or closing out a plan. Leave executed
changes uncommitted for the user to review. If a retained plan contains Git
mutation steps, skip them and record the plan drift in the status sibling.

## Validation

- `git diff --check`
- `python3 scripts/plan_execution.py preflight <plan-file> --format compact`
- `python3 scripts/plan_execution.py status-check <status-file> --format compact`
- `python3 scripts/plan_execution.py resume-check <plan-file> <status-file> --format compact`
- `python3 scripts/plan_execution.py completion-check <plan-file> <status-file> --format compact`
- Confirm no live repository references point to removed bundle files.
