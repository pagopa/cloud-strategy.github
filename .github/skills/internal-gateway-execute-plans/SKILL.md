---
name: internal-gateway-execute-plans
description: Use when executing or resuming an approved repository-owned retained plan under tmp/superpowers/plans/.
---

# Internal Gateway Execute Plans

Execute one approved retained plan through the imported superpowers executors
while keeping repository authority, Git policy, and stop rules. The imported
skills own the task loop, ledger, TDD cycle, rulings, and final review.

## When to use

- Execute or resume an approved plan under `tmp/superpowers/plans/`.

## When not to use

- No approved plan exists: route to `/internal-gateway-writing-plans`.
- The plan contains a legacy `## Execution Manifest`: return it to
  `/internal-gateway-writing-plans` for re-authoring before execution.
- Edits to imported `superpowers-*` skills are out of scope.

## Approval and perimeter

- Approval is the user's explicit answer to the plan handoff or a later
  explicit request to execute. Do not ask for it again.
- The perimeter is the union of the plan's `Files:` paths, plus scratch writes
  under `.superpowers/` and `tmp/`. A ruling never widens it.
- Assume exclusive use of the checkout during execution.

## Workflow

1. **Select the executor.** Use `/superpowers-executing-plans` by default. Use
   `/superpowers-subagent-driven-development` when the user chose
   Subagent-driven.
2. **Set up.** The current checkout is the workspace: do not create a branch or
   worktree, and skip `/superpowers-using-git-worktrees`. Record
   `START: <git rev-parse HEAD>` and the `git status --short` output in the
   ledger before Task 1. Stop when a `Files:` path already has uncommitted
   changes.
3. **Run the executor unchanged, with these overrides:**
   - Git: follow the no-commit contract carried by the imported skills. Never
     commit; review with `git diff START` plus the untracked files listed by
     `git status --short`.
   - Test posture: the task's recorded `/internal-tdd` posture is the agreed
     TDD exception. `feature-first` and `validation-only` tasks do not need a
     red-first run.
   - Subagent briefs carry the no-commit contract, the perimeter, the task
     posture, and the stop rules below.
4. **Stop** on any of the imported stop conditions, and also when:
   - `HEAD` differs from `START`;
   - a change outside the perimeter is required;
   - a protected imported skill path would change;
   - a task file had uncommitted changes at start.
5. **Finish.** Run the final review over `git diff START` plus untracked files.
   Keep the ledger under `.superpowers/sdd/<plan>/`, because Git holds no
   record of the work. Skip `/superpowers-finishing-a-development-branch`.
   Load `/superpowers-verification-before-completion` before any completion
   claim.

## Report

Use exactly four lines, in the user's language, with canonical labels:

```text
Plan: <path> — DONE | PARTIAL | BLOCKED
Changed: <files or no changes>
Checks: <commands and results, or the controlling cause of the stop>
Next: <one action or none>
```

Then add the imported "Rulings I made" and "Deferred minors" lists from the
ledger. Omit an empty list.
