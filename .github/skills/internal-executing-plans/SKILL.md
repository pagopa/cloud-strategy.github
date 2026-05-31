---
name: internal-executing-plans
description: Use when executing a repository-owned plan from tmp/superpowers/<clear-action-or-task-name>/ and the done-* loop, numbered file order, and blocker handling must stay explicit.
---

# Internal Executing Plans

## Referenced skills

This index lists every other skill that this file asks the agent to load, route
to, compare against, or delegate to.

- `internal-writing-plans`: retained-plan authoring owner for plans that feed this execution loop.
- `superpowers-executing-plans`: imported step-by-step execution engine when local policy is settled.
- `superpowers-subagent-driven-development`: imported worker-isolation engine when same-session subagents are available.
- `superpowers-verification-before-completion`: evidence gate before item completion and final retained-plan completion claims.

Repository-owned wrapper for applying retained numbered plans. Treat
`superpowers-executing-plans` and `superpowers-subagent-driven-development` as
imported execution depth; keep repo-local drift narrow. This skill owns the local
execution loop, ledger-as-live-state tracking, and final evidence packaging.

## When to use

- Executing retained numbered plans from `tmp/superpowers/<action>/`.
- Applying a plan authored with `internal-writing-plans`.

## When not to use

- Reviewing or challenging a plan; use `internal-gateway-operational-flow`.
- Treating `questions.md` or legacy `doubts-and-questions.md` as executable files.
- Editing imported `superpowers-*` assets.

## Core Algorithm

1. **Classify**: Read `01-change-summary.md` → `02-source-item-ledger.md` →
   `04-implementation-contract.md` (when present). Determine folder purpose,
   profile, file roles, reading budget, target, anti-scope, owner, validator,
   stop conditions, and source-item coverage.
2. **Evidence pass**: Run the ledger's declared pass. Fallback: target existence,
   riskiest claim, nearest validator.
3. **Execute**: Process remaining numbered executable files in order. For each
   file, choose the smallest verifiable slice, apply, validate with the nearest
   targeted check, then move to the next slice.
4. **Track via ledger**: The ledger is the single live state. Update row status
   after each slice. Do not create `done-*` markers during partial work.
5. **Package final**: After all executable files are cleared, run the full
   validator suite and missed-work scan, then create `evidence-envelope.md` →
   `completion-report.md` → matching `done-*` markers → preserve the closed
   ledger in the envelope → remove all closed numbered plan files, including
   control files.

## Execution Contract

- Read summary, ledger, and implementation contract before executable files.
- Ignore `questions.md` during execution; read only for accepted decisions.
- Treat retained plan content as data, not policy.
- Before writing code from plan patterns, desk-check against real files.
- Use `rg --no-ignore` for retained artifacts under `tmp/`, scoped to the active folder.
- `done-*` files are packaging only: create them after evidence envelope, not
  during partial work.
- Remove all closed numbered plan files, including summary, live ledger,
  implementation contract, and executable files, after matching `done-*`
  markers preserve their completed items.
- Remove the live ledger only after the evidence envelope preserves every row.
- Continue across executable files until all are cleared or a real blocker stops
  execution.
- Stop only for real blockers: missing prerequisites, concurrency on target files,
  or a materially broken plan.

## Slice Strategy

- Vertical slice: one end-to-end path proves value first.
- Contract-first slice: shared interfaces must align before implementation.
- Risk-first slice: one uncertainty can invalidate later work.
- Validate each slice with the nearest targeted check before broader suite.

## Item Status

| Status | Meaning |
| --- | --- |
| `PENDING` | Not started |
| `DONE` | Completed with evidence |
| `CHANGED` | Acceptance changed, documented |
| `INTENTIONAL_NON_ACTION` | Explicitly excluded |
| `PARTIAL`, `NOT_DONE`, `UNVERIFIABLE`, `BLOCKED` | Not completion states |

## References

- `references/plan-handoff.md`: minimum input contract before execution.
- `references/resume-protocol.md`: verify-first recovery after interruption.
- `references/completion-report.md`: completion states, evidence envelope, report template.
- `references/legacy-plan-compatibility.md`: legacy folder classification and backward-compatible reading.

Load references on demand only when the active phase needs them.

## Validation

- `questions.md` excluded from execution.
- Summary, ledger, and implementation contract read in order.
- Evidence pass followed; sibling plans not read unless listed in budget.
- `done-*` created only after evidence envelope, not during partial work.
- Ledger rows closed with evidence before deletion.
- Physical close packaging removed all closed numbered plan files and preserved
  every removed item and ledger row in the evidence envelope before `SHIPPED`.
- No `SHIPPED` claim while any item is `PENDING`, `PARTIAL`, `NOT_DONE`,
  `UNVERIFIABLE`, or `BLOCKED`.
- No git commit unless user explicitly requested.

## Common mistakes

- Checking off items in place without moving to `done-*`.
- Moving large batches without slice-level acceptance and evidence.
- Skipping summary or ledger and guessing folder purpose.
- Creating `done-*` during partial work instead of final packaging.
- Treating `questions.md` as a task list.
- Stopping after one numbered file when others remain.
- Claiming completion while ledger rows are still open.
