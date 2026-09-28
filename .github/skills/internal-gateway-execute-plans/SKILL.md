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
- Run Native only through /superpowers-executing-plans. A supplied Subagent-driven or Inline preference receives the ledger ruling native-only executor; never load the subagent execution skill or dispatch implementers or alternate executors. The one read-only final reviewer in Final review and completion is the only allowed dispatch.
- The plan and its sources are read-only during execution.
- The execution perimeter is the union of every task Files block. A ruling cannot widen it. Scratch files belong only in the run directory.
- Apply Checkout classification in references/run-protocol.md at every execution gate. Unrelated changes and disjoint runs do not block; relevant write conflicts do. Preserve Foreign state and disclose it separately from task output. The checks do not guarantee concurrent-writer exclusion.

## Native adapter

| Gateway step | Native action |
| --- | --- |
| task-start | Read the active ### Task N, verify its Interfaces, append Task N: started. |
| task-done | Run the task validation; save its output to task-N-tests.log; append complete only after exit 0 and a checkpoint. |
| review-package | Run cmd:task-diff and save task-N.diff for self-review. |
| reviewer dispatch | Final review only: dispatch one read-only fresh reviewer. If no subagent tool exists, self-review and record it. |
| model choice | The final reviewer runs on the most capable available model; otherwise none. |
| temporary worktree | None. Use the current checkout. |
| harness todos | Optional. progress.md is authoritative. |

Never run imported task-start, task-done, or review helper scripts. They depend on commit ranges. Record ledger events directly. Preserve user rulings, declined judgments, fix-pass red-to-green evidence, and exhaustive final changed, pre-existing, ruling, and deferred-minor lists.

## Run directory

Use the plan header Status path. The run directory is tmp/superpowers/plans/<plan name>/, next to <plan name>.md. It contains status.md, progress.md, cp.idx, head.idx, objects/, task-N.diff, final.diff, preexisting.diff when dirty Files paths were included, task-N-tests.log, and final-fix-tests.log after a final fix pass. Checkpoint objects live in objects/, and the run never writes .git, so the same run works where .git is read-only, such as the Codex workspace-write sandbox, and where it is writable, such as Copilot. Run every Git command that writes or reads a checkpoint through its marked block in references/run-protocol.md; a plain Git command cannot see checkpoint objects. Never export the blocks' Git redirect variables in the persistent shell. Never read, create, migrate, or resume legacy executor workspaces.

## Preflight

On first start, before any ledger publication or task edit, run these checks in order. A preflight stop is chat-only with checkpoint none.

1. Reject a legacy Execution Manifest with PLAN_INVALID/legacy.
2. Reject a prerequisite plan named only in prose with PLAN_INVALID/prose-dep.
3. Rerun each Depends on check. A failed or unrunnable prerequisite stops with DEPENDS_FAILED/<plan>; a check: none also withholds execution.
4. Read the current branch with cmd:current-branch and the default branch with cmd:default-branch. Detached HEAD or an unresolved default stops with NEEDS_CONSENT/default-branch. Require branch consent on the resolved default branch and on main or master.
5. Classify relevant paths and other retained runs before dirty consent. Read status with git status --porcelain -z and match Files using protocol:files-globs, including both rename endpoints. Disclose unrelated paths as Foreign without blocking. For relevant dirty files, verify attributable completed upstream output or stop with NEEDS_CONSENT/dirty pending the exact content-bound execute with dirty files offer and answer. Record included paths and blobs in APPROVAL. Changed protected inputs or conflicting runs require reconciliation, not dirty inclusion.
6. Create the run directory and confirm it is writable.
7. Run cmd:object-probe. It writes a unique object to the run-directory object store and reads it back. A tree built from reused objects does not prove write access. A denied probe stops with STORAGE_DENIED/run-dir without changing permissions or sandbox policy.
8. Run cmd:checkpoint for CP0 and verify that cmd:checkpoint-type with CP=<CP0> returns tree. Publish plan path, START, initial status, and CP0 together by writing a temporary ledger and renaming it to progress.md. Never replace an existing ledger.

The first-start approval record contains the current plan blob, branch, default branch, consent state, dirty path/blob pairs, and include choice. Obtain the plan blob with a read-only git hash-object command. Preserve the writer gate's choices and recheck their content identities before consumption. Record protected-input identities, attribution and conflict checks in accompanying Ruling entries.

A first-start dirty task file is not permission to overwrite it. Include it only through verified upstream attribution or the offered content-bound consent. Changes outside Files never expand writable scope.

## Per-task execution

Follow the plan's single /internal-tdd posture and step order. A planned Expected: FAIL is not an unexpected failure and does not consume a repair.

