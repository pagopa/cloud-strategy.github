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

V1 binds one brief/result pair. It is an integrity and handoff protocol, not a
sandbox or proof that every execution fact was observed. A deterministic
runtime adapter composes hashes, telemetry, persistence, and a separate
caller-owned `VerificationReceipt` without changing semantic worker fields.

## When to use

Use it at the producer/worker/consumer boundary when a bounded task needs a
machine-readable brief, result, artifact hash, acceptance evidence, or
progress check. Do not use it as a router, retry loop, reviewer, or lifecycle
owner.

## Roles

- The producer writes a complete `DelegationBrief` with a measurable objective,
  value gate, bounded evidence, write scope, acceptance, and budgets.
- The worker reads caller-authorized policy and brief evidence, performs the
  bounded assignment, writes only declared artifacts, and returns semantic
  worker fields.
- The runtime adapter composes the deterministic `WorkerResult` envelope,
  persists it outside worker scope, and produces a `VerificationReceipt`.
- The consumer checks result and receipt before deciding acceptance, retry,
  promotion, or closeout.

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

Evidence uses `fact:<inline-value>` or `path:<repository-relative-path>`;
unprefixed repository paths remain the v1 compatibility form. Resolved paths
form the worker read allowlist. All branches use the same versioned fields. The protocol does not select a
provider, model, skill, route, reviewer, retry, or acceptance decision.

## Status and retry breaker

Results use `completed`, `partial`, `blocked`, `stalled`, `invalid_input`, or
`failed`. Attempt, refill, retry, and progress fields remain compatible claims
for one pair; v1 does not own multi-attempt lineage. `retry_eligible()` is a
deprecated caller-side compatibility utility. Missing authority and invalid
input stop the worker. Minor or prose-only findings do not justify a retry.

## Completion criteria

The consumer accepts a result only after it verifies the adapter-composed
result and caller-owned receipt. Receipt attestations are `verified`,
`worker_claim`, `unavailable`, or `failed`; caller acceptance stays separate.
Use the executable validator in
`scripts/subagent_contract.py`; load `references/protocol.md` for examples,
canonical projections, cache fields, and migration details.
