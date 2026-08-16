# Internal Subagent Contract v1

This reference describes the portable protocol behind the compact skill
surface. It is guidance for producers and consumers; the Python validator is
the executable boundary.

## DelegationBrief

The producer writes one JSON object with exactly these top-level fields:

```json
{
  "schema_version": 1,
  "delegation_id": "stable-id",
  "mode": "read|write|plan",
  "objective": "one observable outcome",
  "value_gate": {
    "autonomous": true,
    "verifiable": true,
    "leverage": "bounded rationale"
  },
  "evidence": [{"ref": "path-or-fact", "purpose": "why it is needed"}],
  "constraints": ["binding must or must-not rule"],
  "write_scope": ["repository-relative path or directory root"],
  "expected_output": {
    "kind": "artifact|analysis|patch|validation",
    "path": "repository-relative path or null",
    "format": "json|markdown|patch|text"
  },
  "acceptance": [{"id": "A1", "observable": "caller-checkable condition"}],
  "validation": [{
    "id": "V1",
    "owner": "worker|caller",
    "command": "exact command",
    "pass_signal": "exit-code-0"
  }],
  "budgets": {"attempts": 2, "context_refills": 1},
  "result_path": "repository-relative result path",
  "cache": {
    "prefix_version": "internal-subagent-contract/v1",
    "key_class": "worker-role"
  }
}
```

`read` briefs have an empty `write_scope` and a null expected-output path.
Every path is repository-relative and must not contain an absolute prefix or a
parent traversal. The producer may lower the attempt/refill budgets but may
not raise the protocol bounds. Evidence and acceptance entries are bounded
facts, not a pasted conversation.

Evidence references use a deterministic v1 convention: `fact:<text>` is an
inline fact, `path:<repository-relative-path>` is an explicit path, and a bare
repository-relative path is retained as the compatibility form of a path
reference. Callers materialize applicable policy and resolve only these
references before worker execution. Globs, ambiguous duplicates, traversal,
missing paths, and symlink targets outside the repository or declared scope
are rejected. A directory reference may expand recursively only within its
resolved root and caller limits.

## WorkerResult

The worker returns one structured object. The result ID must equal the brief
ID, and `brief_sha256` must hash the exact brief bytes supplied to the worker.

```json
{
  "schema_version": 1,
  "delegation_id": "stable-id",
  "brief_sha256": "sha256:<64-hex-digits>",
  "status": "completed",
  "value_delivered": true,
  "summary": "short factual result",
  "artifacts": [{
    "path": "declared/repository-relative/path",
    "sha256": "sha256:<64-hex-digits>",
    "kind": "artifact-kind"
  }],
  "evidence": [{
    "acceptance_id": "A1",
    "ref": "file, command, diff, or test",
    "outcome": "pass|fail|not_run"
  }],
  "non_blocking_findings": ["Minor observation"],
  "remaining": ["unmet acceptance or material gap"],
  "progress_signature": "sha256:<64-hex-digits>",
  "retry": {
    "recommended": false,
    "reason": "why a retry is or is not appropriate",
    "required_new_input": null
  },
  "budgets_used": {"wall_seconds": null, "attempts": 1, "context_refills": 0}
}
```

An evidence entry may use `kind` instead of `acceptance_id` for a generic
evidence inventory; callers use acceptance IDs when proving a value claim.
The consumer verifies artifact bytes and does not trust a path or hash stated
by the worker. A result with `value_delivered: true` must contain an artifact
or an acceptance-bound pass evidence entry.

The runtime adapter may compose deterministic v1 fields from the exact brief
bytes, observed telemetry, and persisted artifact bytes, but it must not
rewrite semantic worker fields. Adapter mismatches remain visible; they are
never silently repaired.

## LifecycleRecord v1

When no terminal worker payload exists, the caller records a separate
`LifecycleRecord`; it does not create a synthetic `WorkerResult` or
`VerificationReceipt`:

```json
{
  "schema_version": 1,
  "delegation_id": "stable-id",
  "brief_sha256": "sha256:<64-hex-digits>",
  "lifecycle": {
    "event": "timeout|interrupted|unavailable|no_terminal_result",
    "source": "caller",
    "reason": "why no terminal payload exists",
    "evidence_ref": "caller:timeout"
  },
  "terminal": {"state": "stalled|unavailable", "output": null},
  "worker_result": null,
  "verification_receipt": null
}
```

