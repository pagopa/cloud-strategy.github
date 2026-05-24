# Simple Task Clarification Gate

Use this reference when simple mode may need one focused block of
clarification before a quick lane can continue.

## Core Rule

Simple mode allows at most one focused `grill-me` block. If the missing answer
would decide ownership, rollout, governance, tradeoffs, validation strategy, or
whether the work needs a plan, stop simple mode and escalate to
`internal-gateway-operational-flow`.

## Exit Check

Run this check before calling `grill-me`:

1. Does the prompt actually need a plan, retained plan, plan rewrite, review,
   or clarify-first workflow?
2. Would the missing answer change the owner, target state, anti-scope,
   validation path, or rollout posture?
3. Would more than one dependent clarification block be needed?

If any answer is yes, do not continue in simple mode.

## Single Clarification Limit

Use `grill-me` only when missing user intent, target path, input data, local
context, or a blocker prevents starting or continuing the active simple lane.
Ask only for the minimum context needed to resume the current lane.

If the first clarification answer creates another dependent question set, or if
the blocker still cannot be resolved inside the same focused block, escalate.

## grill-me Boundary

`grill-me` in simple mode may recover:

- missing file, path, or artifact target
- missing input data or reproduction step
- missing local context needed to start the chosen lane
- one blocker that prevents continuing an already valid simple lane

`grill-me` in simple mode must not decide:

- ownership, lane, or phase changes that need staged workflow
- rollout posture, governance, or approval boundaries
- design tradeoffs, architecture, or cross-boundary scope
- validation strategy beyond the nearest focused check

## Escalation Triggers

Escalate to `internal-gateway-operational-flow` when:

- the exit check fails
- the clarification limit is exceeded
- the answer would change simple-mode ownership or anti-scope
- the task now needs retained-plan, review, or critical-challenge handling
