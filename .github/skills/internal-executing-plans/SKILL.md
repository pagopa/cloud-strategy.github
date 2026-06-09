---
name: internal-executing-plans
description: Use when executing an approved extended repository-owned plan from tmp/superpowers/<clear-action-or-task-name>/ and the done-* loop, numbered file order, and blocker handling must stay explicit.
---

# Internal Executing Plans

## Referenced skills

- `internal-writing-plans`: retained-plan authoring owner for plans that feed this execution loop.
- `superpowers-executing-plans`: imported step-by-step execution engine when local policy is settled.
- `superpowers-subagent-driven-development`: imported worker-isolation engine when same-session subagents are available.
- `superpowers-verification-before-completion`: evidence gate before item completion and final retained-plan completion claims.

Repository-owned wrapper for applying retained numbered plans. This owner only
consumes approved `extended` plans.

## When to use

- Executing approved `extended` retained plans from `tmp/superpowers/<action>/`.
- Applying an `extended` plan authored with `internal-writing-plans`.

## When not to use

- Reviewing or challenging a plan; use `internal-gateway-review` or `internal-gateway-critical-master`.
- Executing `compact` plans; use `internal-gateway-simple-task`.
- Treating `questions.md` as an executable file.

## Core Algorithm

1. Read `01-change-summary.md`, `02-source-item-ledger.md`, and `04-implementation-contract.md`.
2. Verify `Plan profile: extended` and `Recommended consumer: internal-executing-plans`.
3. Run the ledger evidence pass.
4. Process numbered executable files in order.
5. Track progress through the live ledger.
6. Package closeout only for `SHIPPED`.

## Execution Contract

- Reject unsupported profiles immediately.
- Reject any folder whose recommended consumer is not `internal-executing-plans`.
- Ignore `questions.md` during execution.
- Only `SHIPPED` creates `done-*` markers or removes numbered plan files.
- Non-`SHIPPED` exits keep the live ledger and numbered files in place.

## Validation

- Summary, ledger, and implementation contract are read first.
- `Plan profile` is `extended`.
- `Recommended consumer` equals `internal-executing-plans`.
- `done-*` markers appear only during close packaging.
