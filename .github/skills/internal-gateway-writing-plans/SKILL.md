---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs a short preflight before delegating retained writing to superpowers-writing-plans.
---

# Internal Gateway Writing Plans

## Referenced skills

- `superpowers-writing-plans`: required owner after the repository preflight.

Thin repository wrapper for retained writing. This skill records the local
handoff facts, delegates artifact decisions to `superpowers-writing-plans`, and
stops after the delegated outcome.

## When to use

- Use after the user approves retained spec or implementation-plan writing.
- Do not use for quick same-chat tasks, substantive ideation, execution, or
  imported `superpowers-*` edits.

## Contract

1. Capture the preflight: `Target`, `Anti-scope`, `Nearest owner`,
   `Validation path`, `Stop conditions`, and `Observable acceptance`.
2. Load `superpowers-writing-plans` and let it create a plan, ask a blocking
   clarification, redirect, or stop with a reason.
3. If a retained plan is created, verify execution-readiness: ordered tasks,
   concrete file targets, clear edit intent, validation commands or explicit
   gaps, stop conditions, and handoff readiness.
4. Stop after the writing outcome and wait for the user's next choice.

Preserve handoff quality with targeted rereads only when the delegation has a
real evidence gap.
