---
name: internal-gateway-execute-plans
description: Use when executing or resuming an approved repository-owned retained plan under tmp/superpowers/.
---

# Internal Gateway Execute Plans

## Referenced skills

- `superpowers-executing-plans`: required owner for task-by-task plan execution.
- `superpowers-verification-before-completion`: on-demand evidence gate before completion claims.

Thin repository wrapper for approved retained-plan execution. It owns only
repo-local start, stop, and status-file policy; `superpowers-executing-plans`
owns the execution loop.

## When to use

- Execute or resume an approved retained plan under `tmp/superpowers/`.
- Apply repo-local closeout through `<plan-basename>.<STATUS>.md`.

## When not to use

- Writing, reformulating, reviewing, or challenging a plan.
- Executing `questions.md` or unapproved planning notes.
- Running same-chat work that is not driven by an approved retained plan.
- Changing `superpowers-executing-plans`; imported Superpowers behavior stays read-only unless the user explicitly changes scope.

## Execution Discipline

- Plan-bound: follow the approved retained plan and stop when it is no longer executable as written.
- DRY: do not duplicate execution workflow, validation reporting, status policy, or source logic owned elsewhere.
- YAGNI: do not add speculative helpers, abstractions, configuration, or future proofing beyond the approved plan.
- KISS: choose the simplest coherent change that satisfies the plan and stays readable.
- Separation of Concerns: keep planning, execution, validation evidence, closeout status, review, critique, and domain implementation separate.
- Single responsibility: each new helper, section, or code path must have one active-task reason.
- Fail fast on drift: stop and record the defect when the plan forces confusing code, duplicated logic, missing validation, owner conflict, or scope drift.

## Contract

1. Confirm the retained plan folder, plan basename, and approval to execute.
2. Read only target, anti-scope, validation path, stop conditions, and first executable task. Treat `questions.md` as non-executable.
3. On resume, verify any existing `<plan-basename>.<STATUS>.md`; do not resume from `DONE` unless fresh evidence invalidates it.
4. Announce this gateway, then load `superpowers-executing-plans` for critical plan review, todos, task execution, and its stop rules.
5. Preserve compact state with targeted rereads. Summarize large validator output by command, exit code, material counts, changed files, and exact gaps.
6. Stop on scope drift, destructive action, owner conflict, missing validation path, human approval need, secret exposure risk, or repeated non-improving failures.
7. Before final response or pause, write exactly one sibling status file named `<plan-basename>.<STATUS>.md`.

## Status closeout

Supported statuses are `DONE`, `BLOCKED`, `PARTIAL`, and `NEEDS_REVIEW`.
Required headings are `## Status`, `## Reason`, `## Completed`,
`## Remaining`, `## Validation`, `## Next`, and `## Resume Notes`.

Use `DONE` only when all in-scope work is complete and required validation has fresh passing evidence. For any gap, use the status that best explains the remaining action and record the exact evidence needed to resume or finish.

Do not create `done-*`, `completion-report.md`, `evidence-envelope.md`, or `<STATE>-plan-state.md` as new closeout artifacts.

## Validation

- `python3 ./.github/scripts/validate_internal_skills.py --skill internal-gateway-execute-plans --strict`
- Confirm no live repository references point to removed bundle files.
- `git diff --check`
