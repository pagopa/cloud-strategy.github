# Continuation-First Recovery Contract

This is the authoritative recovery ladder for
`/internal-gateway-execute-plans`. The gateway owns route selection, recovery,
stopping, worktree/finishing decisions, and closeout; imported execution
mechanics do not override it. Keep the native authoritative command as the
evidence label even when a supported override or optional accelerator invokes
it.

Before recovery begins, the binding gate must have passed current-plan
`## Control Inventory` and explicit no-Git checks. A plan identified as
`legacy/imported` must be reconstructed through the writing gateway with
refreshed approval and fingerprint before execution or recovery can proceed.

## 1. Attribute

Prove whether the failure occurred in prerequisite discovery, wrapper startup,
validator execution, or validator result. Do not infer attribution from an
error label alone.

Completion: the failing phase and evidence are recorded.

## 2. Discover

Inspect, in order, repository-provided virtual environments, absolute
compatible executables, supported `PYTHON` or `PYTHON_BIN` overrides, native
commands, and cached dependencies. Probe RTK before using it; if it is absent,
stale, or unhealthy, use the native command. Treat a stale or failed graphify
query as unavailable and use the bounded search ladder below.

Completion: every safe in-scope candidate is listed with its compatibility
evidence.

## 3. Retry and repair exact

Rerun the authoritative command through a safe supported override when this
preserves its semantics. A possibly mutating command must not use blind
`accelerator || native` retry. If accelerator start state is unknown, inspect
observable state first and retry only through an idempotent path. After a failed
attempt, try each distinct safe repair or recovery candidate and rerun the exact
validation. Do not repeat an unchanged attempt unless a recorded external state
change makes it meaningful.

Completion: every attempted repair has a distinct evidence delta, or the next
attempt would cross an authority, safety, scope, or ownership boundary.

## 4. Validate equivalent

A direct validator is equivalent only when all four conditions are true:

- the target did not start;
- the same checks ran;
- the same inputs were used; and
- the runtime difference is not material.

Record these booleans in structured closeout evidence. `closeout-check`
rejects an equivalent pass without all four admissibility conditions and the
plan-declared `allowed-if-admissible` policy.

Completion: the equivalent result is represented as `equivalent-pass`, or it is
kept unresolved.

## 5. Escalate

Request user authority before installation, network access, destructive change,
ownership expansion, or plan modification. Do not convert an approval gap into
an autonomous terminal status.

Completion: authority is granted and used, or the request and refusal are
recorded as external evidence.

## 6. Exhaust

Record attempted candidates, the evidence delta from each attempt, rejected
candidates, and why no safe candidate remains. An environmental label alone is
not exhaustion evidence.

Completion: the candidate list is empty or every remaining candidate requires
new authority, and the rejection reasons are explicit.

## 7. Decide

Build the JSON evidence document and run:

```text
python3 scripts/plan_execution.py closeout-check <plan-file> <evidence-file> --format compact
```

Continue immediately for `continue-execution` or `continue-recovery`; do not
write an intermediate status sibling. Write exactly one status sibling only
for `DONE`, `PARTIAL` with an explicit pause, `BLOCKED` with exhausted fatal
evidence, or `NEEDS_REVIEW` with completed work, an observed material failure,
exhausted recovery, and a structured review request. Pending human or external
evidence without an observed material failure is recorded as non-blocking
follow-up on a successful `DONE` closeout; it is not by itself a review route.
The local gateway makes this decision; imported core mechanics cannot create a
status sibling or change the route.

## Bounded graphify fallback

When graphify is absent, stale, or fails, ask one bounded evidence question,
inspect aggregate facts, then use filename discovery and one narrow `rg`
query. Read only local ranges around matches. Widen one dimension only when a
named evidence gap remains, and stop once the question is answered. Record the
bounded result and stop condition; optional-tool availability is never itself a
blocker.
