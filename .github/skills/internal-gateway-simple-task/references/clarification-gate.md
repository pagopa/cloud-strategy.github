# Simple Task Clarification Gate

Use this reference when the simple-task bundle must decide whether one focused clarification can keep the current lane moving.

## Core Rule

Default to the full gate for non-trivial work: bounded evidence, Initial Idea Ordering, one compact `grill-me` block when needed, critical challenge, then the internal readiness record. Complete the internal readiness record, then render only the compact user-facing projection. Do not paste the internal record or Gate Evidence.

Skip the gate only with a Trivial-skip proof showing:

- the task is tiny and local
- no depth keyword is present
- the validation path is obvious or the validation gap is explicit

If a missing answer would change scope, validation, cost, risk, or target state, stop with reason instead of continuing.

Treat `clarification` as `skipped` when local evidence already answers the question or the task is `trivial-skip`.
Treat `clarification` as `blocked` when the missing answer would change scope, validation, cost, risk, or target state.

## Exit Check

Run this check before asking a clarification:

1. Did the user force a deeper posture with `full`, `idea`, or `complete`?
2. Is the task more than a local answer, tiny edit, focused read, or validator run?
3. Would the missing answer change scope, anti-scope, validation path, or approval boundary?
4. Would more than one dependent clarification block be needed?
5. Would the answer turn the task into multi-phase, costly, or unsafe work?

If `1` or `2` is yes and `3-5` are no, use the full gate. If any of `3-5` is yes, stop with reason.

## Single Clarification Limit

Ask at most one compact `grill-me` block for:

- missing file, path, or artifact target
- missing input data or reproduction step
- missing local context needed to start the chosen lane
- one blocker preventing an otherwise valid simple lane

If that answer creates another dependent question set, stop with reason.

## `grill-me` Boundary

`grill-me` may recover:

- a missing path or artifact
- a missing reproduction step
- one bounded blocker
- one missing local fact needed to execute

`grill-me` must not decide:

- staged workflow changes
- architecture or design tradeoffs
- rollout posture
- approval boundaries
- broad validation strategy redesign

## Stop Conditions

Stop conditions are owned by `references/support-routing.md`; this gate adds only the per-question stop rules listed in Stop rules above.
