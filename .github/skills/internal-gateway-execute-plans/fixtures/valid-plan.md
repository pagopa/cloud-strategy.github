## Goal

Validate the plan execution CLI against a realistic plan shape.

## Repository Preflight

- **Target:** test fixture validation.
- **Anti-scope:** no runtime changes.
- **Validation Path:** `pytest -q tests/fixture/`
- **Stop Conditions:** fixture is incomplete.
- **Baseline Validation:** run `pytest -q tests/fixture/` before edits.
- **Recovery Policy:** repair only task-local validation failures in scope.
- **Escalation Conditions:** continue proven pre-existing or unrelated failures; stop on unsafe continuation or unresolved task-local regression.
- **User-Facing Report:** summarize outcome, changes, validation, recovery, gaps, and next action.

## Global Constraints

- No Git mutation.
- Preserve fixture integrity.

## Control Inventory

| ID | Requirement | Class | Owner | Command or trigger | Pass/fail | Evidence | Fallback/boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CI-01 | Current retained plans expose the required structural controls. | automatable-local | executor preflight | `gateway-tests` | Pass: inventory and no-Git constraint are present; fail: either is missing. | Focused pytest output. | Legacy/imported plans remain non-actionable until reconstructed. |

## Execution Contract

```json
{
  "schema_version": 1,
  "validations": [
    {
      "id": "focused-tests",
      "command": "python3 -m pytest -q tests/fixture/",
      "phases": ["baseline", "focused", "final"],
      "required": true,
      "success": "exit-code-0",
      "equivalence": "allowed-if-admissible"
    },
    {
      "id": "diff-check",
      "command": "git diff --check",
      "phases": ["final"],
      "required": true,
      "success": "exit-code-0",
      "equivalence": "exact-only"
    }
  ],
  "manual_obligations": [],
  "authority": {
    "autonomous": ["read-only-discovery", "supported-runtime-override", "idempotent-retry"],
    "requires_approval": ["dependency-installation", "network-access", "destructive-change", "scope-expansion", "plan-modification"]
  }
}
```

## Task 1: Validate CLI

**Files:**
- `scripts/plan_execution.py`

- [ ] Run `python3 scripts/plan_execution.py preflight valid-plan.md`
- [ ] Confirm exit 0.
