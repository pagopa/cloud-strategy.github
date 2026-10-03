from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[1]
SCRIPT = BUNDLE / "scripts" / "check_posture_record.py"
FIXTURES = BUNDLE / "tests" / "evaluation" / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _run(tmp_path: Path, record: dict) -> tuple[int, list[str]]:
    target = tmp_path / "record.json"
    target.write_text(json.dumps(record), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(proc.stdout)
    return proc.returncode, [finding["code"] for finding in payload["findings"]]


def test_valid_fixture_passes(tmp_path: Path) -> None:
    code, findings = _run(tmp_path, _load("posture-record-valid.json"))
    assert (code, findings) == (0, [])


def test_defective_fixture_fails_for_missing_red_and_unobserved_broader(
    tmp_path: Path,
) -> None:
    code, findings = _run(tmp_path, _load("posture-record-defective.json"))
    assert code == 1
    assert "missing-proof-check" in findings
    assert "unobserved-check" in findings


def test_field_order_is_enforced(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    reordered = {key: record[key] for key in ("state", "posture", "boundary", "checks", "gaps")}
    _, findings = _run(tmp_path, reordered)
    assert "field-order" in findings


def test_state_must_match_posture(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["state"] = "feature-first-validated"
    _, findings = _run(tmp_path, record)
    assert "state-posture-mismatch" in findings


def test_refactor_accepts_passing_characterization(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["posture"]["change"] = "refactor"
    record["checks"][0] = {
        "phase": "characterization",
        "command": "python3 -m pytest -q tests/test_report_output.py",
        "result": "passed",
    }
    code, findings = _run(tmp_path, record)
    assert (code, findings) == (0, [])


def test_behavior_change_rejects_characterization_instead_of_red(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["checks"][0] = {
        "phase": "characterization",
        "command": "python3 -m pytest -q tools/sync/tests/test_cli.py",
        "result": "passed",
    }
    _, findings = _run(tmp_path, record)
    assert "proof-kind" in findings


def test_mandatory_record_requires_change_kind(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    del record["posture"]["change"]
    _, findings = _run(tmp_path, record)
    assert "missing-change-kind" in findings


@pytest.mark.parametrize(
    "result",
    ["errored: collection failed", "failed: ModuleNotFoundError: No module named 'sync'"],
)
def test_red_from_an_error_is_not_proof(tmp_path: Path, result: str) -> None:
    record = _load("posture-record-valid.json")
    record["checks"][0]["result"] = result
    _, findings = _run(tmp_path, record)
    assert "proof-check-result" in findings


def test_validation_only_requires_gap_and_alternate_check(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["posture"]["value"] = "validation-only"
    record["state"] = "validation-only"
    record["checks"] = []
    _, findings = _run(tmp_path, record)
    assert "missing-gaps" in findings
    assert "missing-alternate-check" in findings


def test_blocked_requires_a_non_passing_check(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["state"] = "blocked"
    record["gaps"] = "Waiting for review."
    _, findings = _run(tmp_path, record)
    assert "blocked-without-failure" in findings


def test_blocked_accepts_out_of_scope_broader_failure(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["checks"][2]["result"] = "failed: pre-existing test_catalog failure on base"
    record["state"] = "blocked"
    record["gaps"] = "Broader suite has a pre-existing failure; rerun after the base fix."
    code, findings = _run(tmp_path, record)
    assert (code, findings) == (0, [])


def test_validated_state_accepts_recorded_pre_existing_broader_failure(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["checks"][2]["result"] = "failed: test_catalog also fails on the base commit"
    record["checks"][2]["scope"] = "pre-existing"
    record["gaps"] = "test_catalog fails on the base commit; outside the task allowlist."
    code, findings = _run(tmp_path, record)
    assert (code, findings) == (0, [])


def test_pre_existing_broader_failure_must_be_named_in_gaps(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["checks"][2]["result"] = "failed: test_catalog also fails on the base commit"
    record["checks"][2]["scope"] = "pre-existing"
    _, findings = _run(tmp_path, record)
    assert "missing-gaps" in findings


def test_pre_existing_scope_is_only_valid_for_broader_checks(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["checks"][1]["result"] = "failed: focused test fails"
    record["checks"][1]["scope"] = "pre-existing"
    record["gaps"] = "Focused failure claimed pre-existing."
    _, findings = _run(tmp_path, record)
    assert "invalid-scope" in findings


@pytest.mark.parametrize(
    ("field", "value"),
    [("state", ["blocked"]), ("gaps", 3), ("checks", {"phase": "red"}), ("posture", "feature-first")],
)
def test_wrong_field_types_are_findings_not_crashes(
    tmp_path: Path, field: str, value: object
) -> None:
    record = _load("posture-record-valid.json")
    record[field] = value
    code, findings = _run(tmp_path, record)
    assert code == 1
    assert "schema" in findings


def test_duplicate_phase_is_rejected(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["checks"].append(dict(record["checks"][0]))
    _, findings = _run(tmp_path, record)
    assert "duplicate-phase" in findings


def test_red_check_must_fail(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["checks"][0]["result"] = "passed"
    _, findings = _run(tmp_path, record)
    assert "proof-check-result" in findings


def test_proof_must_precede_focused_check(tmp_path: Path) -> None:
    record = _load("posture-record-valid.json")
    record["checks"] = [record["checks"][1], record["checks"][0], record["checks"][2]]
    _, findings = _run(tmp_path, record)
    assert "proof-order" in findings


@pytest.mark.parametrize("state", ["blocked", "prototype-unverified"])
def test_gap_states_require_named_gaps(tmp_path: Path, state: str) -> None:
    record = _load("posture-record-valid.json")
    record["posture"]["value"] = (
        "prototype-unverified" if state == "prototype-unverified" else "feature-first"
    )
    record["state"] = state
    _, findings = _run(tmp_path, record)
    assert "missing-gaps" in findings


def test_unknown_posture_is_rejected(tmp_path: Path) -> None:
    record = copy.deepcopy(_load("posture-record-valid.json"))
    record["posture"]["value"] = "test-later"
    _, findings = _run(tmp_path, record)
    assert "unknown-posture" in findings


def test_invalid_json_is_reported(tmp_path: Path) -> None:
    target = tmp_path / "record.json"
    target.write_text("{", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert json.loads(proc.stdout)["findings"][0]["code"] == "invalid-json"
