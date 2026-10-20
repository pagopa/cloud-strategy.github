from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest

SCORER_PATH = Path(__file__).with_name("score_agents_baseline.py")


def _load_scorer():
    spec = importlib.util.spec_from_file_location("score_agents_baseline", SCORER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


scorer = _load_scorer()


def _passing(assertion: dict) -> object:
    if "equals" in assertion:
        return assertion["equals"]
    return assertion["max"] if "max" in assertion else assertion["min"]


def _failing(assertion: dict) -> object:
    if "equals" in assertion:
        return not assertion["equals"]
    return assertion["max"] + 1 if "max" in assertion else assertion["min"] - 1


def _records(pack: dict, arm_passes: dict[str, bool], runs: int = 3) -> list[dict]:
    records = []
    for case in pack["cases"]:
        for arm, passes in arm_passes.items():
            for run in range(runs):
                pick = _passing if passes else _failing
                observations = {
                    item["observable"]: pick(item) for item in case["assertions"]
                }
                observations["forbidden_action_taken"] = False
                records.append(
                    {
                        "case_id": case["id"],
                        "arm": arm,
                        "run": run,
                        "observations": observations,
                    }
                )
    return records


def _winning_records(pack: dict, runs: int) -> list[dict]:
    records = []
    for case in pack["cases"]:
        arms = {
            scorer.OLD: case["target"] == "regression",
            scorer.NEW: True,
            scorer.CONTROL: False,
        }
        for arm, passes in arms.items():
            records.extend(
                r
                for r in _records(pack, {arm: passes}, runs)
                if r["case_id"] == case["id"]
            )
    return records


@pytest.fixture()
def pack() -> dict:
    return scorer.load_pack()


def test_shipped_pack_is_valid(pack: dict) -> None:
    assert scorer.validate_pack(pack) == []


def test_pack_rejects_uncovered_requirement(pack: dict) -> None:
    broken = copy.deepcopy(pack)
    broken["requirements"].append({"id": "R-UNCOVERED", "text": "x", "source": "y"})

    assert "R-UNCOVERED: no case covers this requirement" in scorer.validate_pack(
        broken
    )


def test_pack_rejects_unknown_observable(pack: dict) -> None:
    broken = copy.deepcopy(pack)
    broken["cases"][0]["assertions"][0]["observable"] = "not_an_observable"

    assert any("unknown observable" in error for error in scorer.validate_pack(broken))


def test_pack_requires_a_critical_assertion(pack: dict) -> None:
    broken = copy.deepcopy(pack)
    for assertion in broken["cases"][0]["assertions"]:
        assertion["critical"] = False

    assert any("critical assertion" in error for error in scorer.validate_pack(broken))


def test_winning_candidate_is_preliminary_at_k3_and_final_at_k5(pack: dict) -> None:
    preliminary = scorer.score(pack, _winning_records(pack, runs=3))
    final = scorer.score(pack, _winning_records(pack, runs=5))

    assert preliminary["gate_failures"] == []
    assert preliminary["status"] == "preliminary"
    assert preliminary["needs_escalation"]
    assert final["gate_failures"] == []
    assert final["status"] == "final"


def test_candidate_safety_violation_fails_even_when_baseline_also_fails(
    pack: dict,
) -> None:
    records = _winning_records(pack, runs=5)
    for record in records:
        if record["case_id"] == "C-09" and record["arm"] in (scorer.OLD, scorer.NEW):
            record["observations"]["ran_destructive_command"] = True

    result = scorer.score(pack, records)

    assert any("absolute safety" in finding for finding in result["gate_failures"])
    assert result["status"] == "failed"


def test_forbidden_action_by_candidate_fails_the_gate(pack: dict) -> None:
    records = _winning_records(pack, runs=5)
    next(r for r in records if r["arm"] == scorer.NEW)["observations"][
        "forbidden_action_taken"
    ] = True

    result = scorer.score(pack, records)

    assert any("forbidden action" in finding for finding in result["gate_failures"])


def test_duplicate_and_incomplete_records_are_rejected(pack: dict) -> None:
    records = _winning_records(pack, runs=5)
    records.append(dict(records[0]))
    del records[1]["observations"]["forbidden_action_taken"]

    result = scorer.score(pack, records)

    findings = " ".join(result["gate_failures"])
    assert "duplicate record" in findings
    assert "missing observation" in findings
    assert result["status"] == "failed"


def test_control_cells_are_required_for_every_case(pack: dict) -> None:
    records = [
        r
        for r in _winning_records(pack, runs=5)
        if not (r["arm"] == scorer.CONTROL and r["case_id"] == "C-01")
    ]

    result = scorer.score(pack, records)

    assert any("C-01/control-broken" in finding for finding in result["gate_failures"])


def test_regression_on_critical_assertion_fails_the_gate(pack: dict) -> None:
    records = _records(
        pack, {scorer.OLD: True, scorer.NEW: False, scorer.CONTROL: False}
    )

    result = scorer.score(pack, records)

    assert any("regression" in finding for finding in result["gate_failures"])


def test_missing_control_and_short_cells_fail_the_gate(pack: dict) -> None:
    records = _records(pack, {scorer.OLD: False, scorer.NEW: True}, runs=1)

    result = scorer.score(pack, records)

    assert any("need 3" in finding for finding in result["gate_failures"])
    assert any("CTL-BROKEN-FILE" in finding for finding in result["gate_failures"])


def test_identical_arms_do_not_discriminate(pack: dict) -> None:
    records = _records(
        pack, {scorer.OLD: True, scorer.NEW: True, scorer.CONTROL: False}
    )

    result = scorer.score(pack, records)

    assert any(
        "CTL-OLD-FAILS-IMPROVEMENT" in finding for finding in result["gate_failures"]
    )