`stalled` is used for timeout, interruption, and missing terminal output.
`unavailable` identifies an unavailable executor. The caller may persist this
record as a deterministic `.lifecycle.json` sibling outside worker scope.

## VerificationReceipt v1

`VerificationReceipt v1` is caller-owned and separate from `WorkerResult v1`.
It binds one brief/result pair and stores the raw worker payload hash and an
optional raw-payload reference. Its fixed top-level shape is:

```json
{
  "schema_version": 1,
  "delegation_id": "stable-id",
  "brief_sha256": "sha256:<64-hex-digits>",
  "result_path": "caller/result.result.json",
  "raw_worker": {"sha256": "sha256:<64-hex-digits>", "ref": null},
  "attestations": {
    "brief_binding": {"state": "verified", "source": "adapter", "evidence_ref": "..."},
    "artifact_integrity": {"state": "verified", "source": "adapter", "evidence_ref": "..."},
    "declared_scope": {"state": "verified", "source": "adapter", "evidence_ref": "..."},
    "execution_confinement": {"state": "unavailable", "source": "runtime", "evidence_ref": "..."},
    "validation_execution": {"state": "worker_claim", "source": "worker", "evidence_ref": "..."},
    "budget_accounting": {"state": "unavailable", "source": "runtime", "evidence_ref": "..."},
    "result_persistence": {"state": "unavailable", "source": "adapter", "evidence_ref": "..."},
    "caller_acceptance": {"state": "unavailable", "source": "caller", "evidence_ref": "..."}
  },
  "caller_decision": {"decision": "not_decided", "source": "caller", "evidence_ref": "..."},
  "value_verified": false
}
```

Each attestation state is exactly `verified`, `worker_claim`, `unavailable`,
or `failed`. A worker-declared validation remains `worker_claim` until the
runtime or caller observes its command, outcome, and evidence. Missing
telemetry is `unavailable`; it is never invented. The caller decision is
separate and is exactly `accepted`, `rejected`, or `not_decided`.

The caller or adapter persists `result_path` outside worker `write_scope` and
stores the receipt at its deterministic `.receipt.json` sibling. `value_verified`
belongs only to the receipt and can be true only after caller acceptance and
verified attestations. V1 validates one brief/result pair; `retry`, `attempts`,
`context_refills`, and `progress_signature` remain compatibility fields, while
retry eligibility is not a new lifecycle owner.

## Progress and retry eligibility

The validator hashes this material projection with compact, sorted-key JSON:

```json
{
  "status": "partial",
  "artifacts": [{"path": "out.md", "sha256": "sha256:..."}],
  "evidence": [{"acceptance_id": "A1", "ref": "V1", "outcome": "pass"}],
  "remaining": ["one bounded item"],
  "required_new_input": "new validator output"
}
```

Artifact and evidence lists, and remaining strings, are normalized for stable
comparison. Reordering keys, whitespace, or prose-only/non-blocking findings
does not constitute progress. The projection is correlation data for one pair;
v1 neither defines attempt lineage nor performs retry. `retry_eligible()` is a
deprecated caller-side compatibility utility and must receive no new
dependencies. Lineage-aware lifecycle behavior requires a later version.

## Stable prompt order and telemetry

When a runtime constructs a worker prompt, stable content precedes dynamic
content in this order:

```text
role -> protocol -> schemas -> mode -> optional breakpoint -> brief -> retry evidence
```

The versioned prefix is:

```text
internal-subagent-contract/v1 | role=bounded-worker | no-nested-agents | result-schema=1 | stop-on-missing-facts-or-repeat-signature
```

Cache controls are optional optimizations, never correctness conditions. Use
`cache_mode=implicit|explicit|unsupported` and record `cached_tokens`,
`cache_write_tokens`, and non-cached input tokens only when the runtime exposes
them. Do not put timestamps, raw user text, secrets, delegation IDs, or raw
paths in stable cache content. Missing cache-write telemetry is an external
capability gap, not a protocol pass.

Caller-owned receipts may include worker status, value bit, progress signature,
attempt/refill counts, latency, token fields when available, artifact count,
and validation outcome. Redact brief content, secrets, and sensitive paths.

## Migration notes

Keep routing, authority, scope, lifecycle, retry choice, independent
validation, acceptance, and closeout with each caller. A worker profile may
enforce its own no-nesting boundary, but this passive protocol does not select
or invoke agents. Existing callers should migrate to the same fields and
version, remove caller-identity branches, and retain their domain-specific
acceptance. Protected or provider-specific callers remain external
compatibility cases; the protocol does not import their policy.
