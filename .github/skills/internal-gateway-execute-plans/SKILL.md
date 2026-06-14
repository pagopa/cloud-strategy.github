---
name: internal-gateway-execute-plans
description: Use when executing an approved compact or extended repository-owned plan from tmp/superpowers/<clear-action-or-task-name>/ and the numbered-file order, done-* loop, and blocker handling must stay explicit.
---

# Internal Gateway Execute Plans

## Referenced skills

- `internal-gateway-writing-plans`: retained-plan authoring owner for plans that feed this execution loop.
- `superpowers-executing-plans`: imported step-by-step execution engine when local policy is settled.
- `superpowers-subagent-driven-development`: imported worker-isolation engine when same-session subagents are available.
- `superpowers-verification-before-completion`: evidence gate before item completion and final retained-plan completion claims.

Repository-owned wrapper for applying retained numbered plans. This owner
consumes approved `compact` and `extended` retained plans.

## When to use

- Executing approved `compact` retained plans from `tmp/superpowers/mini-plan-*`.
- Executing approved `extended` retained plans from `tmp/superpowers/<action>/`.
- Applying a `compact` or `extended` plan authored with `internal-gateway-writing-plans`.

## When not to use

- Reviewing or challenging a plan; use `internal-gateway-review` or `internal-gateway-critical-master`.
- Treating `questions.md` as an executable file.

## Core Algorithm

1. Read `01-change-summary.md` and `02-source-item-ledger.md`.
2. Verify `Plan profile: compact` or `Plan profile: extended`, then infer the execution strategy from profile, folder shape, and validation path.
3. Run the ledger evidence pass.
4. Identify mandatory applicable requirements from selected skills using target, runtime, ownership, and validation path.
5. For `compact`, confirm the folder uses `mini-plan-*`, `questions.md` is `- none`, and `03-execution.md` is the only executable file.
6. For `extended`, read `04-implementation-contract.md` before executable files.
7. Process numbered executable files in order.
8. Run an item-level compliance audit before closing each executable item.
9. Track progress through the live ledger.
10. Aggregate unresolved mandatory applicable requirements before closeout.
11. Package closeout only for `SHIPPED`.

## Execution Contract

- Reject unsupported profiles immediately.
- Reject `compact` folders outside the `mini-plan-*` convention.
- Ignore `questions.md` during execution.
- Infer the execution strategy from `Plan profile`, folder shape, `04-implementation-contract.md` presence when applicable, and the validation path. Do not require a separate retained-plan consumer field.
- Audit only mandatory requirements that are applicable; do not convert specialist rules into universal policy.
- Use `superpowers-verification-before-completion` as the fresh-evidence owner; do not duplicate its mechanics.
- Block item closure and block `SHIPPED` whenever mandatory applicable requirements remain unverified.
- Escalate architecture ownership conflicts, cross-owner skill conflicts, and undefined validation strategy.
- Pressure-test boundary: a Lambda-owned hashed requirements file does not grant a separate stdlib-only CLI launcher permission to install that dependency set.
- Only `SHIPPED` creates `done-*` markers or removes numbered plan files.
- Non-`SHIPPED` exits keep the live ledger and numbered files in place.

## Validation

- Summary and ledger are read first.
- `Plan profile` is `compact` or `extended`.
- Execution strategy is inferred from profile, folder shape, and validation path.
- `compact` retained plans use `tmp/superpowers/mini-plan-*` and `03-execution.md` as the only executable file.
- `extended` retained plans include `04-implementation-contract.md` before executable work.
- Mandatory applicable requirements are checked at item close and before `SHIPPED`.
- Missing mandatory applicable evidence maps to a non-`SHIPPED` state.
- `done-*` markers appear only during close packaging.

## Common failure modes

- Closing an item because edits exist while mandatory applicable evidence is still open.
- Treating every loaded specialist rule as mandatory without applicability proof.
- Hiding ownership conflicts instead of escalating a next owner and validation path.
- Packaging `SHIPPED` while evidence gaps still require `APPLIED_UNVERIFIED`, `PARTIAL`, or `BLOCKED`.
