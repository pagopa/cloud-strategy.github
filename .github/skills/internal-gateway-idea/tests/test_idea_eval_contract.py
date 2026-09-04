from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
EVALUATION_ROOT = REPO_ROOT / ".github/skills/internal-gateway-idea/tests/evaluation"
MANIFEST_PATH = EVALUATION_ROOT / "benchmark.json"
SCORER_PATH = EVALUATION_ROOT / "score_idea_eval.py"
PUBLIC_WRAPPER_PATH = (
    REPO_ROOT / ".github/skills/internal-gateway-idea/agents/openai.yaml"
)
REQUIRED_RECORD_KEYS = (
    "decision_records",
    "question_records",
    "evidence_records",
    "transition_events",
    "route_events",
    "artifact_events",
    "authority_events",
    "communication_records",
    "recovery_records",
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


def _evidence(
    case_id: str, decision_ids: dict[str, list[str]]
) -> list[dict[str, object]]:
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
            eligible_event_index if eligible_event_index is not None else event_index
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


def _candidate_menu(
    event_index: float,
    *,
    phase: str,
    findings_present: bool,
    critical_review_complete: bool,
    dispositions_complete: bool,
) -> dict[str, object]:
    options = [
        "continue",
        "critical-review",
        "realign",
        "+spec",
        "+plan",
        "save",
        "close",
    ]
    locks = {
        "continue": {"locked": False, "reason": "continue analysis"},
        "critical-review": {"locked": False, "reason": "review remains available"},
        "realign": {
            "locked": not findings_present,
            "reason": "no findings exist"
            if not findings_present
            else "findings are available",
        },
        "+spec": {
            "locked": not critical_review_complete,
            "reason": "critical review is pending"
            if not critical_review_complete
            else "review complete",
        },
        "+plan": {
            "locked": not critical_review_complete,
            "reason": "critical review is pending"
            if not critical_review_complete
            else "review complete",
        },
        "save": {"locked": False, "reason": "save is a provisional checkpoint"},
        "close": {
            "locked": not critical_review_complete,
            "reason": "critical review is pending"
            if not critical_review_complete
            else "close is available",
        },
    }
    return {
        "event": "candidate-menu",
        "event_index": event_index,
        "options": options,
        "locks": locks,
        "findings_present": findings_present,
        "phase": phase,
        "critical_review_complete": critical_review_complete,
        "dispositions_complete": dispositions_complete,
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


def _recovery_record(
    case_id: str,
    decisions: list[dict[str, object]],
    evidence_records: list[dict[str, object]],
    authority_events: list[dict[str, object]],
    communication_records: list[dict[str, object]],
    *,
    subject: str | None = None,
    mode: str = "analysis-only",
) -> dict[str, object]:
    terminal_states = {
        "deferred",
        "resolved-from-evidence",
        "accepted",
        "accepted-risk",
        "rejected",
    }
    terminal_ids = [
        str(decision["decision_id"])
        for decision in decisions
        if decision["status"] in terminal_states
    ]
    blocked_later = [
        {
            "decision_id": str(decision["decision_id"]),
            "prerequisites": list(decision["dependencies"]),
        }
        for decision in decisions
        if decision["status"] == "blocked-later"
    ]
    snapshot = next(
        event
        for event in authority_events
        if event.get("event") == "authority-snapshot"
    )
    evidence_anchors = sorted({str(item["evidence_id"]) for item in evidence_records})
    return {
        "record_id": f"{case_id}-recovery",
        "event_index": 99,
        "unit_lock": {
            "subject": subject or case_id,
            "mode": mode,
            "decision_focus": f"Focus {case_id}",
            "desired_artifact": "none",
            "implementation_permission": False,
        },
        "state_capsule": {
            "subject": subject or case_id,
            "mode": mode,
            "decision_focus": f"Focus {case_id}",
            "terminal_decision_ids": terminal_ids,
            "eligible_now_ids": [
                str(decision["decision_id"])
                for decision in decisions
                if decision["status"] == "eligible-now"
            ],
            "blocked_later": blocked_later,
            "evidence_anchors": evidence_anchors,
            "next_action": f"Continue {case_id}",
        },
        "decision_ledger": [
            {
                "decision_id": str(decision["decision_id"]),
                "state": str(decision["status"]),
                "basis": str(decision["decision"]),
                "reopen_condition": str(decision["reopen_condition"]),
                "dependencies": list(decision["dependencies"]),
            }
            for decision in decisions
        ],
        "authority_envelope": {
            "authorized_paths": list(snapshot["authorized_paths"]),
            "authorized_actions": list(snapshot["authorized_actions"]),
            "continuation_boundaries": [
                "continue",
                "finish",
                "pause",
                "context-recovery",
            ],
        },
        "communication_projection": copy.deepcopy(communication_records[0]),
    }


def _observation(
    case_id: str,
    decisions: list[dict[str, object]],
    questions: list[dict[str, object]],
    transitions: list[dict[str, object]],
    routes: list[dict[str, object]],
    artifacts: list[dict[str, object]],
    evidence_links: dict[str, list[str]],
    *,
    authority_events: list[dict[str, object]] | None = None,
    communication_records: list[dict[str, object]] | None = None,
    recovery_subject: str | None = None,
    recovery_mode: str = "analysis-only",
) -> dict[str, object]:
    evidence_records = _evidence(case_id, evidence_links)
    effective_authority_events = authority_events or [
        {
            "event": "authority-snapshot",
            "event_index": 1,
            "authorized_paths": ["tmp/superpowers/specs/analysis.md"],
            "authorized_actions": ["save-analysis"],
            "boundary": "analysis-unit",
        },
        {
            "event": "continuation",
            "event_index": 2,
            "boundary": "continue",
            "authorized_paths": ["tmp/superpowers/specs/analysis.md"],
            "authorized_actions": ["save-analysis"],
        },
        {
            "event": "protected-status",
            "event_index": 3,
            "status": "protected",
            "user_authority": "separate",
            "authorizes_mutation": False,
        },
        {
            "event": "scope-delta",
            "event_index": 4,
            "path": "tmp/other/analysis.md",
            "action": "write",
            "outcome": "authority-or-scope",
            "accepted": False,
        },
    ]
    effective_communication_records = communication_records or [
        {
            "view_id": f"{case_id}-candidate",
            "kind": "candidate",
            "event_index": 4,
            "material_delta_ids": [f"{case_id}-ROOT"],
            "outcome": "decision-ready",
            "controlling_evidence_ids": [f"{case_id}-facts"],
            "principal_risk_id": f"{case_id}-RISK",
            "active_choice": f"choice-{case_id}",
            "blocker_ids": [],
            "unknown_ids": [f"{case_id}-UNKNOWN"],
            "acceptance_condition_ids": [f"{case_id}-ACCEPT"],
            "word_count": 42,
            "word_count_mode": "diagnostic",
            "diagrams": [],
        }
    ]
    return {
        "observation_id": f"synthetic-{case_id}",
        "case_id": case_id,
        "kind": "synthetic-test",
        "decision_records": decisions,
        "question_records": questions,
        "evidence_records": evidence_records,
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
        "authority_events": effective_authority_events,
        "communication_records": effective_communication_records,
        "recovery_records": [
            _recovery_record(
                case_id,
                decisions,
                evidence_records,
                effective_authority_events,
                effective_communication_records,
                subject=recovery_subject,
                mode=recovery_mode,
            )
        ],
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
        subject = (
            "C-04-next" if boundary in {"subject-change", "mode-change"} else "C-04"
        )
        mode = "analysis-and-artifact" if boundary == "mode-change" else "analysis-only"
        c04_transitions.append(
            {
                "event": "capsule-written",
                "boundary": boundary,
                "event_index": event_index,
                "capsule": _capsule("C-04", event_index, subject=subject, mode=mode),
            }
        )

    return {
        "observations": [
            _observation(
                "C-01",
                [
                    _decision(
                        c01_fact, "resolved-from-evidence", evidence_ids=["C01-facts"]
                    ),
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
                    _status_event(
                        c01_fact,
                        "open",
                        "resolved-from-evidence",
                        2,
                        evidence_ids=["C01-facts"],
                    ),
                    _status_event(
                        c01_unknown,
                        "open",
                        "accepted",
                        4,
                        trigger="explicit-user-change",
                    ),
                    _status_event(
                        c01_unknown_2,
                        "open",
                        "accepted",
                        4,
                        trigger="explicit-user-change",
                    ),
                ],
                [
                    {
                        "event": "route-selected",
                        "owner": "/grill-me",
                        "mode": "analysis-only",
                        "event_index": 3,
                    }
                ],
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
                    _status_event(
                        c02_root, "open", "accepted", 3, trigger="explicit-user-change"
                    ),
                    _status_event(
                        c02_dependent,
                        "blocked-later",
                        "resolved-from-evidence",
                        4,
                        evidence_ids=["C02-facts"],
                    ),
                ],
                [
                    {
                        "event": "route-selected",
                        "owner": "/grill-me",
                        "mode": "analysis-only",
                        "event_index": 2,
                    }
                ],
                [],
                {"Facts": [c02_dependent], "Unknowns": [c02_root]},
            ),
            _observation(
                "C-03",
                [
                    _decision(c03_root, "accepted", evidence_ids=["C03-reports"]),
                    _decision(
                        "C03-ALT-A",
                        "rejected",
                        kind="alternative",
                        evidence_ids=["C03-reports"],
                    ),
                    _decision(
                        "C03-ALT-B",
                        "rejected",
                        kind="alternative",
                        evidence_ids=["C03-constraints"],
                    ),
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
                    _status_event(
                        c03_root, "open", "accepted", 4, trigger="explicit-user-change"
                    ),
                    {
                        "event": "decision-reopened",
                        "decision_id": c03_root,
                        "event_index": 5,
                        "trigger": "new-evidence",
                        "evidence_ids": ["C03-facts"],
                    },
                    _status_event(
                        c03_root,
                        "open",
                        "accepted",
                        6,
                        trigger="new-evidence",
                        evidence_ids=["C03-facts"],
                    ),
                ],
                [
                    {
                        "event": "route-selected",
                        "owner": "/grill-me",
                        "mode": "analysis-only",
                        "event_index": 3,
                    }
                ],
                [],
                {
                    "Facts": [c03_root],
                    "Reports": [c03_root, "C03-ALT-A"],
                    "Constraints": ["C03-ALT-B"],
                },
            ),
            _observation(
                "C-04",
                [_decision(c04_root, "accepted", evidence_ids=["C04-unknowns"])],
                [_question("C04-Q1", c04_root, 2, ["C04-unknowns"])],
                c04_transitions,
                [
                    {
                        "event": "route-selected",
                        "owner": "/grill-me",
                        "mode": "analysis-only",
                        "subject": "C-04",
                        "event_index": 2,
                    },
                    {
                        "event": "subject-change",
                        "owner": "internal-gateway-idea",
                        "mode": "analysis-only",
                        "subject": "C-04-next",
                        "event_index": 6,
                    },
                    {
                        "event": "mode-change",
                        "owner": "internal-gateway-idea",
                        "mode": "analysis-and-artifact",
                        "subject": "C-04-next",
                        "event_index": 7,
                    },
                ],
                [],
                {"Unknowns": [c04_root]},
            ),
            _observation(
                "C-05",
                [_decision(c05_root, "accepted", evidence_ids=["C05-unknowns"])],
                [_question("C05-Q1", c05_root, 2, ["C05-unknowns"])],
                [
                    {"event": "setup-complete", "event_index": 1},
                    {
                        "event": "gate-entered",
                        "gate": "GRILL-ME",
                        "phase": "post-setup",
                        "route_owner": "/grill-me",
                        "event_index": 2,
                        "question_ids": ["C05-Q1"],
                        "eligible_decision_ids": [c05_root],
                        "repeat": False,
                    },
                    _status_event(
                        c05_root, "open", "accepted", 3, trigger="explicit-user-change"
                    ),
                    _candidate_menu(
                        4,
                        phase="pre-review",
                        findings_present=True,
                        critical_review_complete=False,
                        dispositions_complete=False,
                    ),
                    {
                        "event": "critical-review",
                        "gate": "CRITICAL REVIEW",
                        "event_index": 5,
                        "explicit": True,
                        "completed": True,
                        "lenses": [
                            {"name": "primary", "type": "system-boundary"},
                            {"name": "evidence", "type": "evidence-quality"},
                            {"name": "lateral", "type": "analogy"},
                        ],
                        "finding_ids": ["C05-F1"],
                        "conclusion": "The candidate is ready after explicit finding disposition.",
                    },
                    {
                        "event": "critical-finding",
                        "event_index": 6,
                        "finding_ids": ["C05-F1"],
                        "findings": [
                            {
                                "finding_id": "C05-F1",
                                "classification": "acceptance-required",
                            }
                        ],
                    },
                    {
                        "event": "realignment",
                        "event_index": 7,
                        "explicit": True,
                        "finding_ids": ["C05-F1"],
                    },
                    {
                        "event": "critical-disposition",
                        "event_index": 8,
                        "explicit": True,
                        "finding_ids": ["C05-F1"],
                        "dispositions": {"C05-F1": "integrate"},
                    },
                    _candidate_menu(
                        9,
                        phase="post-review",
                        findings_present=True,
                        critical_review_complete=True,
                        dispositions_complete=True,
                    ),
                    {
                        "event": "gate-override",
                        "gate": "CRITICAL REVIEW",
                        "action": "close",
                        "named_action": "close",
                        "risk_disposition": "accepted-risk",
                        "preserved_gates": ["GRILL-ME"],
                        "event_index": 9.5,
                        "explicit": True,
                    },
                ],
                [
                    {
                        "event": "route-selected",
                        "owner": "/grill-me",
                        "mode": "analysis-only",
                        "event_index": 2,
                    }
                ],
                [
                    {
                        "event": "candidate-presented",
                        "event_index": 4,
                        "artifact_id": "C05-analysis",
                    },
                    {
                        "event": "artifact-saved",
                        "event_index": 4.5,
                        "artifact_id": "C05-analysis",
                        "path": "tmp/superpowers/specs/c05-analysis.md",
                        "promotes": False,
                        "checkpoint": True,
                        "critical_review": "pending",
                        "closes_findings": False,
                        "authorizes": [],
                    },
                    {
                        "event": "candidate-accepted",
                        "event_index": 10,
                        "explicit": True,
                        "choice": "+spec",
                        "artifact_id": "C05-analysis",
                    },
                    {
                        "event": "critical-choice",
                        "event_index": 11,
                        "choice": "integrate",
                        "explicit": True,
                    },
                    {
                        "event": "critical-findings-integrated",
                        "event_index": 12,
                        "artifact_id": "C05-analysis",
                    },
                    {
                        "event": "spec-authored",
                        "event_index": 13,
                        "artifact_id": "C05-analysis",
                        "path": "tmp/superpowers/specs/c05-analysis.md",
                        "plan_authoring_ready": True,
                    },
                    {
                        "event": "planning-replay",
                        "event_index": 14,
                        "artifact_id": "C05-analysis",
                        "uses_transcript": False,
                    },
                ],
                {"Unknowns": [c05_root]},
                communication_records=[
                    {
                        "view_id": "C-05-candidate",
                        "kind": "candidate",
                        "event_index": 4,
                        "material_delta_ids": ["C05-ROOT"],
                        "outcome": "decision-ready",
                        "controlling_evidence_ids": ["C05-facts", "C05-unknowns"],
                        "principal_risk_id": "C05-RISK",
                        "active_choice": "choice-C-05",
                        "blocker_ids": [],
                        "unknown_ids": ["C05-UNKNOWN"],
                        "acceptance_condition_ids": ["C05-ACCEPT"],
                        "word_count": 160,
                        "word_count_mode": "diagnostic",
                        "diagrams": [
                            {
                                "relationship_count": 3,
                                "useful": True,
                                "conclusion_adjacent": True,
                            }
                        ],
                    }
                ],
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
    c02["recovery_records"][0]["authority_envelope"]["authorized_actions"] = [
        "write-code"
    ]
    c01["authority_events"][2]["authorizes_mutation"] = True
    c02["authority_events"] = [
        event
        for event in c02["authority_events"]
        if event.get("event") != "scope-delta"
    ]
    c03["authority_events"][1]["authorized_actions"] = ["save-analysis", "write-code"]
    c04["communication_records"][0]["material_delta_ids"] = []
    c05["communication_records"][0]["diagrams"] = [
        {"relationship_count": 2, "useful": False, "conclusion_adjacent": False},
        {"relationship_count": 4, "useful": True, "conclusion_adjacent": True},
    ]
    c05["transition_events"] = [
        event
        for event in c05["transition_events"]
        if event.get("event") not in {"realignment", "critical-disposition"}
    ]
    for event in c05["transition_events"]:
        if (
            event.get("event") == "candidate-menu"
            and event.get("phase") == "pre-review"
        ):
            event["options"] = ["continue", "+spec", "+plan", "save", "close"]
        if event.get("event") == "gate-entered":
            event["gate"] = "ACCEPTANCE"
        if event.get("event") == "critical-review":
            event["lenses"] = event["lenses"][:2]
            event["conclusion"] = ""
        if event.get("event") == "gate-override":
            event["preserved_gates"] = []
            event["risk_disposition"] = "integrate"
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
        if event.get("event") == "artifact-saved":
            event["critical_review"] = "complete"
    for event in c05["artifact_events"]:
        if event.get("event") == "planning-replay":
            event["uses_transcript"] = True

    return run


def test_new_records_cover_authority_lifecycle_and_communication_without_prose_matching() -> (
    None
):
    scorer = load_scorer()

    result = scorer.score(load_manifest(), passing_run())

    assert result["authority_envelope_violation_cases"] == []
    assert result["protected_status_authority_violation_cases"] == []
    assert result["scope_delta_violation_cases"] == []
    assert result["lifecycle_order_violation_cases"] == []
    assert result["canonical_view_violation_cases"] == []
    assert result["visual_budget_violation_cases"] == []
    assert result["critical_disposition_violation_cases"] == []
    assert result["save_semantics_violation_cases"] == []


def test_new_records_derive_authority_lifecycle_and_communication_findings() -> None:
    scorer = load_scorer()

    result = scorer.score(load_manifest(), failing_run())

    assert result["accepted"] is False
    assert result["authority_envelope_violation_cases"] == ["C-03"]
    assert result["protected_status_authority_violation_cases"] == ["C-01"]
    assert result["scope_delta_violation_cases"] == ["C-02"]
    assert result["lifecycle_order_violation_cases"] == ["C-05"]
    assert result["canonical_view_violation_cases"] == ["C-04"]
    assert result["visual_budget_violation_cases"] == ["C-05"]
    assert result["critical_disposition_violation_cases"] == ["C-05"]
    assert result["save_semantics_violation_cases"] == ["C-05"]


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
    assert protected["save_is_non_promoting"] is True
    lifecycle = manifest["lifecycle_workflow"]
    assert lifecycle["disposition_event"] == "critical-disposition"
    assert lifecycle["promotion_options"] == ["+spec", "+plan"]
    assert lifecycle["spec_artifact_readiness_field"] == "plan_authoring_ready"
    assert lifecycle["allowed_dispositions"] == [
        "integrate",
        "reject",
        "accept-risk",
        "route",
    ]


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
    assert result["canonical_recovery_violation_cases"] == ["C-02", "C-04", "C-05"]
    assert result["gate_type_violation_cases"] == ["C-05"]
    assert result["grill_me_routing_violation_cases"] == ["C-05"]
    assert result["critical_review_completion_violation_cases"] == ["C-05"]
    assert result["gate_override_violation_cases"] == ["C-05"]
    assert result["menu_projection_violation_cases"] == ["C-05"]
    assert result["provisional_save_violation_cases"] == ["C-05"]

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


def _run_cli(
    tmp_path: Path, manifest: object, run: object
) -> subprocess.CompletedProcess[str]:
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


def test_passing_records_expose_canonical_recovery_and_route_projection_findings() -> (
    None
):
    scorer = load_scorer()

    result = scorer.score(load_manifest(), passing_run())

    assert result["canonical_recovery_violation_cases"] == []
    assert result["route_projection_violation_cases"] == []


def test_public_wrapper_projects_one_autonomous_route_without_brainstorming_handoff() -> (
    None
):
    metadata = yaml.safe_load(PUBLIC_WRAPPER_PATH.read_text(encoding="utf-8"))
    prompt = metadata["interface"]["default_prompt"]

    assert "policy" not in metadata
    assert "autonomous route" in prompt
    assert "/superpowers-brainstorming" not in prompt
    assert prompt.count("/internal-gateway-execute-plans") == 1


def test_public_wrapper_declares_the_canonical_route_contract() -> None:
    metadata = yaml.safe_load(PUBLIC_WRAPPER_PATH.read_text(encoding="utf-8"))

    assert metadata["route_contract"] == {
        "owner": "/internal-gateway-idea",
        "mode": "analysis-only",
        "execution_handoff": "/internal-gateway-execute-plans",
        "forbidden_pre_acceptance_routes": [
            "/internal-tdd",
            "/internal-gateway-writing-plans",
            "/internal-gateway-execute-plans",
        ],
    }


def test_promotion_requires_disposition_and_save_stays_non_promoting() -> None:
    scorer = load_scorer()

    result = scorer.score(load_manifest(), passing_run())

    assert result["critical_disposition_violation_cases"] == []
    assert result["save_semantics_violation_cases"] == []


def test_spec_acceptance_retains_plan_ready_artifact_without_immediate_handoff() -> (
    None
):
    scorer = load_scorer()

    complete = passing_run()
    complete_result = scorer.score(load_manifest(), complete)
    assert complete["observations"][4]["recovery_records"][0]["unit_lock"][
        "implementation_permission"
    ] is False
    assert complete_result["accepted"] is True
    assert complete_result["spec_plan_readiness_violation_cases"] == []
    assert not any(
        event.get("event") == "plan-authoring-handoff"
        for event in complete["observations"][4]["route_events"]
    )

    blocked_spec = copy.deepcopy(complete)
    c05 = blocked_spec["observations"][4]
    spec_artifact = next(
        event
        for event in c05["artifact_events"]
        if event.get("event") == "spec-authored"
    )
    spec_artifact["plan_authoring_ready"] = False
    blocked_result = scorer.score(load_manifest(), blocked_spec)
    assert blocked_result["accepted"] is False
    assert blocked_result["spec_plan_readiness_violation_cases"] == ["C-05"]


def test_synthetic_records_keep_controlled_runtime_readiness_unavailable() -> None:
    scorer = load_scorer()

    result = scorer.score(load_manifest(), passing_run())

    assert result["behavioral_evidence"]["controlled_runtime"] == "unavailable"
    assert result["behavioral_evidence"]["merge_ready"] is False


def test_public_wrapper_declares_no_token_budget_or_question_cap() -> None:
    metadata = yaml.safe_load(PUBLIC_WRAPPER_PATH.read_text(encoding="utf-8"))

    assert "token_budget" not in metadata
    assert "question_cap" not in metadata
    assert "max_questions" not in metadata
    assert "fixed_question_cap" not in metadata


def test_manifest_and_records_derive_the_two_gate_contract() -> None:
    manifest = load_manifest()
    lifecycle = manifest["lifecycle_workflow"]

    assert lifecycle.get("global_gates") == ["GRILL-ME", "CRITICAL REVIEW"]
    assert lifecycle.get("post_setup_gate") == "GRILL-ME"
    assert lifecycle.get("review_lenses") == ["primary", "evidence", "lateral"]
    assert lifecycle.get("lateral_lens_types") == ["analogy", "reverse-assumption"]

    scorer = load_scorer()
    result = scorer.score(manifest, passing_run())
    assert result.get("gate_type_violation_cases") == []
    assert result.get("grill_me_routing_violation_cases") == []
    assert result.get("critical_review_completion_violation_cases") == []
    assert result.get("gate_override_violation_cases") == []
    assert result.get("menu_projection_violation_cases") == []
    assert result.get("provisional_save_violation_cases") == []
