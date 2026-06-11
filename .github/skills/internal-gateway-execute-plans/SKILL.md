---
name: internal-gateway-execute-plans
description: Use when executing an approved extended repository-owned plan from tmp/superpowers/<clear-action-or-task-name>/ and the done-* loop, numbered file order, and blocker handling must stay explicit.
---

# Internal Gateway Execute Plans

## Referenced skills

- `internal-gateway-writing-plans`: retained-plan authoring owner for plans that feed this execution loop.
- `superpowers-executing-plans`: imported step-by-step execution engine when local policy is settled.
- `superpowers-subagent-driven-development`: imported worker-isolation engine when same-session subagents are available.
- `superpowers-verification-before-completion`: evidence gate before item completion and final retained-plan completion claims.

Repository-owned wrapper for applying retained numbered plans. This owner only
consumes approved `extended` plans.

## When to use

- Executing approved `extended` retained plans from `tmp/superpowers/<action>/`.
- Applying an `extended` plan authored with `internal-gateway-writing-plans`.

## When not to use

- Reviewing or challenging a plan; use `internal-gateway-review` or `internal-gateway-critical-master`.
- Executing `compact` plans; use `internal-gateway-simple-task`.
- Treating `questions.md` as an executable file.

## Core Algorithm

1. Read `01-change-summary.md`, `02-source-item-ledger.md`, and `04-implementation-contract.md`.
2. Verify `Plan profile: extended` and `Recommended consumer: internal-gateway-execute-plans`.
3. Run the ledger evidence pass.
4. Identify mandatory applicable requirements from selected skills using target, runtime, ownership, and validation path.
5. Process numbered executable files in order.
6. Run an item-level compliance audit before closing each executable item.
7. Track progress through the live ledger.
8. Aggregate unresolved mandatory applicable requirements before closeout.
9. Package closeout only for `SHIPPED`.

## Execution Contract

- Reject unsupported profiles immediately.
- Reject any folder whose recommended consumer is not `internal-gateway-execute-plans`.
- Ignore `questions.md` during execution.
- Audit only mandatory requirements that are applicable; do not convert specialist rules into universal policy.
- Use `superpowers-verification-before-completion` as the fresh-evidence owner; do not duplicate its mechanics.
- Block item closure and block `SHIPPED` whenever mandatory applicable requirements remain unverified.
- Escalate architecture ownership conflicts, cross-owner skill conflicts, and undefined validation strategy.
- Pressure-test boundary: a Lambda-owned hashed requirements file does not grant a separate stdlib-only CLI launcher permission to install that dependency set.
- Only `SHIPPED` creates `done-*` markers or removes numbered plan files.
- Non-`SHIPPED` exits keep the live ledger and numbered files in place.

## Validation

- Summary, ledger, and implementation contract are read first.
- `Plan profile` is `extended`.
- `Recommended consumer` equals `internal-gateway-execute-plans`.
- Mandatory applicable requirements are checked at item close and before `SHIPPED`.
- Missing mandatory applicable evidence maps to a non-`SHIPPED` state.
- `done-*` markers appear only during close packaging.

## Common failure modes

- Closing an item because edits exist while mandatory applicable evidence is still open.
- Treating every loaded specialist rule as mandatory without applicability proof.
- Hiding ownership conflicts instead of escalating a next owner and validation path.
- Packaging `SHIPPED` while evidence gaps still require `APPLIED_UNVERIFIED`, `PARTIAL`, or `BLOCKED`.
