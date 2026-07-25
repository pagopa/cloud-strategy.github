---
name: internal-gateway-execute-plans
description: "Use when executing or resuming an approved repository-owned retained plan under tmp/superpowers/plans/."
disable-model-invocation: true
---

# Internal Gateway Execute Plans

## Bundle References

- `references/execution-contract.md` — detailed operational rules for every execution phase.
- `references/status-contract.md` — status transition table, required headings, and exact sibling filenames.
- `scripts/plan_execution.py` — read-only stdlib-only CLI for plan binding, status shape, resume safety, and completion readiness.

## When to use

- Execute or resume an approved retained plan under `tmp/superpowers/plans/`.
- Apply repo-local closeout through one exact allowed status sibling file.

## When not to use

- Writing, reformulating, reviewing, or challenging a plan.
- Running same-chat work that is not driven by an approved retained plan.
- Changing imported execution behavior; this bundle is self-contained.

## Execution Workflow

The workflow proceeds through nine phases in order. Each phase has one checkable completion condition.

### 1. Bind plan

Require an exact plan path under `tmp/superpowers/plans/`. Require explicit user approval kept as conversation state. Compute a SHA-256 fingerprint of the approved plan using the helper script.

**Completion:** fingerprint recorded, approval state explicit.

### 2. Workspace preflight

Record branch, dirty files, and in-scope overlap. Identify affected callers, implementations, tests, and contracts for interface changes.

**Completion:** baseline recorded, dependency set named.

### 3. Plan review

Read the plan critically. Identify questions or concerns. Raise blockers before starting. Do not proceed with ambiguous or destructive steps.

**Completion:** no unresolved blockers, or stop recorded.

### 4. Task preflight

Before each task, name its observable outcome, dependency set, and focused validation command.

**Completion:** outcome, dependency set, and validation command announced.

### 5. Test-first gate

For tasks that change executable or evaluable behavior, require red-first evidence or a pre-code seam exception recorded before the first implementation edit.

**Completion:** failing test exists, or exception recorded with alternate validation path.

### 6. Execution unit

Execute the smallest coherent change set. Complete all known coupled edits (signature, callers, body) as one unit. Perform a consistency pass across the dependency set.

**Completion:** all coupled edits done, consistency pass done.

### 7. Task transition

Run the focused validation command. Require fresh passing evidence before marking the task complete. If the check is missing, not run, or failing, keep the task in progress or blocked.

**Completion:** task-level evidence passes, or task stays in progress.

### 8. Plan closeout

Before final response or pause, run broader validation if required. Require fresh passing evidence before claiming `DONE`. Replace any older sibling status file for the same plan basename, then write exactly one allowed status sibling file.

**Completion:** broader evidence passes, one exact status sibling written.

### 9. Stop

Stop on scope drift, destructive action, owner conflict, missing validation path, human approval need, secret exposure risk, or repeated non-improving failures. Record the defect and write the appropriate status sibling.

**Completion:** stop condition recorded, status sibling written.

## Execution Discipline

- Plan-bound: follow the approved retained plan and stop when it is no longer executable as written.
- Evidence-gated: require fresh focused evidence before every task transition and broader evidence before `DONE`.
- Fail-fast on drift: stop and record the defect when the plan forces confusing code, duplicated logic, missing validation, owner conflict, or scope drift.

## No-Commit Rule

The skill must never run `git add`, `git commit`, `git push`, `git merge`, or any other git mutation while executing, pausing, or closing out a plan. Executed changes stay uncommitted in the working tree; the user reviews and commits them personally.

This rule is mandatory. The user may bypass it only with an explicit request for commit help in the current task; state the bypass in the status file and the final response.

If an approved plan contains `git add`, `git commit`, or `git push` steps, skip them, record them as plan drift in the status file, and continue with the remaining steps.

## Status File

Before final response or pause, replace any older sibling status file for the same plan basename, then write exactly one allowed status sibling file named `<plan-basename>.<STATUS>.md` where STATUS is one of `DONE`, `PARTIAL`, `BLOCKED`, or `NEEDS_REVIEW`. See `references/status-contract.md` for required headings and transition rules.

## Validation

- `git diff --check`
- `python3 scripts/plan_execution.py preflight <plan-file> --format compact`
- `python3 scripts/plan_execution.py status-check <status-file> --format compact`
- `python3 scripts/plan_execution.py resume-check <plan-file> <status-file> --format compact`
- `python3 scripts/plan_execution.py completion-check <plan-file> <status-file> --format compact`
- Confirm no live repository references point to removed bundle files.
- Confirm no git mutation ran during execution or closeout.
