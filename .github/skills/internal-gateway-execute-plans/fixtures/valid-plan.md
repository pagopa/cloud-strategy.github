## Goal

Validate the plan execution CLI against a realistic plan shape.

## Repository Preflight

- **Target:** test fixture validation.
- **Anti-scope:** no runtime changes.
- **Validation Path:** `pytest -q tests/fixture/`
- **Stop Conditions:** fixture is incomplete.

## Global Constraints

- Preserve fixture integrity.

## Task 1: Validate CLI

**Files:**
- `scripts/plan_execution.py`

- [ ] Run `python3 scripts/plan_execution.py preflight valid-plan.md`
- [ ] Confirm exit 0.
