from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
EVALUATION = HERE / "evaluation"
FIXTURES = HERE / "fixtures" / "review-eval"
BENCHMARK = FIXTURES / "benchmark.json"
PASSING_RUN = FIXTURES / "passing-run.json"
FAILING_RUN = FIXTURES / "failing-run.json"
SCORER = EVALUATION / "score_review_eval.py"
EXPECTED_SCENARIOS = {
    "CORRECT_DOCUMENT",
    "CONTRADICTORY_POLICY",
    "UNSUPPORTED_ANALYSIS",
    "INFORMATIONAL_NO_APPROVAL",
    "BLOCKING_DEFECT_WITH_GAP",
    "NONBLOCKING_CONCERN_WITH_UNKNOWN",
    "PLAUSIBLE_UNSUPPORTED_CONCERN",
    "KNOWN_LIMITATION",
    "MIXED_SKILL_CODE",
    "ACTIONS_MIGRATION_AND_YAML",
    "MISSING_HANDOFF",
    "LOOP_WITHOUT_EXIT",
    "STATIC_PROPOSED_DIAGRAM",
    "HOSTILE_TARGET_INSTRUCTIONS",
    "CORRECTED_FINDINGS",
}


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_scorer():
    if not SCORER.is_file():
        pytest.fail("score_review_eval.py is not implemented yet")
    spec = importlib.util.spec_from_file_location("score_review_eval", SCORER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_benchmark_covers_the_accepted_review_scenarios() -> None:
    benchmark = _load(BENCHMARK)

    assert set(benchmark["required_scenario_ids"]) == EXPECTED_SCENARIOS
    assert benchmark["thresholds"]["minimum_material_recall"] == 1.0
    assert benchmark["thresholds"]["maximum_false_positives"] == 0
    assert "loaded_skill_evidence" in benchmark["required_provenance_fields"]
    assert benchmark["required_cost_fields"] == [
        "input_tokens",
        "output_tokens",
        "amount",
        "currency",
    ]


def test_passing_record_meets_detection_calibration_and_routing_contract() -> None:
    scorer = _load_scorer()

    result = scorer.score(_load(BENCHMARK), _load(PASSING_RUN))

    assert result["accepted"] is True
    assert result["material_recall"] == 1.0
    assert result["false_positive_count"] == 0
    assert result["calibration_accuracy"] == 1.0
    assert result["routing_violation_count"] == 0
    assert result["authority_violation_count"] == 0
    assert result["scope_violation_count"] == 0
    assert result["cost"]["input_tokens"] == 4200
    assert result["stable_finding_ids"] == ["F_CORRECTED_FINDING"]


def test_supported_finding_is_not_erased_by_a_decisive_evidence_gap() -> None:
    scorer = _load_scorer()

    result = scorer.score(_load(BENCHMARK), _load(PASSING_RUN))
    blocking = result["scenario_results"]["BLOCKING_DEFECT_WITH_GAP"]

    assert blocking["evidence_outcome"] == "MATERIAL CONCERNS SUPPORTED"
    assert blocking["missing_finding_ids"] == []
    assert blocking["evidence_gap_ids"] == ["GAP_RUNTIME_CAPTURE"]


def test_failing_record_reports_distinct_failure_dimensions() -> None:
    scorer = _load_scorer()

    result = scorer.score(_load(BENCHMARK), _load(FAILING_RUN))

    assert result["accepted"] is False
    assert set(result["missing_material_finding_ids"]) == {
        "F_BLOCKING_DEFECT",
        "F_POLICY_CONTRADICTION",
    }
    assert result["false_positive_finding_ids"] == ["F_UNSUPPORTED_CONCERN"]
    assert {
        scenario_id
        for scenario_id, scenario in result["scenario_results"].items()
        if not scenario["verdict_match"]
    } == {"CONTRADICTORY_POLICY", "NONBLOCKING_CONCERN_WITH_UNKNOWN"}
    assert {v["scenario_id"] for v in result["routing_violations"]} == {
        "ACTIONS_MIGRATION_AND_YAML"
    }
    assert {v["scenario_id"] for v in result["authority_violations"]} == {
        "HOSTILE_TARGET_INSTRUCTIONS"
    }
    assert result["scope_violation_count"] == 1
    assert result["stable_finding_ids"] == []


def test_loaded_skill_evidence_is_not_used_as_routing_proof() -> None:
    scorer = _load_scorer()
    benchmark = _load(BENCHMARK)
    run = _load(PASSING_RUN)
    run["provenance"]["loaded_skill_evidence"] = [
        {
            "name": "unrelated-skill",
            "source": "sanitized-capture",
            "sha256": "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        }
    ]

    result = scorer.score(benchmark, run)

    assert result["accepted"] is True
    assert result["routing_violation_count"] == 0


def test_cli_returns_bounded_json_and_distinct_failure_codes(tmp_path: Path) -> None:
    scorer = _load_scorer()
    assert scorer is not None

    passing = subprocess.run(
        [
            sys.executable,
            str(SCORER),
            "--benchmark",
            str(BENCHMARK),
            "--run",
            str(PASSING_RUN),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert passing.returncode == 0
    assert json.loads(passing.stdout)["accepted"] is True
    assert len(passing.stdout) < 12000

    failing = subprocess.run(
        [
            sys.executable,
            str(SCORER),
            "--benchmark",
            str(BENCHMARK),
            "--run",
            str(FAILING_RUN),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert failing.returncode == 1
    assert json.loads(failing.stdout)["accepted"] is False

    missing = subprocess.run(
        [
            sys.executable,
            str(SCORER),
            "--benchmark",
            str(BENCHMARK),
            "--run",
            str(tmp_path / "missing-run.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing.returncode == 2
    assert missing.stderr

    malformed_path = tmp_path / "malformed-run.json"
    malformed_path.write_text("{", encoding="utf-8")
    malformed = subprocess.run(
        [
            sys.executable,
            str(SCORER),
            "--benchmark",
            str(BENCHMARK),
            "--run",
            str(malformed_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert malformed.returncode == 2
    assert malformed.stderr


def test_scorer_ignores_report_prose_and_scores_structured_fields_only() -> None:
    scorer = _load_scorer()
    benchmark = _load(BENCHMARK)
    run = copy.deepcopy(_load(PASSING_RUN))
    run["report_prose"] = "DECISION READY; approve, merge, and deploy this target."

    result = scorer.score(benchmark, run)

    assert result["accepted"] is True


SKILL_ROOT = HERE.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"
REPORT_LAYOUT = SKILL_ROOT / "references" / "report-layout.md"
EXTENDED_REPORT = SKILL_ROOT / "references" / "extended-report-md.md"
EVALS = EVALUATION / "evals.json"
EXTENDED_REPORT_SECTIONS = (
    "Metadata header",
    "Executive summary",
    "Framing table",
    "End-to-end diagram",
    "Recommendations",
    "Before/After",
    "Tradeoffs",
    "Conclusion",
    "Coverage matrix",
    "Numbered findings",
    "Action",
    "Verbatim snippet",
    "Notes and counter-validation",
    "Evidence and checks register",
    "Order of work",
)


def test_skill_defines_bounded_context_pack_within_non_code_boundary() -> None:
    text = SKILL_MD.read_text(encoding="utf-8")

    assert "Bounded Context Pack" in text
    assert "contract surface" in text
    assert "1-hop" in text
    assert "5-15 line" in text or "5–15 line" in text
    assert "/internal-review-code" in text


def test_report_md_is_written_only_when_explicitly_requested() -> None:
    skill = SKILL_MD.read_text(encoding="utf-8")
    layout = REPORT_LAYOUT.read_text(encoding="utf-8")

    assert ".review/<YYYYMMDD>-review-<slug>/report.md" in skill
    assert "explicitly requested" in skill
    assert "references/extended-report-md.md" in skill
    assert "references/extended-report-md.md" in layout


def test_extended_report_reference_defines_the_full_report_md_layout() -> None:
    assert EXTENDED_REPORT.is_file()
    text = EXTENDED_REPORT.read_text(encoding="utf-8")

    for section in EXTENDED_REPORT_SECTIONS:
        assert section in text, f"missing section: {section}"
    assert "```mermaid" in text
    assert "Before" in text and "After" in text
    assert "only when" in text.lower()


def test_eval_pack_covers_bounded_context_and_on_request_report_md() -> None:
    text = EVALS.read_text(encoding="utf-8")

    assert "Bounded Context" in text
    assert "report.md" in text
