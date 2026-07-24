---
name: internal-gateway-execute-plans
description: Use when executing or resuming an approved repository-owned retained plan under tmp/superpowers/.
---

# Internal Gateway Execute Plans

## Referenced skills

- `superpowers-executing-plans`: required owner for task-by-task plan execution.
- `internal-tdd`: repository-owned test-first route for tasks that change executable or evaluable behavior.
- `superpowers-verification-before-completion`: on-demand evidence gate before completion claims.
- `addyosmani-code-simplification`: plan-bound method owner only when the current approved plan task explicitly requires behavior-preserving simplification or records an approved review remediation.

Thin repository wrapper for approved retained-plan execution. It owns only
repo-local start, task-transition, stop, and status-file policy;
`superpowers-executing-plans` owns the execution loop.

## When to use

- Execute or resume an approved retained plan under `tmp/superpowers/`.
- Apply repo-local closeout through `<plan-basename>.<STATUS>.md`.

## When not to use

- Writing, reformulating, reviewing, or challenging a plan.
- Running same-chat work that is not driven by an approved retained plan.
- Changing `superpowers-executing-plans`; imported Superpowers behavior stays read-only unless the user explicitly changes scope.

## Execution Discipline

- Plan-bound: follow the approved retained plan and stop when it is no longer executable as written.
- DRY: do not duplicate execution workflow, validation reporting, status policy, or source logic owned elsewhere.
- YAGNI: do not add speculative helpers, abstractions, configuration, or future proofing beyond the approved plan.
- KISS: choose the simplest coherent change that satisfies the plan and stays readable.
- Separation of Concerns: keep planning, execution, validation evidence, closeout status, review, critique, and domain implementation separate.
- Single responsibility: each new helper, section, or code path must have one active-task reason.
- Tight feedback: treat the smallest coherent change set as one execution unit, then run its focused check. Coupled edits such as signature, callers, and body belong to one unit; unrelated plan tasks do not.
- Test first: when a task changes executable or evaluable behavior, load `internal-tdd` before its first implementation edit and follow the selected posture.
- Fail fast on drift: stop and record the defect when the plan forces confusing code, duplicated logic, missing validation, owner conflict, or scope drift.
- Scoped simplification: load `addyosmani-code-simplification` only when the current approved plan task explicitly requires behavior-preserving code simplification or records an approved review remediation; never introduce it as cleanup outside the approved plan.

## Contract

1. Confirm the retained plan folder, plan basename, and approval to execute.
2. Read only target, anti-scope, validation path, stop conditions, and first executable task.
3. On resume, verify any existing `<plan-basename>.<STATUS>.md`; do not resume from `DONE` unless fresh evidence invalidates it.
4. Announce this gateway, then load `superpowers-executing-plans` for critical plan review, todos, task execution, and its stop rules.
5. Before each task, name its observable outcome, dependency set, and focused validation. For interface or signature changes, identify affected callers, implementations, tests, and contracts before editing.
6. When the approved task authorizes simplification, establish the passing behavior baseline, load `addyosmani-code-simplification`, keep the refactor inside the task scope, and rerun the same focused validation afterward.
7. Execute one smallest coherent change set. Complete all known coupled edits, perform a consistency pass across the dependency set, then run the focused validation before widening the task.
8. Before marking a task complete or starting the next task, require fresh passing task-level evidence. If the check is missing, not run, or failing, keep the task in progress or blocked; do not claim completion.
9. Preserve compact state with targeted rereads. Summarize large validator output by command, exit code, material counts, changed files, and exact gaps.
10. Stop on scope drift, destructive action, owner conflict, missing validation path, human approval need, secret exposure risk, or repeated non-improving failures.
11. Before final response or pause, replace any older sibling `<plan-basename>.*.md` status file for the same plan basename, then write exactly one sibling status file named `<plan-basename>.<STATUS>.md`.

## No-Commit Rule

- The skill must never run `git add`, `git commit`, `git push`, `git merge`,
  or any other git mutation while executing, pausing, or closing out a plan.
  Executed changes stay uncommitted in the working tree; the user reviews and
  commits them personally.
- This rule is mandatory. The user may bypass it only with an explicit
  request for commit help in the current task; state the bypass in the status
  file and the final response.
- If an approved plan contains `git add`, `git commit`, or `git push` steps,
  skip them, record them as plan drift in the status file, and continue with
  the remaining steps.
- Do not run merge, push, or branch-cleanup actions from
  `superpowers-finishing-a-development-branch` unless the user explicitly
  chooses that action in the current task.

## Status closeout

Supported statuses are `DONE`, `BLOCKED`, `PARTIAL`, and `NEEDS_REVIEW`.
Required headings are `## Status`, `## Reason`, `## Completed`,
`## Remaining`, `## Validation`, `## Next`, and `## Resume Notes`.

Before claiming `DONE`, load `superpowers-verification-before-completion` and present fresh passing evidence.

Use `DONE` only when every task passed its transition gate, all in-scope work is complete, and required broader validation has fresh passing evidence. A final broad check does not retroactively validate skipped task gates. For any gap, use the status that best explains the remaining action and record the exact evidence needed to resume or finish.

Do not create `done-*`, `completion-report.md`, `evidence-envelope.md`, or `<STATE>-plan-state.md` as new closeout artifacts.

## Validation

- Pressure-check that a task cannot become complete without fresh focused evidence and that an interface change requires dependency consistency.
- Confirm no live repository references point to removed bundle files.
- `git diff --check`
- Confirm simplification loads only from an explicitly authorizing plan task, preserves task scope, and reruns the same focused validation used for the baseline.
