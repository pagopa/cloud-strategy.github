---
name: internal-subagent-contract
description: Use when validating the caller-owned contract for one bounded subagent brief and result.
---

# Internal Subagent Contract

Use this skill when a caller needs a small, structured handoff to one bounded
worker and must verify the returned evidence. The contract is passive: it
defines the brief/result shape and validates protocol invariants. The caller
chooses whether delegation is worthwhile, owns scope and authority, selects
the runtime, validates acceptance, and closes the work.

## When to use

Use it at the producer/worker/consumer boundary when a bounded task needs a
machine-readable brief, result, artifact hash, acceptance evidence, or
progress check. Do not use it as a router, retry loop, reviewer, or lifecycle
owner.

## Roles

- The producer writes a complete `DelegationBrief` with a measurable objective,
  value gate, bounded evidence, write scope, acceptance, and budgets.
- The worker reads only that brief, performs the bounded assignment, writes only
  declared artifacts, and returns a `WorkerResult`.
- The consumer independently checks hashes, scope, evidence, acceptance, and
  the result status before deciding what happens next.

## Value gate

Delegation is valid only when the brief says why the work is autonomous,
verifiable, and materially more useful than a trivial local operation. A short
answer, one obvious edit, one command, or an unverifiable request fails the
gate. `value_delivered: true` requires an artifact or acceptance-bound pass
evidence; a prose summary is not value.

## Three protocol branches

- `read` supplies bounded evidence and produces no worker write scope.
- `write` supplies a bounded implementation or artifact scope.
- `plan` supplies bounded drafting scope and a caller-owned acceptance check.

All branches use the same versioned fields. The protocol does not select a
provider, model, skill, route, reviewer, retry, or acceptance decision.

## Status and retry breaker

Results use `completed`, `partial`, `blocked`, `stalled`, `invalid_input`, or
`failed`. One initial attempt, at most one context refill, and at most one
corrective retry are the default upper bounds; a caller may lower them.
Repeated material progress is `stalled`. Missing authority, invalid input,
and repeated progress stop the worker. Minor, cosmetic, punctuation, and
prose-only findings never reopen a retry.

## Completion criteria

The consumer accepts a result only after it verifies the delegation ID, exact
brief hash, artifact hashes and repository-relative scope, acceptance evidence,
progress signature, and budget use. Use the executable validator in
`scripts/subagent_contract.py`; load `references/protocol.md` for examples,
canonical projections, cache fields, and migration details.
