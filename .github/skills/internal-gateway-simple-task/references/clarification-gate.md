# Simple Task Clarification Gate

Use this reference when simple mode must decide whether to run the full
interview and critical gate, prove a trivial skip, or ask one focused blocker
question before a quick lane can continue.

## Core Rule

Simple mode defaults to a full gate for non-trivial work: ask one compact focused `grill-me` block before operational work, then run
`internal-gateway-critical-master` after the user's interview response. Ask the
user to respond first to `grill-me` and then to the critical outcome.

Skip both gates only with a Trivial-skip proof. The proof must show the task is
trivial and venial, no depth keyword is present, and the focused validation path
or gap is already clear.

If the missing answer would decide ownership, rollout, governance, tradeoffs,
validation strategy, or whether the work needs a plan, stop simple mode and
escalate to `internal-gateway-idea-brainstorming` or `internal-gateway-review`.

If the clarification or full gate reveals material risk, hidden assumptions, or
dominant failure-mode pressure, escalate to `internal-gateway-critical-master`.

## Depth Keyword Override

Treat `full`, `idea`, and `complete` as user-forced full-gate keywords when the
request still targets simple mode. Do not use `trivial-skip` after one of these
keywords. Run `grill-me` first, then the critical gate, unless the keyword proves
the task belongs to a narrower planning, review, or pressure-testing owner.

## Exit Check

Run this check before skipping or calling `grill-me`:

1. Did the user provide a depth keyword: `full`, `idea`, or `complete`?
2. Is the task more than a local answer, tiny edit, focused read, or validator
    run with obvious validation?
3. Does the prompt actually need a plan, retained plan, plan rewrite, review,
    or clarify-first workflow?
4. Would the missing answer change the owner, target state, anti-scope,
    validation path, or rollout posture?
5. Would more than one dependent clarification block be needed?

If answer 1 or 2 is yes and answers 3-5 are no, use the full gate. If any of
answers 3-5 is yes, do not continue in simple mode.

## Single Clarification Limit

Use one compact `grill-me` block for the full gate or when missing user intent,
target path, input data, local context, or a blocker prevents starting or
continuing the active simple lane. Ask only for the minimum context needed to
resume the current lane.

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

Escalate to `internal-gateway-idea-brainstorming`,
`internal-gateway-review`, or `internal-gateway-critical-master` when:

- the exit check fails
- the clarification limit is exceeded
- the answer would change simple-mode ownership or anti-scope
- the task now needs retained-plan, review, or critical-challenge handling
- material risk or failure-mode pressure dominates
