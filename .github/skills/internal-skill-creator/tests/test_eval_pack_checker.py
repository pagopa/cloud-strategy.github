import importlib.util
import json
import subprocess
import sys
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = BUNDLE_ROOT / "fixtures" / "eval-packs"
CHECKER_PATH = BUNDLE_ROOT / "scripts" / "check_eval_pack.py"
SPEC = importlib.util.spec_from_file_location("check_eval_pack", CHECKER_PATH)
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


def _codes(findings):
    return sorted(finding["code"] for finding in findings)


def _write_pack(tmp_path, entry):
    if "raw_text" in entry:
        contents = entry["raw_text"]
    else:
        contents = json.dumps(entry["pack"])
    path = tmp_path / f"{entry['name']}.json"
    path.write_text(contents, encoding="utf-8")
    return path


def test_valid_pack_and_run_record_have_no_findings():
    pack_path = FIXTURES / "valid-pack.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))

    assert CHECKER.check_pack(pack_path, BUNDLE_ROOT, "fixture-skill") == []
    assert CHECKER.check_run_record(
        FIXTURES / "valid-run-record.json", BUNDLE_ROOT, pack
    ) == []


def test_each_defective_fixture_returns_its_declared_codes(tmp_path):
    cases = json.loads((FIXTURES / "defective-packs.json").read_text(encoding="utf-8"))
    valid_pack = json.loads((FIXTURES / "valid-pack.json").read_text(encoding="utf-8"))

    for entry in cases:
        if "record" in entry:
            record_path = tmp_path / f"{entry['name']}.json"
            record_path.write_text(json.dumps(entry["record"]), encoding="utf-8")
            findings = CHECKER.check_run_record(record_path, BUNDLE_ROOT, valid_pack)
        else:
            pack_path = _write_pack(tmp_path, entry)
            findings = CHECKER.check_pack(pack_path, BUNDLE_ROOT, "fixture-skill")
        assert _codes(findings) == sorted(entry["expected_codes"]), entry["name"]


def test_cli_returns_compact_failure_and_success_statuses(tmp_path):
    valid = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            str(FIXTURES / "valid-pack.json"),
            "--bundle-root",
            str(BUNDLE_ROOT),
            "--skill-name",
            "fixture-skill",
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert valid.returncode == 0
    assert json.loads(valid.stdout)["status"] == "ok"

    bad_pack = _write_pack(
        tmp_path,
        {"name": "bad", "pack": {"schema": "wrong"}},
    )
    invalid = subprocess.run(
        [
            sys.executable,
            str(CHECKER_PATH),
            str(bad_pack),
            "--bundle-root",
            str(BUNDLE_ROOT),
            "--skill-name",
            "fixture-skill",
            "--format",
            "compact",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid.returncode == 1
    assert json.loads(invalid.stdout)["status"] == "failed"


def test_creator_pack_is_valid_and_covers_all_case_families():
    pack_path = BUNDLE_ROOT / "tests/evaluation/evals.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    assert CHECKER.check_pack(pack_path, BUNDLE_ROOT, "internal-skill-creator") == []

    families = {case["family"] for case in pack["cases"]}
    assert {
        "new-skill",
        "material-ambiguity",
        "bounded-revision",
        "rule-relocation",
        "replacement",
        "retirement",
        "competing-owner",
        "untrusted-inspected-instructions",
        "missing-dependency",
        "held-out-downstream",
        "self-eval",
        "delegation",
        "regression",
    } <= families


def test_delegation_cases_preserve_the_six_expected_decisions():
    pack = json.loads(
        (BUNDLE_ROOT / "tests/evaluation/evals.json").read_text(encoding="utf-8")
    )
    decisions = {
        case["id"]: case["expected_output"]
        for case in pack["cases"]
        if case["id"].startswith("C-DELEGATION-")
    }
    assert decisions == {
        "C-DELEGATION-READ": "Delegate with mode read.",
        "C-DELEGATION-PLAN": "Delegate with mode plan.",
        "C-DELEGATION-WRITE": "Delegate with mode write.",
        "C-DELEGATION-LOCAL": "Complete the work locally without invoking a worker.",
        "C-DELEGATION-DECISION": "Keep the decision with the parent or stop for the missing decision.",
        "C-DELEGATION-AGENT": "Route to /internal-agent-creator.",
    }


def test_self_eval_covers_four_creator_behaviors():
    pack = json.loads(
        (BUNDLE_ROOT / "tests/evaluation/evals.json").read_text(encoding="utf-8")
    )
    self_eval = {
        case["id"]
        for case in pack["cases"]
        if case["family"] == "self-eval"
    }
    assert {
        "C-SELF-SUITES",
        "C-SELF-REGRESSION",
        "C-SELF-PRESERVE",
        "C-SELF-CRITERIA",
    } <= self_eval


def test_held_out_downstream_case_is_declared():
    pack = json.loads(
        (BUNDLE_ROOT / "tests/evaluation/evals.json").read_text(encoding="utf-8")
    )
    assert any(
        case["family"] == "held-out-downstream" and case["held_out"]
        for case in pack["cases"]
    )


def test_generated_pack_fixtures_match_their_declared_verdicts(tmp_path):
    valid_output = BUNDLE_ROOT / "tests/evaluation/fixtures/generated-pack-output.json"
    assert CHECKER.check_pack(valid_output, BUNDLE_ROOT, "fixture-skill") == []

    defective_path = BUNDLE_ROOT / "tests/evaluation/fixtures/generated-pack-defective.json"
    defective = json.loads(defective_path.read_text(encoding="utf-8"))
    pack_path = tmp_path / "generated-pack-defective.json"
    pack_path.write_text(json.dumps(defective["pack"]), encoding="utf-8")
    assert _codes(CHECKER.check_pack(pack_path, BUNDLE_ROOT, "fixture-skill")) == sorted(
        defective["expected_codes"]
    )
