# Manifest-only plan fixture

## Goal

Validate the manifest-authoritative execution CLI against a realistic writer output.

## Repository Preflight

- **Target:** manifest fixture validation.
- **Anti-scope:** no runtime changes.
- **Validation Path:** `python3 -m pytest -q tests/fixture/`
- **Stop Conditions:** fixture is incomplete.
- **Baseline Validation:** run `python3 -m pytest -q tests/fixture/` before edits.
- **Recovery Policy:** repair only task-local validation failures in scope.
- **Escalation Conditions:** request authority for scope expansion.
- **User-Facing Report:** summarize outcome, changes, validation, gaps, and next action.

## Global Constraints

- No Git mutation.
- Preserve fixture integrity.

## Status Contract

- YAML is the current runtime status and uses one uppercase sibling: `<plan-basename>.DONE.yaml`, `<plan-basename>.PARTIAL.yaml`, or `<plan-basename>.BLOCKED.yaml`.
- Runtime status uses schema version `2`; the Execution Manifest uses schema version `1`.
- The filename status and YAML `status` value must agree.
- `approval_evidence` records explicit execution approval and binds the current semantic fingerprint and content hash.
- `delivery_verdicts` records `structure`, `semantic_review`, `artifact_provenance`, `source_baseline`, and `execution_readiness`; `DONE` requires all five to pass.
- No alternate runtime status format is accepted.

## Control Inventory

| ID | Requirement | Class | Owner | Command or trigger | Pass/fail | Evidence | Fallback/boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CI-01 | Current retained plans expose the required structural controls. | automatable-local | gateway preflight | `gateway-tests` | Pass: manifest, inventory, and no-Git constraint are present; fail: any is missing. | Focused pytest output. | Legacy/imported plans remain non-actionable until reconstructed. |

## Execution Manifest

```json
{
  "schema_version": 1,
  "manifest_version": "execution-manifest/v1",
  "plan_id": "valid-plan",
  "repository_root": ".",
  "authority_boundaries": {
    "normative_owner": "/internal-gateway-writing-plans",
    "execution_owner": "/internal-gateway-execute-plans",
    "worker": "internal-luna-executor",
    "caller_owns": ["routing", "scope", "authority", "lifecycle", "retry", "independent_validation", "acceptance", "closeout"],
    "protected_paths": [".github/skills/mattpocock-research/**", ".github/skills/superpowers-*/**"],
    "no_git_mutation": true
  },
  "delegation": {
    "schema_version": 1,
    "mode": "none",
    "worker": "primary-owner",
    "result": null,
    "receipt": null,
    "acceptance": null
  },
  "targets": [
    {"id": "TGT-FIXTURE", "path": "tests/fixture/", "state": "inspect"}
  ],
  "controls": {
    "CI-01": {"class": "automatable-local", "owner": "gateway", "binding": ["T1", "focused-tests", "diff-check"]}
  },
  "validations": [
    {"id": "focused-tests", "command": "python3 -m pytest -q tests/fixture/", "owner": "fixture tests", "pass_signal": "exit-code-0", "phases": ["baseline", "focused", "final"], "equivalence": "allowed-if-admissible"},
    {"id": "diff-check", "command": "git diff --check", "owner": "gateway", "pass_signal": "exit-code-0", "phases": ["final"]}
  ],
  "manual_obligations": [],
  "tasks": [
    {"id": "T1", "order": 1, "posture": "validation-only", "objective": "Validate the manifest-authoritative CLI fixture.", "depends_on": [], "target_ids": ["TGT-FIXTURE"], "validation_ids": ["focused-tests", "diff-check"], "manual_obligation_ids": [], "acceptance": ["Manifest parses and binds its projection."], "stop_conditions": ["Fixture is incomplete."]}
  ],
  "retry_policy": {"initial_attempts": 1, "max_context_refills": 1, "max_corrective_retries": 1, "caller_may_lower": true, "repeat_progress_status": "stalled", "minor_or_cosmetic_reopens": false},
  "hashing": {"content_sha256": {"algorithm": "SHA-256", "input": "exact retained-plan bytes", "binding": "external"}, "semantic_fingerprint": {"algorithm": "SHA-256", "input": "RFC 8785 canonical Execution Manifest JSON", "version": "semantic-fingerprint/v1", "binding": "external"}, "self_reference": false},
  "approval": {"binds": "semantic_fingerprint", "editorial_content_change": "retain approval and update content_sha256 audit", "normative_manifest_change": "require renewed approval and preflight"},
  "bootstrap": {"mode": "manifest-only", "compatibility_projection": [], "projection_binding": {"controls": "manifest.controls", "tasks": "manifest.tasks", "validations": "manifest.validations", "authority": "manifest.authority_boundaries"}, "legacy_only": "reject", "retirement_evidence": "The writer emits this manifest without a legacy Execution Contract projection."},
  "rollout": ["baseline", "final"],
  "handoff": {"next_owner": "/internal-gateway-execute-plans", "requires": ["human approval", "exact semantic_fingerprint review", "zero blocking preflight findings"], "status_sibling": "none", "git_mutation": "prohibited"}
}
```

## Task 1: Validate CLI

**Files:**
- `scripts/plan_execution.py`

- [ ] Run `python3 -m pytest -q tests/fixture/`
- [ ] Confirm exit 0.
