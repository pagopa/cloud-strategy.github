from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
EVALUATION_ROOT = REPO_ROOT / "tests/github/skills/internal-gateway-idea/evaluation"
MANIFEST_PATH = EVALUATION_ROOT / "benchmark.json"
SCORER_PATH = EVALUATION_ROOT / "score_idea_eval.py"
REQUIRED_RECORD_KEYS = (
    "decision_records",
    "question_records",
    "evidence_records",
    "transition_events",
    "route_events",
    "artifact_events",
    "provenance",
)
EVIDENCE_CLASSES = ("Facts", "Reports", "Assumptions", "Unknowns", "Constraints")
CASE_IDS = ("C-01", "C-02", "C-03", "C-04", "C-05")


def load_manifest() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_scorer() -> ModuleType:
    assert SCORER_PATH.is_file(), (
        "score_idea_eval.py must exist before the evaluator contract can run"
    )
    spec = importlib.util.spec_from_file_location("idea_eval_scorer", SCORER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _evidence(case_id: str, decision_ids: dict[str, list[str]]) -> list[dict[str, object]]:
    prefix = case_id.replace("-", "")
    return [
        {
            "evidence_id": f"{prefix}-facts",
            "class": "Facts",
            "strength": "sufficient",
            "event_index": 1,
            "decision_ids": decision_ids.get("Facts", []),
        },
        {
            "evidence_id": f"{prefix}-reports",
            "class": "Reports",
            "strength": "credible",
            "event_index": 1,
            "decision_ids": decision_ids.get("Reports", []),
        },
        {
            "evidence_id": f"{prefix}-assumptions",
            "class": "Assumptions",
            "strength": "declared",
            "event_index": 1,
            "decision_ids": decision_ids.get("Assumptions", []),
        },
        {
            "evidence_id": f"{prefix}-unknowns",
            "class": "Unknowns",
            "strength": "material",
            "event_index": 1,
            "decision_ids": decision_ids.get("Unknowns", []),
        },
        {
            "evidence_id": f"{prefix}-constraints",
            "class": "Constraints",
            "strength": "accepted",
            "event_index": 1,
            "decision_ids": decision_ids.get("Constraints", []),
        },
    ]


def _decision(
    decision_id: str,
    status: str,
    *,
    kind: str = "root",
    dependencies: list[str] | None = None,
    evidence_ids: list[str] | None = None,
    material: bool = True,
    reopen_condition: str = "new-evidence",
) -> dict[str, object]:
    return {
        "decision_id": decision_id,
        "decision": f"Resolve {decision_id}",
        "kind": kind,
        "status": status,
        "material": material,
        "dependencies": dependencies or [],
        "evidence_ids": evidence_ids or [],
        "reopen_condition": reopen_condition,
    }


def _question(
    question_id: str,
    decision_id: str,
    event_index: int,
    evidence_ids: list[str],
    *,
    kind: str = "decision",
    prerequisites: list[str] | None = None,
    block_id: str | None = None,
    eligible_event_index: int | None = None,
) -> dict[str, object]:
    return {
        "question_id": question_id,
        "decision_id": decision_id,
        "kind": kind,
        "event_index": event_index,
        "eligible_event_index": (
            eligible_event_index
            if eligible_event_index is not None
            else event_index
        ),
        "block_id": block_id or f"{question_id}-BLOCK",
        "evidence_ids": evidence_ids,
        "prerequisites": prerequisites or [],
    }


def _status_event(
    decision_id: str,
    from_status: str,
    to_status: str,
    event_index: int,
    *,
    trigger: str = "evidence",
    evidence_ids: list[str] | None = None,
) -> dict[str, object]:
    return {
        "event": "decision-status",
        "decision_id": decision_id,
        "from": from_status,
        "to": to_status,
        "event_index": event_index,
        "trigger": trigger,
        "evidence_ids": evidence_ids or [],
    }


def _capsule(
    case_id: str,
    event_index: int,
    *,
    subject: str | None = None,
    mode: str | None = None,
) -> dict[str, object]:
    return {
        "subject": subject or case_id,
        "mode": mode or "analysis-only",
        "decision_focus": f"Focus {case_id}",
        "accepted_ids": [f"{case_id}-ROOT"],
        "rejected_ids": [],
        "deferred_ids": [],
        "accepted_risk_ids": [],
        "eligible_now_ids": [],
        "blocked_later": [],
        "evidence_anchors": [f"{case_id}-facts"],
        "next_action": f"Continue {case_id} at event {event_index}",
    }


def _observation(
    case_id: str,
    decisions: list[dict[str, object]],
    questions: list[dict[str, object]],
    transitions: list[dict[str, object]],
    routes: list[dict[str, object]],
    artifacts: list[dict[str, object]],
    evidence_links: dict[str, list[str]],
) -> dict[str, object]:
    return {
        "observation_id": f"synthetic-{case_id}",
        "case_id": case_id,
        "kind": "synthetic-test",
        "decision_records": decisions,
        "question_records": questions,
        "evidence_records": _evidence(case_id, evidence_links),
        "transition_events": transitions,
        "route_events": [
            {
                "event": "invocation",
                "owner": "/internal-gateway-idea",
                "mode": "analysis-only",
                "event_index": 0,
                "explicit": True,
            },
            *routes,
        ],
        "artifact_events": artifacts,
        "provenance": {
            "kind": "synthetic-test",
            "source": "inline-test-records",
            "sanitized_perimeter": "internal-gateway-idea-eval-v1",
            "baseline_id": "synthetic-baseline-v1",
            "candidate_id": "synthetic-candidate-v1",
        },
    }


def passing_run() -> dict[str, object]:
    c01_fact = "C01-FACT"
    c01_unknown = "C01-UNKNOWN"
    c01_unknown_2 = "C01-UNKNOWN-2"
    c02_root = "C02-ROOT"
    c02_dependent = "C02-DEPENDENT"
    c03_root = "C03-ROOT"
    c04_root = "C04-ROOT"
    c05_root = "C05-ROOT"

    c04_transitions: list[dict[str, object]] = [
        _status_event(c04_root, "open", "accepted", 3),
    ]
    for event_index, boundary in enumerate(
        ("pause", "compaction", "subject-change", "mode-change"), start=4
    ):
        subject = "C-04-next" if boundary in {"subject-change", "mode-change"} else "C-04"
        mode = "analysis-and-artifact" if boundary == "mode-change" else "analysis-only"
        c04_transitions.append(
            {
                "event": "capsule-written",
                "boundary": boundary,
                "event_index": event_index,
                "capsule": _capsule(
                    "C-04", event_index, subject=subject, mode=mode
                ),
            }
        )

    return {
        "observations": [
            _observation(
                "C-01",
                [
                    _decision(c01_fact, "resolved-from-evidence", evidence_ids=["C01-facts"]),
                    _decision(c01_unknown, "accepted", evidence_ids=["C01-unknowns"]),
                    _decision(c01_unknown_2, "accepted", evidence_ids=["C01-unknowns"]),
                ],
                [
                    _question(
                        "C01-Q1",
                        c01_unknown,
                        3,
                        ["C01-unknowns"],
                        block_id="C01-B1",
                        eligible_event_index=2,
                    ),
                    _question(
                        "C01-Q2",
                        c01_unknown_2,
                        3,
                        ["C01-unknowns"],
                        block_id="C01-B1",
                        eligible_event_index=2,
                    ),
                ],
                [
                    _status_event(c01_fact, "open", "resolved-from-evidence", 2, evidence_ids=["C01-facts"]),
                    _status_event(c01_unknown, "open", "accepted", 4, trigger="explicit-user-change"),
                    _status_event(c01_unknown_2, "open", "accepted", 4, trigger="explicit-user-change"),
                ],
                [{"event": "route-selected", "owner": "/grill-me", "mode": "analysis-only", "event_index": 3}],
                [],
                {
                    "Facts": [c01_fact],
                    "Unknowns": [c01_unknown, c01_unknown_2],
                },
            ),
            _observation(
                "C-02",
                [
                    _decision(c02_root, "accepted", evidence_ids=["C02-unknowns"]),
                    _decision(
                        c02_dependent,
                        "resolved-from-evidence",
                        kind="dependent",
                        dependencies=[c02_root],
                        evidence_ids=["C02-facts"],
                    ),
                ],
                [_question("C02-Q1", c02_root, 2, ["C02-unknowns"])],
                [
                    _status_event(c02_dependent, "open", "blocked-later", 2),
                    _status_event(c02_root, "open", "accepted", 3, trigger="explicit-user-change"),
                    _status_event(c02_dependent, "blocked-later", "resolved-from-evidence", 4, evidence_ids=["C02-facts"]),
                ],
                [{"event": "route-selected", "owner": "/grill-me", "mode": "analysis-only", "event_index": 2}],
                [],
                {"Facts": [c02_dependent], "Unknowns": [c02_root]},
            ),
            _observation(
                "C-03",
                [
                    _decision(c03_root, "accepted", evidence_ids=["C03-reports"]),
                    _decision("C03-ALT-A", "rejected", kind="alternative", evidence_ids=["C03-reports"]),
                    _decision("C03-ALT-B", "rejected", kind="alternative", evidence_ids=["C03-constraints"]),
                ],
                [_question("C03-Q1", c03_root, 3, ["C03-reports"])],
                [
                    {
                        "event": "internal-challenge",
                        "dimension": "mechanism",
                        "changed_from": "single-owner-control",
                        "changed_to": "shared-policy-enforcement",
                        "event_index": 2,
                        "evidence_ids": ["C03-reports", "C03-constraints"],
                        "visible_alternatives": ["C03-ALT-A", "C03-ALT-B"],
                        "credible_mechanism_count": 2,
                    },
                    _status_event("C03-ALT-A", "open", "rejected", 3),
                    _status_event("C03-ALT-B", "open", "rejected", 3),
                    _status_event(c03_root, "open", "accepted", 4, trigger="explicit-user-change"),
                    {
                        "event": "decision-reopened",
                        "decision_id": c03_root,
                        "event_index": 5,
                        "trigger": "new-evidence",
                        "evidence_ids": ["C03-facts"],
                    },
                    _status_event(c03_root, "open", "accepted", 6, trigger="new-evidence", evidence_ids=["C03-facts"]),
                ],
                [{"event": "route-selected", "owner": "/grill-me", "mode": "analysis-only", "event_index": 3}],
                [],
                {"Facts": [c03_root], "Reports": [c03_root, "C03-ALT-A"], "Constraints": ["C03-ALT-B"]},
            ),
            _observation(
                "C-04",
                [_decision(c04_root, "accepted", evidence_ids=["C04-unknowns"])],
                [_question("C04-Q1", c04_root, 2, ["C04-unknowns"])],
                c04_transitions,
                [
                    {"event": "route-selected", "owner": "/grill-me", "mode": "analysis-only", "subject": "C-04", "event_index": 2},
                    {"event": "subject-change", "owner": "internal-gateway-idea", "mode": "analysis-only", "subject": "C-04-next", "event_index": 6},
                    {"event": "mode-change", "owner": "internal-gateway-idea", "mode": "analysis-and-artifact", "subject": "C-04-next", "event_index": 7},
                ],
                [],
                {"Unknowns": [c04_root]},
            ),
            _observation(
                "C-05",
                [_decision(c05_root, "accepted", evidence_ids=["C05-unknowns"])],
                [_question("C05-Q1", c05_root, 2, ["C05-unknowns"])],
                [_status_event(c05_root, "open", "accepted", 3, trigger="explicit-user-change")],
                [{"event": "route-selected", "owner": "/grill-me", "mode": "analysis-only", "event_index": 2}],
                [
                    {"event": "candidate-presented", "event_index": 4, "artifact_id": "C05-analysis"},
                    {"event": "candidate-accepted", "event_index": 5, "explicit": True, "artifact_id": "C05-analysis"},
                    {"event": "critical-choice", "event_index": 6, "choice": "integrate", "explicit": True},
                    {"event": "critical-findings-integrated", "event_index": 7, "artifact_id": "C05-analysis"},
                    {"event": "artifact-saved", "event_index": 8, "artifact_id": "C05-analysis", "path": "tmp/superpowers/specs/c05-analysis.md"},
                    {"event": "planning-replay", "event_index": 9, "artifact_id": "C05-analysis", "uses_transcript": False},
                ],
                {"Unknowns": [c05_root]},
            ),
        ]
    }


def failing_run() -> dict[str, object]:
    run = copy.deepcopy(passing_run())
    observations = run["observations"]
    assert isinstance(observations, list)

    c01 = observations[0]
    c01["question_records"][1]["block_id"] = "C01-B2"
    c01["question_records"].append(
        _question("C01-Q-FACT", "C01-FACT", 5, ["C01-facts"], kind="fact")
    )
    c01["question_eligibility_complete"] = True

    c02 = observations[1]
    c02["question_records"].append(
        _question(
            "C02-Q-DEPENDENT",
            "C02-DEPENDENT",
            2,
            ["C02-unknowns"],
            prerequisites=["C02-ROOT"],
        )
    )

    c03 = observations[2]
    c03["transition_events"] = [
        event
        for event in c03["transition_events"]
        if event.get("event") != "internal-challenge"
    ]
    for event in c03["transition_events"]:
        if event.get("event") == "decision-reopened":
            event["trigger"] = "unsupported-claim"
            event["evidence_ids"] = []

    c04 = observations[3]
    c04["transition_events"] = [
        event
        for event in c04["transition_events"]
        if event.get("boundary") != "compaction"
    ]
    c04["route_events"].append(
        {
            "event": "route-selected",
            "owner": "/internal-tdd",
            "mode": "analysis-only",
            "subject": "C-04-next",
            "event_index": 8,
        }
    )

    c05 = observations[4]
    c05["artifact_events"] = [
        event
        for event in c05["artifact_events"]
        if event.get("event") != "critical-choice"
    ]
    c05["artifact_events"].append(
        {
            "event": "artifact-saved",
            "event_index": 10,
            "artifact_id": "C05-analysis-second",
            "path": "tmp/superpowers/specs/c05-analysis-second.md",
        }
    )
    for event in c05["artifact_events"]:
        if event.get("event") == "planning-replay":
            event["uses_transcript"] = True

    return run


def test_manifest_declares_cases_records_limits_and_forbidden_verdicts() -> None:
    manifest = load_manifest()

    assert manifest["contract_version"] == "internal-gateway-idea-eval-v1"
    assert manifest["required_case_ids"] == list(CASE_IDS)
    assert set(manifest["required_record_keys"]) == set(REQUIRED_RECORD_KEYS)
    assert set(manifest["forbidden_verdict_fields"]) == {
        "question_eligibility_complete",
        "critical_integrated",
        "runtime_evidence",
    }
    protected = manifest["protected_workflow"]
    assert protected["required_evidence_classes"] == list(EVIDENCE_CLASSES)
    assert protected["max_recoverable_fact_questions"] == 0
    assert protected["max_premature_dependent_questions"] == 0
    assert protected["max_unjustified_reopens"] == 0
    assert protected["max_split_known_question_batches"] == 0
    assert protected["max_saved_artifacts"] == 1
    assert protected["forbid_fixed_question_cap"] is True
    assert protected["forbid_automatic_critical_realign"] is True


def test_passing_records_are_accepted_without_claiming_runtime_evidence() -> None:
    scorer = load_scorer()
    result = scorer.score(load_manifest(), passing_run())

    assert result["accepted"] is True
    assert result["missing_case_ids"] == []
    assert result["findings"] == []
    assert result["behavioral_evidence"]["status"] == "unavailable"
    assert result["behavioral_evidence"]["case_ids"] == list(CASE_IDS)


def test_failing_records_report_derived_findings_and_reject() -> None:
    scorer = load_scorer()
    result = scorer.score(load_manifest(), failing_run())

    assert result["accepted"] is False
    assert result["missing_case_ids"] == []
    assert result["recoverable_fact_question_cases"] == ["C-01"]
    assert result["split_known_question_batch_cases"] == ["C-01"]
    assert result["premature_dependent_question_cases"] == ["C-02"]
    assert result["unjustified_reopen_cases"] == ["C-03"]
    assert result["anchored_challenge_violation_cases"] == ["C-03"]
    assert result["state_continuity_violation_cases"] == ["C-04"]
    assert result["analysis_only_routing_violation_cases"] == ["C-04"]
    assert result["artifact_replay_violation_cases"] == ["C-05"]
    assert result["self_attested_verdict_cases"] == ["C-01"]

    for key, value in result.items():
        if key.endswith("_cases"):
            assert value == sorted(value)


def test_malformed_run_is_rejected_as_input_error() -> None:
    scorer = load_scorer()

    with pytest.raises(ValueError):
        scorer.score(load_manifest(), {"observations": [{"case_id": "C-01"}]})

    future_eligibility = passing_run()
    future_eligibility["observations"][0]["question_records"][0][
        "eligible_event_index"
    ] = 4
    with pytest.raises(ValueError, match="eligible after it was asked"):
        scorer.score(load_manifest(), future_eligibility)


def _run_cli(tmp_path: Path, manifest: object, run: object) -> subprocess.CompletedProcess[str]:
    manifest_file = tmp_path / "manifest.json"
    run_file = tmp_path / "run.json"
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
    run_file.write_text(json.dumps(run), encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            str(SCORER_PATH),
            "--manifest",
            str(manifest_file),
            "--run",
            str(run_file),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_uses_exit_zero_one_and_two_for_accept_reject_and_malformed(
    tmp_path: Path,
) -> None:
    load_scorer()

    accepted = _run_cli(tmp_path, load_manifest(), passing_run())
    assert accepted.returncode == 0
    assert json.loads(accepted.stdout)["accepted"] is True

    rejected = _run_cli(tmp_path, load_manifest(), failing_run())
    assert rejected.returncode == 1
    assert json.loads(rejected.stdout)["accepted"] is False

    malformed_manifest = tmp_path / "malformed-manifest.json"
    malformed_run = tmp_path / "malformed-run.json"
    malformed_manifest.write_text("{", encoding="utf-8")
    malformed_run.write_text("{}", encoding="utf-8")
    malformed = subprocess.run(
        [
            sys.executable,
            str(SCORER_PATH),
            "--manifest",
            str(malformed_manifest),
            "--run",
            str(malformed_run),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert malformed.returncode == 2
    assert malformed.stderr.startswith("error: ")
