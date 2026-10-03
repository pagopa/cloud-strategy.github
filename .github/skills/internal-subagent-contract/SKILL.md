---
name: internal-subagent-contract
description: Use when writing, executing, or checking one bounded subagent handoff under the internal-subagent-contract/v1 protocol, including a DelegationBrief, the worker's semantic result, the WorkerResult, a VerificationReceipt, or a LifecycleRecord.
---

# Internal Subagent Contract

This skill defines one structured handoff between a caller and one bounded
worker, and it ships a validator for that handoff. It is a protocol, not a
router: the caller decides whether to delegate, picks the worker, owns scope
and authority, runs acceptance, and closes the work. The protocol never
selects a provider, model, skill, reviewer, retry, or acceptance decision.

V1 binds exactly one brief and one result. It proves integrity and binding;
it does not sandbox the worker or prove facts that nobody observed.

## When to use

- A caller is about to delegate one bounded task and needs a checkable brief.
- A worker received a `DelegationBrief` and must return its result.
- A caller must check a returned result, receipt, or missing result before it
  accepts, retries, or closes the work.

Keep routing, retry loops, review, and lifecycle ownership with the caller.
When delegation fails the value gate, the primary owner does the work locally
and writes no brief.

## Roles

| Role | Owns | Produces |
| --- | --- | --- |
| Caller (producer) | Value gate, scope, authority, budgets, evidence | `DelegationBrief` |
| Worker | The bounded assignment only | Artifacts in `write_scope` and one semantic payload |
| Runtime adapter | Hashes, telemetry, persistence | `WorkerResult` and `VerificationReceipt` |
| Caller (consumer) | Acceptance, retry choice, closeout | Receipt decision or `LifecycleRecord` |

One agent may act as caller, adapter, and consumer. The worker role stays
separate: a worker never writes the receipt or decides acceptance.

## Caller: write the brief

1. Pass the value gate. Delegate only when the brief can state why the work is
   autonomous, verifiable, and materially more useful than doing it locally.
   A short answer, one obvious edit, one command, or an unverifiable request
   fails the gate. Provider or model identity never satisfies it.
2. Pick the mode. Valid values are exactly `read`, `write`, and `plan`.
   - `read`: bounded evidence in, analysis out; `write_scope` is `[]` and
     `expected_output.path` is `null`.
   - `write`: one bounded implementation or artifact scope.
   - `plan`: one bounded draft plus a caller-owned acceptance check. The
     `value_gate` also needs non-empty `local_alternative` (the real
     primary-owner alternative) and `off_critical_path` (why the next handoff
     does not wait on this worker). The validator checks presence only; the
     caller judges substance and works locally when the comparison is weak.
3. List evidence as `fact:<inline value>` or `path:<repository-relative path>`.
   Resolved paths form the worker's read allowlist. Globs, `..`, absolute
   paths, and missing paths are rejected. Bare relative paths remain valid for
   compatibility.
4. Keep every path repository-relative. Budgets may be at most
   `attempts: 2` and `context_refills: 1`.
