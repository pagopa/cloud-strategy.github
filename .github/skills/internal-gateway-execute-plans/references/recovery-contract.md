# Continuation-First Recovery Contract

This is the authoritative recovery ladder for the gateway. Keep the native
authoritative command as the evidence label even when a supported override or
optional accelerator invokes it.

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

## 3. Retry exact

Rerun the authoritative command through a safe supported override when this
preserves its semantics. A possibly mutating command must not use blind
`accelerator || native` retry. If accelerator start state is unknown, inspect
observable state first and retry only through an idempotent path.

Completion: the retry ran once and produced a distinct evidence delta.

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
evidence, or `NEEDS_REVIEW` with completed work and exhausted human, external,
or non-substitutable environmental evidence.

## Bounded graphify fallback

When graphify is absent, stale, or fails, ask one bounded evidence question,
inspect aggregate facts, then use filename discovery and one narrow `rg`
query. Read only local ranges around matches. Widen one dimension only when a
named evidence gap remains, and stop once the question is answered. Record the
bounded result and stop condition; optional-tool availability is never itself a
blocker.
