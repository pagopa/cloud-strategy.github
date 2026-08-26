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

- YAML is the current runtime status and uses one uppercase sibling: `<plan-basename>.DONE.yaml`, `<plan-basename>.DONE_WITH_WARNINGS.yaml`, `<plan-basename>.PARTIAL.yaml`, or `<plan-basename>.BLOCKED.yaml`.
- The Execution Manifest uses schema version `3`; runtime status uses schema version `2`.
- The filename status and YAML `status` value must agree.
- `approval_evidence` records only the source and exact statement of explicit execution approval.
- `delivery_verdicts` records `structure`, `semantic_review`, `artifact_provenance`, `source_baseline`, and `execution_readiness`; `DONE` requires all five to pass.
- No alternate runtime status format is accepted.

## Control Inventory

| ID | Requirement | Class | Owner | Command or trigger | Pass/fail | Evidence | Fallback/boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CI-01 | Current retained plans expose the required structural controls. | automatable-local | gateway preflight | `gateway-tests` | Pass: manifest, inventory, and no-Git constraint are present; fail: any is missing. | Focused pytest output. | Imported or pre-v3 plans remain non-actionable until reconstructed. |

## Execution Manifest

```json
{
  "schema_version": 3,
  "manifest_version": "execution-manifest/v3",
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
    "result": "not_applicable",
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
  "retry_policy": {"initial_attempts": 1, "max_context_refills": 1, "max_corrective_retries": 3, "caller_may_lower": true, "repeat_progress_status": "stalled", "minor_or_cosmetic_reopens": false},
  "approval": {"editorial_content_change": "retain approval for non-normative wording", "normative_manifest_change": "require renewed approval and v3 preflight"},
  "bootstrap": {
    "mode": "manifest-only",
    "compatibility_projection": [],
    "projection_binding": {
      "controls": "manifest.controls",
      "tasks": "manifest.tasks",
      "validations": "manifest.validations",
      "authority": "manifest.authority_boundaries"
    },
    "legacy_only": "reject",
    "retirement_evidence": "This retained plan emits no legacy projection; the Manifest v3 object is the sole execution contract."
  },
  "rollout": ["baseline", "final"],
  "handoff": {"next_owner": "/internal-gateway-execute-plans", "requires": ["human approval", "exact Manifest v3 review", "zero blocking preflight findings"], "status_sibling": "none", "git_mutation": "prohibited"}
}
```

## Valid DONE_WITH_WARNINGS Status

```yaml
schema_version: 2
status: DONE_WITH_WARNINGS
plan: tmp/superpowers/plans/valid-plan.md
approval_evidence:
  source: current-conversation
  statement: explicit execution approval
delivery_verdicts:
  - {category: structure, outcome: passed, coverage: fixture, limit: none}
  - {category: semantic_review, outcome: passed, coverage: fixture, limit: none}
  - {category: artifact_provenance, outcome: passed, coverage: fixture, limit: none}
  - {category: source_baseline, outcome: passed, coverage: fixture, limit: none}
  - {category: execution_readiness, outcome: passed, coverage: fixture, limit: none}
completed_task_ids: [T1]
remaining_task_ids: []
last_validation: focused fixture validation passed
next_action: none
warnings:
  - kind: human-follow-up
    evidence: Offline review remains open.
    next_action: Complete the offline review.
deviations: []
```

## Invalid Technical Warning Status

```yaml
schema_version: 2
status: DONE_WITH_WARNINGS
plan: tmp/superpowers/plans/valid-plan.md
approval_evidence:
  source: current-conversation
  statement: explicit execution approval
delivery_verdicts:
  - {category: structure, outcome: passed, coverage: fixture, limit: none}
  - {category: semantic_review, outcome: passed, coverage: fixture, limit: none}
  - {category: artifact_provenance, outcome: passed, coverage: fixture, limit: none}
  - {category: source_baseline, outcome: failed, coverage: fixture, limit: technical failure}
  - {category: execution_readiness, outcome: passed, coverage: fixture, limit: none}
completed_task_ids: [T1]
remaining_task_ids: []
last_validation: fixture validation failed
next_action: Repair the technical failure.
warnings:
  - kind: external-unavailable
    evidence: External evidence was unavailable.
    next_action: Collect the evidence before closeout.
deviations: []
```

## Deviation Fixtures

```yaml
schema_version: 2
status: PARTIAL
plan: tmp/superpowers/plans/valid-plan.md
approval_evidence:
  source: current-conversation
  statement: explicit execution approval
delivery_verdicts:
  - {category: structure, outcome: passed, coverage: fixture, limit: none}
  - {category: semantic_review, outcome: passed, coverage: fixture, limit: none}
  - {category: artifact_provenance, outcome: passed, coverage: fixture, limit: none}
  - {category: source_baseline, outcome: passed, coverage: fixture, limit: none}
  - {category: execution_readiness, outcome: inconclusive, coverage: fixture, limit: pending}
completed_task_ids: []
remaining_task_ids: [T1]
last_validation: fixture validation paused
next_action: Continue the approved task loop.
warnings: []
deviations:
  - task: T1
    mismatch: target already has the declared state
    resolution: Keep the target unchanged and record the observation.
```

## Task 1: Validate CLI

**Files:**
- `scripts/plan_execution.py`

- [ ] Run `python3 -m pytest -q tests/fixture/`
- [ ] Confirm exit 0.
