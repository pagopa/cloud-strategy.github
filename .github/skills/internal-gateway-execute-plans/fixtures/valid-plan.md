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

- Preserve fixture integrity.

## Task 1: Validate CLI

**Files:**
- `scripts/plan_execution.py`

- [ ] Run `python3 scripts/plan_execution.py preflight valid-plan.md`
- [ ] Confirm exit 0.