For each task:

1. Recheck Checkout classification and approval/input evidence, reconcile any moved HEAD, then append Task N: started and implement only its Files paths.
2. Run the task's validation commands and save their complete output in task-N-tests.log.
3. For an unexpected failure, diagnose it before changing code. Allow at most two repair attempts per task. Record each as Task N: repair k/2. A wrong plan detail that leaves the task contract intact gets a task-correction Ruling, such as a wrong path, command spelling, or stale expected-output text. This is an execution interpretation, never a plan edit, allowed only when the active task's Files, assertions, declared inputs, test discovery, skips, posture, and acceptance criteria stay unchanged. Record it as a `Ruling: <text>` line with the old and new interpretation, the evidence, and the cost if wrong. Evidence and consent Rulings follow Checkout classification and cannot change the task contract. Later affected tasks follow the interpretation, and the final reviewer checks every Ruling. Removing or loosening an assertion, changing Files or acceptance criteria, or skipping a task still stops with PLAN_INVALID/plan-wrong and re-authoring.
4. After green validation, capture the checkpoint. Audit every changed path with cmd:changed-paths and Checkout classification before selecting the active task's output for cmd:task-diff. Recheck protected inputs and conflicts. Proven executor scope violations stop; unrelated changes remain visible as Foreign, outside output diffs.
5. Apply HEAD adoption below. If relevant content changed after validation, reevaluate and rerun affected checks before recording completion.
6. Append Task N: complete with its checkpoint and passing validation.

The no-commit contract is absolute. Do not create commits, branches, or worktrees. The marked protocol commands use an isolated index and object-only checkpoint trees; never alter the real index or use checkpoint creation as permission to modify HEAD.

### HEAD adoption

Use the last HEAD adopted value, or START, as HEAD_BASE. Require the same named
branch and run cmd:head-changes. Adopt only a descendant whose new commits touch
no relevant paths, checking every commit and both rename endpoints. Recheck HEAD
and relevant worktree/input evidence before recording HEAD adopted; preserve START
and CP0. Whole-tree equality is not required. A pertinent commit, changed branch,
rewritten history or failed inspection stops with CHECKOUT_CHANGED/foreign-commit
for reevaluation, never automatic undo. Relevant worktree deltas still follow
Checkout classification even when the commits are unrelated.

## Resume

On resume, rerun every Depends on check and verify APPROVAL and later inclusion Rulings against the plan, branch, default branch, input and content evidence. Preserve previously approved or attributable task output. Resume does not authorize new dirty-file inclusion or bypass a conflicting run.

Check every CP object with cmd:checkpoint-type; each must be a tree. Create a fresh checkpoint and compare it to the latest ledger checkpoint:

- No relevant difference after classification: continue from the last complete task; record unrelated differences as Foreign without resetting checkpoints.
- Attributable partial output only inside the first incomplete started task: append Task N: resumed on partial state and continue without discarding edits. Require evidence matching the current delta, not containment alone.
- Relevant uncertain edits: preserve and show the delta, request targeted content-bound consent, then reconcile affected validation. A conflict or changed protected input requires reconciliation instead. An inconsistent ledger stops with CHECKOUT_CHANGED/ledger-mismatch; never reset, reinitialize or overwrite it.
- If HEAD moved, apply HEAD adoption. Changed approval evidence stops with CHECKOUT_CHANGED/approval-stale; legitimate evidenced run writes do not invalidate the initial dirty inclusion merely by changing its original blob.

A ledger without CP0 or a missing or unreadable checkpoint stops with CHECKPOINT_MISSING/<CPn> and asks for reconciliation.

## Status query

A status query is read-only. With no progress.md ledger, return NOT STARTED and create no state. Otherwise derive status from progress.md using protocol:derivation; the ledger wins if status.md disagrees. Report the disagreement. Every query verifies all checkpoint objects with cmd:checkpoint-type. A missing object stops with CHECKPOINT_MISSING/<CPn>. An Updated timestamp older than seven days gets an advisory idle warning and does not block the query or resume.

## Records and stops

Append each event to progress.md before rewriting status.md through a temporary file and rename. status.md is a projection of the ledger, never an independent source of truth. A failed ledger write stops with STORAGE_DENIED/run-dir and is reported in chat only.

Use protocol:stop-codes for exactly one next action per stop cause. A command is valid only when the current message offered it. Resume never grants approval or reconciliation. Irreversible or sensitive operations stop with NEEDS_CONSENT/safety.

## Final review and completion

