---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs an approved implementation plan written from an approved design or reviewed retained spec.
---

# Internal Gateway Writing Plans

Write one retained implementation plan through `/superpowers-writing-plans`
and hand it to `/internal-gateway-execute-plans`. This gateway adds only the
repository deltas: eligibility, plan location, test posture, authority, and the
report. The imported skill owns plan structure and self-review.

## When to use

- The user asks for an implementation plan from an approved design, a reviewed
  retained spec, or concrete direct requirements.
- `/internal-gateway-idea` hands off a `+plan` selection, with or without a
  retained spec marked `plan_authoring_ready: true`.

## When not to use

- Early or unclear ideas belong to `/internal-gateway-idea`.
- Bounded one-session work belongs to `/internal-gateway-simple-task`.
- Plan execution belongs to `/internal-gateway-execute-plans`.
- Edits to imported `superpowers-*` skills are out of scope.

## Eligibility

Write only when all three conditions hold:

1. The current conversation contains an explicit request to write a plan.
2. A source exists: a retained spec path, an approved design, a reviewed
   retained spec, or concrete direct requirements.
3. The target and the anti-scope are known.

A `+plan` selection satisfies conditions 1 and 2 without another discovery or
approval round. `implementation_permission: false` never blocks plan writing.
When a condition is missing, stop and name the one decision that unblocks it.

## Workflow

1. Load `/superpowers-writing-plans` and follow it for file structure, task
   right-sizing, step content, Interfaces, Global Constraints, Review Focus,
   and self-review.
2. Apply these repository deltas while writing:
   - Save the plan to `tmp/superpowers/plans/YYYY-MM-DD-HHMM-<topic>.md`.
   - Set the header `**Spec:**` to the source path. For direct requirements,
     write `direct requirements` and copy them into Global Constraints.
   - In the header, name `/internal-gateway-execute-plans` as the executor
     instead of the imported executors.
   - Classify every executable or evaluable task through `/internal-tdd`.
     Record one `Posture:` line per task and order its steps to match: red
     first for `mandatory-test-first`, a passing characterization check first
     for a behavior-preserving refactor, and implementation before validation
     for `feature-first`.
   - List every path a task may touch in its `Files:` block. The union of
     these blocks is the execution perimeter. Never list a protected imported
     skill path unless the user named that exact path in this conversation.
   - Write native, directly executable validation commands. Check that each
     tool exists before you write its command; never invent a command.
   - Write no commit steps. Replace each one with the task validation and
     `git status --short`.
3. Close with the imported handoff question. Offer `Inline` as the default and
   `Subagent-driven` as the alternative. The user's answer is the execution
   approval; do not start execution here.

## Boundaries

- No Git mutation while writing or handing off a plan.
- No execution, runtime status file, or ledger creation.
- A plan that still needs a user decision stays unfinished; do not hand it off.

## Report

Use exactly three lines, in the user's language, with canonical labels:

```text
Plan: <retained path>
Scope: <target; anti-scope>
Next: <answer the handoff question, or the one missing decision>
```
