# Plan Handoff

Use this reference when `internal-gateway-execute-plans` receives an approved
retained plan.

## Required Inputs

- Retained plan folder under `tmp/superpowers/`.
- Approval to execute the retained plan.
- `01-change-summary.md` when present.
- `02-execution.md` for compact plans or `02-control.md` for extended plans.
- Target, anti-scope, validation path, and stop conditions recoverable from the
  retained plan.

## Before Delegating To Superpowers

1. Confirm the plan folder path and basename.
2. Read only the smallest context needed to recover target, anti-scope,
   validation path, and stop conditions.
3. Treat `questions.md` as non-executable.
4. If the plan cannot be classified or lacks an executable path, stop with a
   `BLOCKED` status file instead of guessing.
5. Invoke `superpowers-executing-plans` for task-by-task execution once the
   handoff is safe.

## Stop Conditions

- The plan is not approved for execution.
- The retained plan path is missing or unreadable.
- Target, anti-scope, or validation path cannot be recovered.
- The requested action would modify `superpowers-executing-plans`.
- A required approval, credential, dependency, or owner decision is missing.
