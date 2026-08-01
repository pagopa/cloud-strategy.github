# Evidence Contract

Keep one compact ledger across analysis cycles. Update deltas after a critical
re-entry instead of regenerating settled evidence.

## Target Brief

- `target`: repository, subsystem, or module under review.
- `nearest_owner`: repository policy or owner path.
- `goal`: desired architectural outcome.
- `anti_scope`: explicitly excluded work.
- `validation_path`: discovered checks and their owners.
- `baseline`: branch, dirty files, and relevant pre-change results.
- `immutable_dependencies`: referenced core bundles and evidence that they were
  not modified during the session.

## Evidence Dossier

- `current_interface`: public fields, methods, and contracts.
- `callers`: direct callers and their observable needs.
- `implementation_leakage`: hidden behavior that crosses the boundary.
- `dependencies`: dependency categories and coupling direction.
- `adapters`: real implementations and their variation points.
- `tests`: existing coverage and missing seams.
- `observable_contracts`: behavior, errors, ordering, and side effects.
- `deletion_test`: what disappears if the proposed module is removed.
- `gaps`: evidence not yet confirmed.

## Candidate Record

- `candidate_id`: stable identifier for the cycle.
- `proposed_deep_module`: behavior with a coherent responsibility.
- `seam`: a real behavior-variation point, not merely a file edge.
- `value`: expected leverage or locality improvement.
- `confidence`: confirmed, inferred, or estimated support.
- `blast_radius`: affected callers, adapters, tests, and migration surface.
- `reversibility`: rollback or containment path.
- `overlap_conflicts`: competing candidates and ownership collisions.
- `evidence_links`: dossier entries supporting the record.

## Design Packet

- `selected_candidate`: approved Candidate Record.
- `cycle`: current analysis/design cycle number.
- `packet_id`: stable ID binding approval, challenge, and handoff.
- `interface`: members plus invariants, ordering, and error behavior.
- `hidden_implementation`: details kept behind the boundary.
- `caller_mapping`: caller to productive operation and invariant.
- `test_surface`: behavior tests and seam tests, without test-only members.
- `dependency_strategy`: categories, adapters, and propagation plan.
- `alternatives_rejected`: design-it-twice comparison and reasons.
- `protected_behavior`: behavior and side effects that must remain stable.
- `migration_sequence`: bounded implementation order.
- `stop_conditions`: conditions that halt plan handoff or implementation.
- `validation_commands`: repository-owned checks for the future implementation.
- `approval_receipt`: explicit user approval naming this `cycle` and `packet_id`.

## Critical challenge records

- `critical_result`: the exact result returned by the existing
  `/internal-gateway-critical-master` call. Preserve its producer semantics;
  this gateway must not add fields, outcomes, or correlation metadata to it.
- `resolver_decision`: the pure `TransitionDecision` containing `next_state`,
  `approval_invalidated`, `reason`, and the required stop-report facts.

## Retained Design Artifact

The successful terminal output is a reviewable, disposable Design Artifact at:

`tmp/codebase-improvement/designs/YYYY-MM-DD-<target-slug>.md`

It must contain:

- Target Brief.
- Latest accepted Design Packet.
- Approval receipt naming the current cycle and packet ID.
- Matching critical receipt returned by `/internal-gateway-critical-master`.
- Critical Resolution Ledger.
- Validation path and fresh evidence.
- Explicit anti-scope.

The artifact remains uncommitted working state. It may be passed to
`/internal-gateway-writing-plans` only after a separate user request; this
gateway never invokes that owner automatically.

## Stop report

Every `stop-with-reason` decision records non-empty values for these six fields:

- `what_happened`
- `recovery_attempted`
- `evidence_unavailable_reason`
- `approval_status`
- `consequence`
- `resume_condition`

## Critical Resolution Ledger

- `cycle`: current analysis/design cycle number.
- `challenged_packet_id`: Design Packet ID challenged by the critic.
- `critic_objection`: objection, uncertainty, question, or risk.
- `evidence_required`: smallest evidence needed to resolve it.
- `resolution`: evidence-backed answer or unresolved state.
- `changed_decisions`: design or scope deltas.
- `approval_invalidated`: must be `true` for an open point.
- `critical_result`: canonical outcome, defense, and whether the result is clear.
- `next_state`: Analysis, Stop with reason, or Challenged Design Ready.

## Invariants

- Distinguish confirmed evidence, inference, and estimate.
- Do not call a file edge a seam without a behavior-variation point.
- Do not add interface members solely for tests.
- Require two real adapters before introducing an injectable seam.
- Apply the deletion test to both current and proposed modules.
- Compare proposed interfaces against anti-scope and rejected candidates.
- Retain only the latest accepted Design Packet in the Design Artifact.
- Bind the approval receipt, critical result, and retained artifact to the same
  current `cycle` and `packet_id`; mismatches are open points.
