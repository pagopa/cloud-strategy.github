# Execution Contract

This reference maps repository-local hooks around the delegated
`/superpowers-executing-plans` loop. It does not duplicate that skill's plan
review, todo, task execution, or core stop procedure.

## Before the delegated loop

- Require the exact retained plan path under `tmp/superpowers/plans/`.
- Confirm explicit user approval is present in the current conversation.
- Compute and record the SHA-256 plan fingerprint with `scripts/plan_execution.py`.
- Record branch, dirty files, and in-scope overlap before editing.
- Name the local task dependency set and focused validation command.
- Preserve the no-Git-mutation rule throughout execution.

## Before each delegated task

- State the task's observable outcome, dependency set, and focused validation.
- For executable or evaluable behavior, load `/internal-tdd` and establish
  red-first evidence before the first implementation edit.
- Keep repository-owned routing, status, fixtures, and approval gates in scope;
  do not edit imported core skills.

## After each delegated task

- Run the plan-specified focused validation command.
- Confirm the dependency set no longer asserts the replaced behavior.
- Retain fresh evidence before transitioning to the next task.
- If the plan authorizes simplification, `/addyosmani-code-simplification`
  may be loaded at that task's explicit gate.

## Execution discipline

- **TF (tight feedback):** Within the current approved task, treat the smallest
  coherent dependency set as one execution unit. Keep coupled edits, such as a
  signature, its callers, and its implementation, together; keep unrelated plan
  tasks separate. Use the task's focused validation as its transition gate.
- **FFD (fail fast on drift):** Stop the delegated loop when execution reveals
  plan drift, an owner conflict, missing required validation, or unapproved
  scope expansion. Record the gap and the exact evidence needed to continue in
  the applicable status sibling.

## Pause and resume

- On pause, record the exact status sibling, remaining tasks, validation gap,
  and next action using `references/status-contract.md`.
- On resume, run `resume-check` and require the recorded fingerprint to match
  the retained plan before continuing.
- If the plan changed after approval, stop and record plan drift until the
  approval and fingerprint are refreshed.

## Closeout

- Run all broader validation required by the retained plan.
- Load `/superpowers-verification-before-completion` before claiming completion.
- Run `git diff --check` and verify no Git mutation was performed.
- Replace older status siblings for the same plan basename and write exactly
  one allowed status sibling.
- Run `completion-check` only when every task and broader check has fresh
  passing evidence.
