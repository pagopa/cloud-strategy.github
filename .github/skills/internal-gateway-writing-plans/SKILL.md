---
name: internal-gateway-writing-plans
description: Use when repository-owned work needs a short repository preflight wrapper that delegates writing decisions to superpowers-writing-plans.
---

# Internal Gateway Writing Plans

## Referenced skills

- `superpowers-writing-plans`: required writing owner after preflight.

Repository-owned wrapper for retained planning requests. This skill does not
own a local retained-plan protocol or decide the output artifact.

## When to use

- Preparing a request for `superpowers-writing-plans` after a short repository
  preflight.
- Capturing the smallest target state, anti-scope, nearest owner, validation
  path, stop conditions, and observable acceptance before delegation.

## When not to use

- Clear, local, quick tasks whose next steps fit in chat and do not need a
  retained artifact.
- Substantive ideation before planning; use `internal-gateway-idea-brainstorming`.
- Editing imported `superpowers-*` skills.

## Contract

- Run a short preflight before loading `superpowers-writing-plans`.
- Delegate the next action to `superpowers-writing-plans`.
- `superpowers-writing-plans` will decide whether to create a retained plan,
  ask a blocking clarification, redirect to a better owner, or stop with a
  reason.
- Save created retained plans through the Superpowers default path:
  `tmp/superpowers/plans/YYYY-MM-DD-<feature-name>.md`.
- If a retained plan is created, run an `Execution-readiness check` before
  claiming completion.
- Stop after the delegated writing outcome and wait for the user's next choice.

## Preflight

- `Target`: the smallest target state that satisfies the request.
- `Anti-scope`: tempting work that must stay outside the plan.
- `Nearest owner`: repository owner or skill family that owns the change.
- `Validation path`: concrete validator, review path, or explicit validation gap.
- `Stop conditions`: missing input, unsafe scope, ownership conflict, or
  validation failure that must stop execution.
- `Observable acceptance`: diff, file state, validator assertion, manual check,
  or explicit non-action that proves the result.

## Execution-readiness check

For any created retained plan, verify task order, concrete file targets, clear
edit intent, validation commands or explicit gaps, stop conditions, and
handoff readiness for `superpowers-executing-plans` or
`superpowers-subagent-driven-development`.

Preserve known-context handoff quality with a short preflight and targeted rereads when the delegation leaves a gap.
