from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE_ROOT = REPO_ROOT / ".github/skills/internal-wayfinder-report"
FIXTURE = (
    REPO_ROOT
    / "tests/github/skills/internal-wayfinder-report/fixtures/valid-model.v1.json"
)


def load_bundle_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


report_model = load_bundle_module(
    "report_model", BUNDLE_ROOT / "scripts" / "report_model.py"
)
report_view = load_bundle_module(
    "report_view", BUNDLE_ROOT / "scripts" / "report_view.py"
)


def build_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    (workspace / "issues").mkdir(parents=True)
    (workspace / "report").mkdir()
    (workspace / "map.md").write_text("# Map\n", encoding="utf-8")
    (workspace / "analysis.md").write_text("# Analysis\n", encoding="utf-8")
    (workspace / "issues" / "01.md").write_text("# Issue 01\n", encoding="utf-8")
    return workspace


def load_fixture_model(tmp_path: Path, mutate=None):
    workspace = build_workspace(tmp_path)
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if mutate is not None:
        mutate(payload)
    model_path = workspace / "report" / "report-model.v1.json"
    model_path.write_text(json.dumps(payload), encoding="utf-8")
    return report_model.load_report_model(model_path, workspace)


def append_decision(payload: dict, title: str, state: str) -> None:
    decision_path = payload["understand"]["decision_path"]
    entry = json.loads(json.dumps(decision_path[0]))
    entry["title"] = title
    entry["state"] = state
    decision_path.append(entry)


def test_derive_metrics_flags_specified_without_implementation(tmp_path: Path) -> None:
    model = load_fixture_model(
        tmp_path,
        lambda payload: payload["understand"]["implementation"].update(
            {"implemented": []}
        ),
    )

    metrics = {metric.label: metric for metric in report_view.derive_metrics(model)}

    assert "Copertura" in metrics
    assert metrics["Copertura"].tone == "critical"
    assert "senza prova di implementazione" in metrics["Copertura"].detail


def test_derive_metrics_reports_decisions_findings_and_verification(
    tmp_path: Path,
) -> None:
    model = load_fixture_model(tmp_path)

    metrics = {metric.label: metric for metric in report_view.derive_metrics(model)}

    assert set(metrics) == {
        "Stato",
        "Decisioni",
        "Copertura",
        "Findings",
        "Da verificare",
    }
    assert metrics["Stato"].value == report_view.STATUS_LABELS[model.status]
    resolved = sum(
        1 for entry in model.understand.decision_path if entry.state == "resolved"
    )
    assert metrics["Decisioni"].value == (
        f"{resolved}/{len(model.understand.decision_path)}"
    )
    assert metrics["Findings"].value == str(len(model.review.findings))


def test_decision_path_flowchart_links_entries_and_marks_states(
    tmp_path: Path,
) -> None:
    model = load_fixture_model(
        tmp_path,
        lambda payload: append_decision(payload, "Scegliere il formato", "open"),
    )

    flowchart = report_view.decision_path_flowchart(model)

    assert flowchart is not None
    assert flowchart.startswith("flowchart TD")
    assert "D1 --> D2" in flowchart
    assert "classDef resolved" in flowchart
    assert flowchart.count("-->") == len(model.understand.decision_path) - 1
    assert "class D1 resolved;" in flowchart
    assert "class D2 open;" in flowchart


def test_decision_path_flowchart_is_none_without_entries(tmp_path: Path) -> None:
    model = load_fixture_model(
        tmp_path,
        lambda payload: payload["understand"].update({"decision_path": []}),
    )

    assert report_view.decision_path_flowchart(model) is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('Titolo "critico" [urgente]', "Titolo 'critico' urgente"),
        ("A --> B; class X", "A B class X"),
        ("   ", "(senza titolo)"),
    ],
)
def test_mermaid_label_neutralizes_syntax_characters(raw: str, expected: str) -> None:
    assert report_view.mermaid_label(raw) == expected


def test_mermaid_label_truncates_long_titles() -> None:
    label = report_view.mermaid_label("parola " * 40)

    assert len(label) <= 80
    assert label.endswith("…")


def test_rank_reason_names_impact_certainty_and_propagation(tmp_path: Path) -> None:
    model = load_fixture_model(tmp_path)
    finding = report_model.rank_findings(model.review.findings)[0]

    reason = report_view.rank_reason(finding)

    assert report_view.IMPACT_LABELS[finding.impact_level] in reason
    assert report_view.CERTAINTY_LABELS[finding.certainty] in reason
    assert f"propagazione {finding.propagation}" in reason