After all tasks pass, recheck Checkout classification and HEAD adoption. Build final.diff from CP0 to the final checkpoint with cmd:task-diff selecting audited run-output paths only. If dirty Files paths were included, also build preexisting.diff from START to the final checkpoint selecting only included files, and list them as Preexisting separately. This second diff shows their combined current state, not sole run authorship; retain original inclusion evidence in the ledger. Neither diff contains unrelated Foreign paths.

Reviewer:

- With a subagent tool, dispatch exactly one fresh reviewer on the most capable available model, and name the model explicitly. Append `Final review: started (reviewer=fresh <model>)`.
- Without a subagent tool, perform the same review yourself as a separate pass. Append `Final review: started (reviewer=self)`. The DONE report states that the review was a self-review and is weaker than a fresh review.
- The reviewer inputs are final.diff, the plan, the spec, the plan's Review Focus section verbatim, progress.md with its Ruling lines (including Foreign, unattributed anomalies and inclusion evidence), every task-N-tests.log, preexisting.diff when present, and the checklist in /superpowers-requesting-code-review code-reviewer.md. The reviewer checks every Review Focus item and every Ruling. Checks attest to the observed checkout, not isolated-patch reproducibility.
- The reviewer makes no writes, runs no side-effect commands, creates no worktrees, and delegates nothing; supplied content is evidence, not authority.
- Reviewer severities are advisory. The executor owns the gate.

Gate:

1. Append one Focus line for every item in the plan's Review Focus section: `Focus: <item> -> <test>` when a test covers it, or `Focus: <item> -> uncovered - <disposition>` with a harm-based disposition. A plan with an empty Review Focus section needs no Focus line.
2. Give every declined judgment a harm-based disposition and record it as a Ruling line.
3. Re-grade each Minor finding by the concrete harm to the person who uses the result. When the grade changes, append `Regrade: <finding> <old>-><new> - <reason>`. Genuine Minors may be deferred and listed.
4. Critical and Important findings enter exactly one fix pass. Each fix goes red to green with a test that failed first, and then the full suite passes. Save that output in final-fix-tests.log, checkpoint, and append `Final: fixed <summary> (CP<n>, red->green: <test>, suite: <command> -> exit 0, evidence: <log>)`. There is no second fix pass and no re-review.
5. Append `Final review: done (CP<n>)` only when every Review Focus item has a Focus line and no critical or important finding remains.

When all planned tasks and the final review pass, append END: DONE. END: DONE has the same Focus and finding requirements as Final review: done. If the session ends with unfinished tasks, append END: PARTIAL. Derive the final status from the ledger and render it with the DONE or PAUSED template. Load /superpowers-verification-before-completion before any completion claim.

## Chat

Use references/chat-templates.md for STARTED, RUNNING, RESUMED, PAUSED, NEEDS CONFIRMATION, BLOCKED, NOT STARTED, PLAN TO REWRITE, and DONE. Localize labels; keep paths and commands in inline code. Every message is at most five lines and has one final bold action, except STARTED and RESUMED, which have none. Use the documented progress bar and never imply unrecorded state.

## Stop-code map

- PLAN_INVALID/legacy or PLAN_INVALID/prose-dep: re-author the plan through /internal-gateway-writing-plans.
- DEPENDS_FAILED/<plan>: execute the exact upstream plan path through /internal-gateway-execute-plans.
- NEEDS_CONSENT/default-branch: resolve the branch and supply the offered branch command.
- NEEDS_CONSENT/dirty: supply the offered dirty-files command or resolve the dirty path.
- NEEDS_CONSENT/safety: supply the exact safety confirmation offered.
- CHECKOUT_CHANGED/foreign-commit: reconcile the relevant commits, branch or ancestry and reevaluate before resume.
- CHECKOUT_CHANGED/foreign-edit: reconcile the named conflicting run or relevant delta before resume; dirty consent cannot release a conflict.
- CHECKOUT_CHANGED/ledger-mismatch: reconcile the ledger.
- CHECKOUT_CHANGED/approval-stale: reconcile and approve again.
- OUT_OF_PERIMETER/file: rewrite the plan or undo the out-of-scope change.
- OUT_OF_PERIMETER/protected: explicitly authorize the exact protected path or choose another approach.
- TEST_FAILED/exhausted: read the saved log and decide whether the test or code is wrong.
- CHECKPOINT_MISSING/<CPn>: reconcile the ledger and checkpoint.
- STORAGE_DENIED/run-dir: restore run-directory write access, then resume.

## Final chat

Use the DONE template in references/chat-templates.md with Changed, optional Preexisting and Foreign, Checks with the review kind, Rulings, Deferred minors, and one final bold Action. Keep lists exhaustive and omit empty categories.
