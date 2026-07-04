---
name: internal-gateway-execute-plans
description: Use when executing an approved repository-owned retained plan and repo-local policy must wrap superpowers-executing-plans with a resumable status file.
---

# Internal Gateway Execute Plans

gateway-only wrapper for approved retained plans. This skill does not replace `superpowers-executing-plans`; it activates before that skill and adds repository-local execution policy.

## Referenced Skills

- `superpowers-executing-plans`: required execution engine for the plan steps.
- `superpowers-verification-before-completion`: evidence gate before completion claims when fresh validation is required.

## When To Use

- Executing approved retained plans under `tmp/superpowers/`.
- Resuming approved retained plans that were previously stopped through this gateway.
- Applying repo-local status-file policy before using `superpowers-executing-plans`.

## When Not To Use

- Writing or reformulating a plan.
- Reviewing or challenging a plan.
- Executing `questions.md` or unapproved planning notes.
- Changing `superpowers-executing-plans`; this wrapper must not patch imported Superpowers behavior.

## Execution Discipline

- Plan-bound execution: follow the approved retained plan and stop when the plan is no longer executable as written.
- DRY: do not duplicate gateway workflow logic, status-file handling, validation reporting, or source logic when an existing owner already provides it.
- YAGNI: do not add speculative helpers, abstractions, configuration, or future-proofing beyond the approved plan.
- KISS: prefer the simplest coherent change that satisfies the plan and remains readable.
- Separation of Concerns: keep execution, status files, validation evidence, planning, review, critique, and domain implementation responsibilities separate.
- single responsibility: each new helper, script, section, or code path must have one clear reason tied to the active task.
- Fail-fast on drift: stop and record the defect when the plan forces confusing code, duplicated logic, missing validation, owner conflict, or scope drift.

## Wrapper Contract

1. Confirm the retained plan path and that execution is approved.
2. Read the smallest plan context needed to identify target, anti-scope, validation path, and stop conditions.
3. If the plan is a compact plan, read `02-execution.md`; if it is an extended plan, read `02-control.md` before numbered execution files.
4. Announce that this gateway is wrapping `superpowers-executing-plans`.
5. Invoke `superpowers-executing-plans` for the task-by-task execution loop.
6. Preserve compact execution state. Prefer targeted rereads over full re-ingestion unless new evidence invalidates the current state.
7. Use Compact Evidence Reporting for large validator output: retain command, exit code, material counts, changed files, and exact gaps without pasting raw logs when a summary preserves the evidence.
8. Stop on scope drift, destructive action, owner conflict, missing validation path, human approval need, secret exposure risk, or repeated non-improving failures.
9. Before final response or pause, write exactly one status file in the retained plan folder named `<plan-basename>.<STATUS>.md`.
10. No `DONE` claim is allowed unless the status file exists and fresh evidence supports `DONE`, or the status file records the exact validation gap under another status.

## Status File Contract

`<plan-basename>` is the retained plan folder name. Supported statuses:

- `DONE`: all in-scope work is complete and required validation passed.
- `BLOCKED`: a real blocker or required external/user action prevents safe continuation.
- `PARTIAL`: some in-scope work remains incomplete or intentionally deferred.
- `NEEDS_REVIEW`: work was applied but review, validation, or evidence coverage is still required before `DONE`.

Required headings:

- `## Status`
- `## Reason`
- `## Completed`
- `## Remaining`
- `## Validation`
- `## Next`
- `## Resume Notes`

The status file must be short, factual, and useful to a later agent. It must state why the current status was chosen and what evidence or action is needed to resume or finish.

## Legacy Contract Boundary

This gateway no longer owns `done-*` packaging, `completion-report.md`, `evidence-envelope.md`, or `<STATE>-plan-state.md` markers. Existing historical artifacts may be read as evidence, but new gateway output uses `<plan-basename>.<STATUS>.md`.

## Validation

- The wrapper references `superpowers-executing-plans` and does not duplicate its execution algorithm.
- The retained plan path and plan basename are known before execution starts.
- The final or paused state maps to exactly one supported status.
- The status file exists in the retained plan folder.
- The status filename, status value, and required headings match the contract.
- Fresh validation evidence or an explicit validation gap is recorded before any completion claim.
