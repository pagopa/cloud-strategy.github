# Execution Contract

Detailed operational rules for every execution phase. The main skill file owns the nine-phase sequence and completion conditions; this file owns the operational depth.

## Plan Readiness

A plan is ready for execution when it contains at minimum:

- **Goal** — one sentence describing the target outcome.
- **Repository Preflight** — target, anti-scope, nearest owner, validation path, stop conditions, and observable acceptance criteria.
- **Global Constraints** — invariants that apply to every task.
- **Ordered Tasks** — each with explicit files, interfaces, and step-by-step instructions.

Each task must name:

- The files it creates or modifies.
- The interfaces it consumes and produces.
- Concrete steps with focused validation commands.
- A checkable completion condition.

## Workspace Baseline

Before the first task, record:

- Current branch name.
- Dirty files relevant to the plan scope.
- Overlap between plan targets and uncommitted user changes.
- Affected callers, implementations, tests, and contracts for any interface change.

Preserve this baseline in the status file under `## Workspace Baseline`. Resume must detect drift between the recorded baseline and the current working tree.

## Plan Review Defect Classes

Raise these before starting execution:

- **Ambiguous target** — the goal or acceptance criteria are unclear.
- **Missing validation path** — no focused command to verify a task.
- **Destructive step** — a step that deletes, overwrites, or mutates external state without explicit user approval.
- **Owner conflict** — a task modifies a file owned by a narrower contract.
- **Scope creep** — a task introduces work outside the plan's stated target.
- **Unapproved external dependency** — a task requires a library, tool, or service not already in the stack.

## Task Dependency Set

Before editing, name every artifact the task touches:

- Source files created or modified.
- Callers of changed functions or interfaces.
- Implementations of changed contracts.
- Tests that assert the changed behavior.
- Documentation that references the changed interface.

After editing, perform a consistency pass across the dependency set. Confirm that no caller, implementation, test, or contract asserts the old behavior.

## Red-Green-Refactor Evidence

For tasks that change executable or evaluable behavior:

1. **Red** — write a failing test that asserts the new behavior. Confirm it fails for the right reason.
2. **Green** — make the smallest implementation edit that makes the test pass. Confirm all tests in the focused set pass.
3. **Refactor** — improve the implementation without changing behavior. Confirm all tests still pass.

Pre-code seam exceptions are allowed only when:

- The task is prose-only documentation.
- The task is mechanical formatting.
- The task is a behavior-neutral rename.
- The task is read-only validation.
- The plan explicitly names the exception and an alternate validation path.

Tests created after implementation count only as regression coverage, not as test-first work.

## Plan Drift

When the plan forces confusing code, duplicated logic, missing validation, owner conflict, or scope drift:

1. Stop execution of the current task.
2. Record the defect in the status file under `## Reason`.
3. Write a `PARTIAL` or `BLOCKED` status sibling with the exact evidence needed to resume.
4. Do not continue with workaround code.

## Approved Destructive Actions

If the plan contains destructive steps (delete, overwrite, mutate external state):

1. Confirm explicit user approval in the current conversation.
2. Record the approval in the status file under `## Reason`.
3. Execute the destructive step.
4. Verify the outcome with a focused validation command.

If approval is not explicit, stop and record the blocker.

## Retry and Fail-Fast

When a focused validation fails:

1. Diagnose the failure from the validator output.
2. Make the smallest fix that addresses the root cause.
3. Rerun the focused validation.
4. If the failure repeats three times without improvement, stop and record the blocker.

Do not retry by widening the change set. Do not retry by skipping the validation.

## Task Validator vs. Broader Plan Validation

- **Task validator** — a focused command that verifies the current task's observable outcome. Run this before marking the task complete.
- **Broader plan validation** — a comprehensive check that verifies the entire plan's acceptance criteria. Run this before claiming `DONE`.

A task cannot become complete without fresh task-validator evidence. A plan cannot become `DONE` without fresh broader-validation evidence. A final broad check does not retroactively validate skipped task gates.
