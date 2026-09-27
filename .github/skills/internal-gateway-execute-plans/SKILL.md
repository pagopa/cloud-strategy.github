---
name: internal-gateway-execute-plans
description: Use when executing, resuming, or querying an approved repository-owned retained plan under tmp/superpowers/plans/.
---

# Internal Gateway Execute Plans

Execute an approved retained plan through the native /superpowers-executing-plans workflow. This gateway owns checkout authority, checkpoints, the ledger, stop rules, and chat status. Load references/run-protocol.md and references/chat-templates.md at the start.

## When to use

- Execute or resume an approved plan under tmp/superpowers/plans/.
- Answer a read-only status query for that plan.

## When not to use

- No approved plan exists: route to /internal-gateway-writing-plans.
- A plan contains a legacy Execution Manifest: stop with PLAN_INVALID/legacy and route it to /internal-gateway-writing-plans for re-authoring.
- Work requests edits to imported superpowers skills.

## Approval and perimeter

- Approval is the exact command offered by the writer gate or a later explicit user request to execute. Do not ask again when valid approval is already present.
- Run Native only through /superpowers-executing-plans. A supplied Subagent-driven or Inline preference receives the ledger ruling native-only executor; never load the subagent execution skill or dispatch implementers.
- The plan and its sources are read-only during execution.
- The execution perimeter is the union of every task Files block. A ruling cannot widen it. Scratch files belong only in the run directory.
- The checkout must remain exclusive to this run. A change the run did not make is foreign state, not task output.

## Native adapter

| Gateway step | Native action |
| --- | --- |
| task-start | Read the active ### Task N, verify its Interfaces, append Task N: started. |
| task-done | Run the task validation; save its output to task-N-tests.log; append complete only after exit 0 and a checkpoint. |
| review-package | Run cmd:task-diff and save task-N.diff for self-review. |
| reviewer dispatch | None. Review the saved diff yourself using the code-review checklist. |
| model choice | None. |
| temporary worktree | None. Use the current checkout. |
| harness todos | Optional. progress.md is authoritative. |

Never run imported task-start, task-done, or review helper scripts. They depend on commit ranges. Record ledger events directly. Preserve user rulings, declined judgments, fix-pass red-to-green evidence, and exhaustive final changed, pre-existing, ruling, and deferred-minor lists.

## Run directory

Use the plan header Status path. The run directory is tmp/superpowers/plans/<plan name>/, next to <plan name>.md. It contains status.md, progress.md, cp.idx, head.idx, task-N.diff, final.diff, and task-N-tests.log. Git checkpoint objects are the only artifact outside the run directory. Never read, create, migrate, or resume legacy executor workspaces.

## Preflight

On first start, before any ledger publication or task edit, run these checks in order. A preflight stop is chat-only with checkpoint none.

1. Reject a legacy Execution Manifest with PLAN_INVALID/legacy.
2. Reject a prerequisite plan named only in prose with PLAN_INVALID/prose-dep.
3. Rerun each Depends on check. A failed or unrunnable prerequisite stops with DEPENDS_FAILED/<plan>; a check: none also withholds execution.
4. Read the current branch with cmd:current-branch and the default branch with cmd:default-branch. Detached HEAD or an unresolved default stops with NEEDS_CONSENT/default-branch. Require branch consent on the resolved default branch and on main or master.
5. Read only task Files paths with git status --porcelain -- <Files paths>. Stop with NEEDS_CONSENT/dirty unless the user supplied the exact execute with dirty files command offered by the writer gate. Record included paths and blobs in APPROVAL.
6. Run cmd:object-probe with unique input and confirm the new object with git cat-file -e. A tree built from reused objects does not prove object-store write access. A denied probe stops without changing permissions or sandbox policy.
7. Create the run directory and confirm it is writable.
8. Run cmd:checkpoint for CP0 and verify git cat-file -t <CP0> returns tree. Publish plan path, START, initial status, and CP0 together by writing a temporary ledger and renaming it to progress.md. Never replace an existing ledger.

The first-start approval record contains the current plan blob, branch, default branch, consent state, dirty path/blob pairs, and include choice. Obtain the plan blob with a read-only git hash-object command. Preserve the writer gate's branch and dirty-file choices exactly.

A first-start dirty task file is not permission to overwrite it. Include it only after the exact dirty-files command was offered and supplied. Changes outside Files do not become task input.

## Per-task execution

Follow the plan's single /internal-tdd posture and step order. A planned Expected: FAIL is not an unexpected failure and does not consume a repair.

For each task:

1. Append Task N: started and implement only its Files paths.
2. Run the task's validation commands and save their complete output in task-N-tests.log.
3. For an unexpected failure, diagnose it before changing code. Allow at most two repair attempts per task. Record each as Task N: repair k/2. Never change assertions, acceptance criteria, or the task perimeter; that requires PLAN_INVALID/plan-wrong and re-authoring.
4. After green validation, capture the checkpoint. Read changed paths with cmd:changed-paths and apply protocol:files-globs, checking protected paths first and both rename endpoints.
5. Compare HEAD with the latest checkpoint using cmd:head-tree. Adopt a moved HEAD only when the branch is unchanged, the scratch-excluded HEAD tree equals the latest checkpoint, and a fresh checkpoint also equals it; retain START and CP0 and append HEAD adopted. Otherwise stop with CHECKOUT_CHANGED/foreign-commit.
6. Append Task N: complete with its checkpoint and passing validation.

