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
- The plan contains a legacy `## Execution Manifest`: run no task and report
  `Next: re-author <path> through /internal-gateway-writing-plans`.
- Edits to imported `superpowers-*` skills are out of scope.

## Approval and perimeter

- Approval is the user's explicit answer to the plan handoff or a later
  explicit request to execute. Do not ask for it again.
- The perimeter is the union of the plan's `Files:` paths, plus scratch writes
  under `.superpowers/` and `tmp/`. A ruling never widens it.
- Assume exclusive use of the checkout during execution.

## Checkpoints

Without commits, a checkpoint records the working state, minus scratch paths,
as a Git tree. Run `git read-tree HEAD`,
`git add -A -- . ':(exclude).superpowers/**' ':(exclude)tmp/**'`, and
`git write-tree` in order, from the repository root, each with
`GIT_INDEX_FILE=<workspace>/cp.idx`. The exclusions apply even when ignore
rules do not cover these paths. This writes objects only: no commit, ref,
real-index, or working-tree change.

Ledger it as `CP<n>: <tree>`: `CP0` at first start, then one after every
completed task and fix round, in the same append as its completion line.
Checkpoints replace the imported commit ranges, `git log` recovery, and the
imported review-package script.

## Workflow

1. **Select the executor.** Use `/superpowers-executing-plans` for `Native`,
   its alias `Inline`, or no stated choice. Use
   `/superpowers-subagent-driven-development` for `Subagent-driven`.
2. **Set up.** The current checkout is the workspace: do not create a branch or
   worktree, and skip `/superpowers-using-git-worktrees`.
   - First start (no ledger for this plan): create the workspace
     `.superpowers/sdd/<plan file name without .md>/` if needed, then run the
     preflight before any ledger write or task edit. A plan without a
     `**Depends on:**` line has no dependency. Stop on the first failure:
     1. A `Files:` path already has uncommitted changes.
     2. A `**Depends on:**` check in the plan fails, cannot run, or is
        `none`.
     3. Git object storage rejects a new object: run `git hash-object -w
        --stdin` on unique input, then `git cat-file -e` on the result. A
        successful CP0 is not proof, because a clean tree reuses existing
        objects. Never change permissions or sandbox policy to pass.
     4. CP0 cannot be created, or `git cat-file -t <CP0>` is not `tree`.

     Then write the plan path, `START: <git rev-parse HEAD>`, the preflight
     `git status --short` output, and `CP0` to a temporary file in the
     workspace and rename it to the ledger path. Never replace an existing
     ledger.
   - Resume (the ledger names this plan): rerun every `**Depends on:**`
     check first; a recorded result is not current evidence. Reuse `START`
     and the checkpoints.
     Diff a fresh checkpoint against the latest one, ignoring scratch paths.
     Continue when they match, or when every difference is inside the first
     incomplete task's `Files:` paths; then resume that task and ledger
     `Task <N>: resumed on partial state`. Otherwise, or when a checkpoint is
     missing or unreadable, including a ledger without `CP0`, stop for
     reconciliation; never reset, reinitialize, or overwrite.
3. **Run the executor unchanged, with these overrides:**
   - Git: follow the no-commit contract carried by the imported skills. Never
     commit. Review a task with `git diff CP<n-1> CP<n>` and a fix round with
     `git diff <reviewed CP> <new CP>`, saved in the workspace; earlier changes
     are context only.
   - Test posture: the task's recorded `/internal-tdd` posture is the agreed
     TDD exception. `feature-first` and `validation-only` tasks do not need a
     red-first run.
   - Subagent briefs carry the no-commit contract, the perimeter, the task
     posture, and the stop rules below. Implementers report changed files,
     not commits.
4. **Stop** on any of the imported stop conditions, and also when:
   - `HEAD` differs from `START`;
   - a `**Depends on:**` check fails or cannot run;
   - a change outside the perimeter is required, or
     `git diff --name-only CP<n-1> CP<n>` shows one;
   - a protected imported skill path would change;
   - a task file was dirty in the recorded first-start status.
5. **Finish.** Run the final review over `git diff CP0 <final CP>`, so
   pre-existing changes stay out of the review and of `Changed`. Keep the
   ledger and workspace under `.superpowers/sdd/<plan>/`, because Git holds no
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

`Next:` names one action that removes the controlling blocker:

- reconcile `<ledger path>`;
- rerun with writable Git object storage;
- execute `<repository root>:<plan path>` through
  `/internal-gateway-execute-plans`, for an existing upstream plan;
- write a plan that delivers `<required output>` through
  `/internal-gateway-writing-plans`, when the producer is `unresolved` or its
  path does not exist;
- supply a read-only check for `<required output>`, when the check is `none`;
- for any other stop, the decision that clears its cause, such as
  `resolve <failing command or dirty path>, then rerun`.

Never name a plan by label alone.

Then add the imported "Rulings I made" and "Deferred minors" lists from the
ledger. Omit an empty list.
