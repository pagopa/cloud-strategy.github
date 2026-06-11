---
name: internal-gateway-simple-task
description: Use when a concrete low-to-medium-risk repository-owned coding or non-coding task can be answered, edited, diagnosed, validated, or executed quickly through one lane, including approved compact retained plans.
---

# Internal Gateway Simple Task

## Referenced skills

- `grill-me`: one focused clarification block for simple blockers.
- `internal-gateway-idea-brainstorming`: planning owner when simple work no longer fits.
- `internal-gateway-review`: review owner when defect-first analysis becomes dominant.
- `internal-gateway-critical-master`: critical owner when assumptions or failure modes dominate.
- `superpowers-verification-before-completion`: final evidence gate.

Use this skill as the skill-first fast path for concrete repository-owned work.
It is single-lane and single-phase by design. It also owns approved `compact`
retained-plan execution.

`references/support-routing.md` remains the single source of truth for claim-gate owners in simple mode.

## When to use

- The outcome, target, command, or validation path is already concrete.
- One quick lane can finish: `answer`, `edit`, `diagnose`, `validate`, or `execute`.
- Approved `compact` retained-plan execution is allowed when the folder declares
  `Recommended consumer: internal-gateway-simple-task`.

## When not to use

- Ownership, rollout, governance, or cross-boundary tradeoffs still need a decision; use `internal-gateway-idea-brainstorming`.
- The request is defect-first review; use `internal-gateway-review`.
- The request is approved `extended` retained-plan execution; use `internal-gateway-execute-plans`.
- The primary request is pressure testing; use `internal-gateway-critical-master`.

## Simple Flow

1. Inspect local files first.
2. Use at most one focused clarification block.
3. Confirm the task still fits one quick lane.
4. Select only directly applicable skill owners and required references from prompt, target path, runtime, ownership, and validation path.
5. Identify mandatory applicable requirements internally before execution; do not emit a default user checklist.
4. For approved `compact` plans, read `01-change-summary.md` and `02-source-item-ledger.md` first, verify the consumer contract, and confirm the folder uses the `mini-plan-*` prefix.
5. Execute the one concrete lane.
6. Run focused validation or name the explicit gap.
7. Run a pre-close compliance audit over mandatory applicable requirements only. Delegate fresh-evidence mechanics to `superpowers-verification-before-completion`.
8. Block completion claims when mandatory applicable requirements remain unverified.
9. If architecture ownership, owner conflicts, or validation strategy are ambiguous, escalate instead of assuming a universal rule.
7. If the task stops being simple, stop and issue an escalation alert.

## Validation

- Work stayed single-lane and single-phase, or escalation was explicit.
- Approved `compact` retained-plan execution stayed lightweight, used the `mini-plan-*` folder convention, and did not copy the extended `done-*` packaging loop.
- `compact` closeout still uses the shared completion contract: `State: SHIPPED` is the only state that permits `done-*` markers and numbered-file removal.
- Focused validation ran before completion claims, or the exact validation gap was reported.
- Completion claims were blocked when mandatory applicable requirements were still unverified.
- Output stayed concise unless a gap, exception, or escalation had to be reported.

## Common failure modes

- Treating loaded skills as automatically mandatory instead of checking applicability.
- Declaring completion after code edits while mandatory applicable evidence is still missing.
- Promoting specialist requirements to universal policy without target/runtime ownership proof.
- Continuing without escalation when ownership conflicts or validation strategy remain undefined.