The no-commit contract is absolute. Do not create commits, branches, or worktrees. The marked protocol commands use an isolated index and object-only checkpoint trees; never alter the real index or use checkpoint creation as permission to modify HEAD.

## Resume

On resume, rerun every Depends on check and verify the APPROVAL record against the plan blob, branch, default branch, consent, and dirty paths. Resume does not authorize execution or dirty-file inclusion.

Check every CP object with git cat-file -t; each must be a tree. Create a fresh checkpoint and compare it to the latest ledger checkpoint:

- Equal trees: continue from the last complete task.
- Differences only inside the first incomplete task's Files paths and its last event is started: append Task N: resumed on partial state and continue without discarding edits.
- Any other difference: stop with CHECKOUT_CHANGED/foreign-edit or CHECKOUT_CHANGED/ledger-mismatch. Do not reset, reinitialize, or overwrite the ledger.
- If HEAD moved, apply the HEAD-adoption conditions in Per-task execution. If approval evidence changed, stop with CHECKOUT_CHANGED/approval-stale.

A ledger without CP0 or a missing or unreadable checkpoint stops with CHECKPOINT_MISSING/<CPn> and asks for reconciliation.

## Status query

A status query is read-only. With no run directory, return NOT STARTED and create no state. Otherwise derive status from progress.md using protocol:derivation; the ledger wins if status.md disagrees. Report the disagreement. Every query verifies all checkpoint objects. A missing object stops with CHECKPOINT_MISSING/<CPn>. An Updated timestamp older than seven days gets an advisory idle warning and does not block the query or resume.

## Records and stops

Append each event to progress.md before rewriting status.md through a temporary file and rename. status.md is a projection of the ledger, never an independent source of truth. A failed ledger write stops with STORAGE_DENIED/run-dir and is reported in chat only.

Use protocol:stop-codes for exactly one next action per stop cause. A command is valid only when the current message offered it. Resume never grants approval or reconciliation. Irreversible or sensitive operations stop with NEEDS_CONSENT/safety.

## Final review and completion

After all tasks pass, append Final review: started. Build final.diff from CP0 to the final checkpoint. If dirty Files paths were included, also review git diff <START> <final CP> -- <included files>; list them as Preexisting separately.

Self-review the saved plan, diffs, task logs, and test evidence with the code-review checklist for plan alignment, code quality, architecture, security, testing, and production readiness. Do not dispatch a reviewer. Make one fix pass, checkpoint it, and record Final: fixed. Append Final review: done only when no critical or important finding remains. Minor items may be deferred and listed.

When all planned tasks and the final review pass, append END: DONE. If the session ends with unfinished tasks, append END: PARTIAL. Derive the final status from the ledger and render it with the DONE or PAUSED template. Load /superpowers-verification-before-completion before any completion claim.

## Chat

Use references/chat-templates.md for STARTED, RUNNING, RESUMED, PAUSED, NEEDS CONFIRMATION, BLOCKED, NOT STARTED, PLAN TO REWRITE, and DONE. Localize labels; keep paths and commands in inline code. Every message is at most five lines and has one final bold action, except STARTED and RESUMED, which have none. Use the documented progress bar and never imply unrecorded state.

## Stop-code map

- PLAN_INVALID/legacy or PLAN_INVALID/prose-dep: re-author the plan through /internal-gateway-writing-plans.
- DEPENDS_FAILED/<plan>: execute the exact upstream plan path through /internal-gateway-execute-plans.
- NEEDS_CONSENT/default-branch: resolve the branch and supply the offered branch command.
- NEEDS_CONSENT/dirty: supply the offered dirty-files command or resolve the dirty path.
- NEEDS_CONSENT/safety: supply the exact safety confirmation offered.
- CHECKOUT_CHANGED/foreign-commit: confirm or undo the commit, then resume.
- CHECKOUT_CHANGED/foreign-edit: stop the other session, then resume.
- CHECKOUT_CHANGED/ledger-mismatch: reconcile the ledger.
- CHECKOUT_CHANGED/approval-stale: reconcile and approve again.
- OUT_OF_PERIMETER/file: rewrite the plan or undo the out-of-scope change.
- OUT_OF_PERIMETER/protected: explicitly authorize the exact protected path or choose another approach.
- TEST_FAILED/exhausted: read the saved log and decide whether the test or code is wrong.
- CHECKPOINT_MISSING/<CPn>: reconcile the ledger and checkpoint.
- STORAGE_DENIED/git-objects: restore authorized object-store write access, then resume.
- STORAGE_DENIED/run-dir: restore run-directory write access, then resume.

## Final chat

Use the DONE template in references/chat-templates.md with Changed, optional Preexisting, Checks, Rulings, Deferred minors, and one final bold Action. Keep lists exhaustive and omit empty categories.
