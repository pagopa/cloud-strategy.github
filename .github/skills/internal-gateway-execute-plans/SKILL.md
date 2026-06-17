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

1. Read `01-change-summary.md` first.
2. For `compact`, read `02-execution.md`; for `extended`, read `02-control.md`.
3. Verify `Plan profile: compact` or `Plan profile: extended`, then infer the execution strategy from profile, folder shape, and validation path.
4. Establish execution state from summary, control file, and active validator outcomes; keep it compact and update it as items close.
5. Avoid repeated full rereads: inspect changed sections, active executable item context, and failing-validator evidence first.
6. Run the ledger evidence pass.
7. Identify mandatory applicable requirements from selected skills using target, runtime, ownership, and validation path.
8. For `compact`, confirm the folder uses `mini-plan-*` and `02-execution.md` is the only executable file.
9. For `extended`, read numbered executable files after `02-control.md` in order starting at `03-execution.md`.
10. Process numbered executable files in order.
11. Run an item-level compliance audit before closing each executable item.
12. Track progress through the live ledger.
13. Aggregate unresolved mandatory applicable requirements before closeout.
14. Package closeout only for `DONE`.

## Execution Contract

- Reject unsupported profiles immediately.
- Reject `compact` folders outside the `mini-plan-*` convention.
- Ignore `questions.md` during execution.
- Maintain a compact execution state and prefer targeted rereads over full file re-ingestion unless new evidence invalidates current state.
- Infer the execution strategy from `Plan profile`, folder shape, merged control-contract sections in `02-control.md` when applicable, and the validation path. Do not require a separate retained-plan consumer field.
- Audit only mandatory requirements that are applicable; do not convert specialist rules into universal policy.
- Use `superpowers-verification-before-completion` as the fresh-evidence owner; do not duplicate its mechanics.
- Block item closure and block `SHIPPED` whenever mandatory applicable requirements remain unverified.
- Escalate architecture ownership conflicts, cross-owner skill conflicts, and undefined validation strategy.
- Pressure-test boundary: a Lambda-owned hashed requirements file does not grant a separate stdlib-only CLI launcher permission to install that dependency set.
- Only `DONE` may create `done-*` markers or remove numbered plan files, or publish a lightweight `DONE-plan-state.md` marker (`<STATE>-plan-state.md` convention) with `State: DONE` and `Continuation: none`.
- Non-`DONE` exits keep the live ledger and numbered files in place.

## Validation

- Summary and profile-control files are read first.
- `Plan profile` is `compact` or `extended`.
- Execution strategy is inferred from profile, folder shape, and validation path.
- `compact` retained plans use `tmp/superpowers/mini-plan-*` and `02-execution.md` as the only executable file.
- `extended` retained plans include `02-control.md` before executable work.
- Mandatory applicable requirements are checked at item close and before `DONE`.
- Missing mandatory applicable evidence maps to a non-`DONE` state.
- `done-*` markers appear only during full close packaging; lightweight closeout uses `<STATE>-plan-state.md` (for closed plans: `DONE-plan-state.md`) and may retain numbered files.

## Common failure modes

- Closing an item because edits exist while mandatory applicable evidence is still open.
- Treating every loaded specialist rule as mandatory without applicability proof.
- Hiding ownership conflicts instead of escalating a next owner and validation path.
- Packaging `DONE` while evidence gaps still require `APPLIED_UNVERIFIED`, `PARTIAL`, or `BLOCKED`.
