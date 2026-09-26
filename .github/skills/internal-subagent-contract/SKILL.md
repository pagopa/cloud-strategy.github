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

- A bounded task at the producer/worker/consumer boundary needs a
  machine-readable brief, result, artifact hash, acceptance evidence, or
  progress check.

## When not to use

- Routing, retry loops, review, or lifecycle ownership. The caller keeps these
  decisions.

## Roles

- **Producer:** writes a complete `DelegationBrief` with a measurable
  objective, value gate, bounded evidence, write scope, acceptance, and
  budgets.
- **Worker:** reads caller-authorized policy and brief evidence, performs the
  bounded assignment, writes only declared artifacts, and returns semantic
  worker fields.
- **Runtime adapter:** composes the deterministic `WorkerResult` envelope,
  persists it outside worker scope, and produces a `VerificationReceipt` when
  a terminal worker payload exists. Otherwise the caller records a separate
  `LifecycleRecord`.
- **Consumer:** checks result and receipt before deciding acceptance, retry,
  promotion, or closeout.

## Value gate

Delegation is valid only when the brief says why the work is autonomous,
verifiable, and materially more useful than a trivial local operation. A short
answer, one obvious edit, one command, or an unverifiable request fails the
gate. `value_delivered: true` requires an artifact or acceptance-bound pass
evidence; a prose summary is not value.

For `mode: plan`, the `value_gate` also requires non-empty
`local_alternative` and `off_critical_path` fields:

- The caller compares the worker package with the actual primary-owner
  alternative and explains why the package is not on the critical path.
- The validator checks only that both fields are present and non-empty; the
  caller owns the semantic admission decision.
- If the comparison or rationale is not substantive, the caller uses local
  authoring with `mode: none` instead of invoking a worker.
- Provider or model identity never satisfies this gate.

## Protocol branches

- `read` supplies bounded evidence and produces no worker write scope.
- `write` supplies a bounded implementation or artifact scope.
- `plan` supplies bounded drafting scope and a caller-owned acceptance check.

All branches use the same versioned fields. Evidence uses
`fact:<inline-value>` or `path:<repository-relative-path>`; unprefixed
repository paths remain the v1 compatibility form. Resolved paths form the
worker read allowlist. The protocol does not select a provider, model, skill,
route, reviewer, retry, or acceptance decision.

## Status and retry breaker

Results use `completed`, `partial`, `blocked`, `stalled`, `invalid_input`, or
`failed`. Attempt, refill, retry, and progress fields remain compatible claims
for one pair; v1 does not own multi-attempt lineage. `retry_eligible()` is a
deprecated caller-side compatibility utility. Missing authority and invalid
input stop the worker. Minor or prose-only findings do not justify a retry.

## Worker result projection

The worker returns one compact semantic result, not a progress transcript:

```text
Status: <completed | partial | blocked | stalled | invalid_input | failed>
Value: <true/false and one factual sentence>
Artifacts: <path + verified kind, or none>
Evidence: <acceptance-bound outcomes only>
Remaining: <material gaps, or none>
Retry: <recommended/not recommended + required new input>
```

The caller-owned `VerificationReceipt` remains separate and is not repeated in
the worker summary. A result is not accepted because its prose sounds
complete: the caller must verify the declared bytes, scope, evidence, receipt,
and acceptance decision.

## Lifecycle record projection

When a timeout, interruption, unavailable executor, or missing terminal output
prevents a worker payload, the caller records lifecycle evidence separately
from the worker protocol. It must not be converted into a successful
`WorkerResult` or a fabricated receipt.

```text
Event: <timeout | interrupted | unavailable | no_terminal_result>
Terminal: <stalled | unavailable>; output=<none>
WorkerResult: <none>
VerificationReceipt: <none>
Owner: caller
```

`stalled` is the terminal classification for timeout, interruption, and
missing terminal output. `unavailable` records an unavailable executor. The
record binds the delegation ID and exact brief hash, and may be persisted as a
`.lifecycle.json` sibling without creating result or receipt files.

## Validation

Run the bundle validator from the repository root:

```bash
python3 <this-bundle>/scripts/subagent_contract.py brief <brief.json>
python3 <this-bundle>/scripts/subagent_contract.py result <result.json> <brief.json>
python3 <this-bundle>/scripts/subagent_contract.py progress-signature <result.json>
```

## Completion criteria

The consumer accepts a result only after it verifies the adapter-composed
result and caller-owned receipt as described in
[Worker result projection](#worker-result-projection). Receipt
attestations are `verified`,
`worker_claim`, `unavailable`, or `failed`; caller acceptance stays separate.

## References

- [`references/protocol.md`](references/protocol.md): load for examples,
  canonical projections, cache fields, and migration details.