5. Run `brief` validation (see [Validation](#validation)) and fix every error
   before handing the brief to a worker.

The full field list and examples are in the DelegationBrief section of
[`references/protocol.md`](references/protocol.md).

## Worker: execute and return

1. Read only caller-authorized policy and the brief's evidence.
2. Do the one assignment. Write only inside `write_scope`. Do not invoke,
   spawn, or hand off to another agent.
3. Stop early with the matching status when facts, authority, capability,
   scope, or budget are missing. Do not guess the missing input.
4. Return one JSON object with exactly these ten fields and no others:

   ```json
   {
     "schema_version": 1,
     "delegation_id": "<same as the brief>",
     "status": "completed",
     "value_delivered": true,
     "summary": "one factual sentence",
     "artifacts": [{"path": "<inside write_scope>", "kind": "<artifact kind>"}],
     "evidence": [{"acceptance_id": "A1", "ref": "<file, command, or test>", "outcome": "pass"}],
     "non_blocking_findings": [],
     "remaining": [],
     "retry": {"recommended": false, "reason": "<why>", "required_new_input": null}
   }
   ```

   Leave out `brief_sha256`, `progress_signature`, and `budgets_used`; the
   adapter computes them and rejects a payload that supplies them. Artifact
   `sha256` is optional and must match the file bytes when present.
5. Set `value_delivered: true` only with an artifact or an acceptance-bound
   `pass` evidence entry. A prose summary is not value.
6. When a worker can run commands, check the payload before returning it:
   `worker-payload` in [Validation](#validation).

A short human summary may follow the JSON. It never replaces the JSON.

### Status selection

| Status | Use when |
| --- | --- |
| `completed` | Every acceptance item has `pass` evidence. |
| `partial` | Some acceptance is met; `remaining` lists each gap. |
| `blocked` | Authority, capability, or scope is missing. |
| `invalid_input` | The brief is contradictory, incomplete, or invalid. |
| `stalled` | Material progress repeats, so another attempt would not change the result. |
| `failed` | The work was attempted and cannot meet acceptance. |

`blocked` and `invalid_input` stop the worker. Recommend a retry only with a
concrete `required_new_input`. Minor, cosmetic, or prose-only findings go in
`non_blocking_findings` and never justify a retry.

## Caller: check and decide

1. Compose the `WorkerResult` and receipt with the adapter in
   `scripts/runtime_evidence.py` (`compose_handoff`, then `persist_handoff`).
   The adapter must not rewrite semantic worker fields; a mismatch fails.
2. Verify artifact bytes, declared scope, evidence, and the receipt yourself.
   Do not accept a result because its prose sounds complete.
3. Read each receipt attestation as `verified`, `worker_claim`,
   `unavailable`, or `failed`. A worker-declared validation stays
   `worker_claim` until the caller or runtime observes it. Missing telemetry
   stays `unavailable`.
4. Record the separate caller decision: `accepted`, `rejected`, or
   `not_decided`. `value_verified: true` requires acceptance and verified
   attestations.
5. When a timeout, interruption, unavailable executor, or missing terminal
   output leaves no worker payload, record a `LifecycleRecord` with
   `compose_lifecycle_record`. Do not create a `WorkerResult` or receipt for
   that case.

```text
Event: <timeout | interrupted | unavailable | no_terminal_result>
Terminal: <stalled | unavailable>; output=<none>
WorkerResult: <none>
VerificationReceipt: <none>
Owner: caller
```

`unavailable` marks an unavailable executor; the other events are `stalled`.
Result, receipt, and lifecycle files use the `.result.json`, `.receipt.json`,
and `.lifecycle.json` siblings outside the worker's `write_scope`.

Progress and retry fields describe one pair only. V1 owns no multi-attempt
lineage; `retry_eligible()` is a deprecated caller-side helper and takes no
new dependencies.

## Validation

Run from the repository root. Each command prints `valid` and exits `0`, or
prints one error per line and exits `1`.

```bash
python3 <this-bundle>/scripts/subagent_contract.py brief <brief.json>
python3 <this-bundle>/scripts/subagent_contract.py worker-payload <payload.json> <brief.json>
python3 <this-bundle>/scripts/subagent_contract.py result <result.json> <brief.json>
python3 <this-bundle>/scripts/subagent_contract.py progress-signature <result.json>
```

`worker-payload` checks the raw ten-field worker object; `result` checks the
adapter-composed `WorkerResult`. Receipts and lifecycle records are checked
through `validate_receipt` and `validate_lifecycle_record` in the same script.

## Completion criteria

- The brief passes `brief` validation before any worker runs.
- The worker payload passes `worker-payload`, or the caller records why it
  could not run.
- The consumer has a receipt with every attestation state set and a separate
  caller decision, or a `LifecycleRecord` when no payload exists.
- No accepted result rests only on worker prose or unobserved claims.

## References

- [`references/protocol.md`](references/protocol.md): full schemas, receipt
  and lifecycle shapes, progress signature, prompt order, cache fields, and
  migration notes.
