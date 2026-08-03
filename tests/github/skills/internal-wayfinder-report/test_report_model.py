from __future__ import annotations

import importlib.util
import json
import shutil
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
BUNDLE_ROOT = REPO_ROOT / ".github/skills/internal-wayfinder-report"


FIXTURE = Path(__file__).parent / "fixtures" / "valid-model.v1.json"
RENDERER = BUNDLE_ROOT / "scripts" / "render_report.py"


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
ModelError = report_model.ModelError
load_payload = report_model.load_payload
load_report_model = report_model.load_report_model
rank_findings = report_model.rank_findings


def make_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    (workspace / "issues").mkdir(parents=True)
    (workspace / "report").mkdir()
    (workspace / "map.md").write_text(
        "# Map\n\nDestination: create a traceable local report.\n",
        encoding="utf-8",
    )
    (workspace / "analysis.md").write_text(
        "# Analysis\n\nProblem: decisions are hard to trace.\n",
        encoding="utf-8",
    )
    (workspace / "issues" / "01.md").write_text(
        "# Issue 01\n\nDecision: keep report generation read-only.\n",
        encoding="utf-8",
    )
    return workspace


def fixture_payload() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def copy_fixture_into_report(workspace: Path) -> Path:
    model_path = workspace / "report" / "report-model.v1.json"
    shutil.copyfile(FIXTURE, model_path)
    return model_path


def test_load_report_model_accepts_v1_and_preserves_claim_sources(
    tmp_path: Path,
) -> None:
    workspace = make_workspace(tmp_path)
    model_path = copy_fixture_into_report(workspace)

    model = load_report_model(model_path, workspace)

    assert model.schema_version == 1
    assert model.destination.sources[0].path == "map.md"
    assert model.review.findings[0].evidence[0].path in {"map.md", "analysis.md"}


@pytest.mark.parametrize(
    "bad_path",
    ["../outside.md", "/tmp/outside.md", "https://example.invalid/source"],
)
def test_load_report_model_rejects_non_local_source_paths(
    tmp_path: Path, bad_path: str
) -> None:
    workspace = make_workspace(tmp_path)
    payload = fixture_payload()
    payload["destination"]["sources"][0]["path"] = bad_path  # type: ignore[index]

    with pytest.raises(ModelError, match="workspace"):
        load_payload(payload, workspace)


def test_load_report_model_rejects_unknown_version_and_missing_claim_sources(
    tmp_path: Path,
) -> None:
    workspace = make_workspace(tmp_path)

    unknown_version = fixture_payload()
    unknown_version["schema_version"] = 2
    with pytest.raises(ModelError, match="schema_version"):
        load_payload(unknown_version, workspace)

    missing_sources = fixture_payload()
    missing_sources["destination"]["sources"] = []  # type: ignore[index]
    with pytest.raises(ModelError, match="sources"):
        load_payload(missing_sources, workspace)


def test_load_report_model_rejects_unknown_fields_and_non_files(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)

    unknown_field = fixture_payload()
    unknown_field["unexpected"] = True
    with pytest.raises(ModelError, match="unknown fields"):
        load_payload(unknown_field, workspace)

    for bad_path in ("missing.md", "issues", "issues/../map.md"):
        bad_source = fixture_payload()
        bad_source["destination"]["sources"][0]["path"] = bad_path  # type: ignore[index]
        with pytest.raises(ModelError, match="workspace"):
            load_payload(bad_source, workspace)


def test_load_report_model_rejects_a_symlink_outside_workspace(tmp_path: Path) -> None:
    workspace = make_workspace(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    (workspace / "outside-link.md").symlink_to(outside)
    payload = fixture_payload()
    payload["destination"]["sources"][0]["path"] = "outside-link.md"  # type: ignore[index]

    with pytest.raises(ModelError, match="workspace"):
        load_payload(payload, workspace)


def test_rank_findings_returns_every_finding_in_stable_priority_order(
    tmp_path: Path,
) -> None:
    workspace = make_workspace(tmp_path)
    model = load_report_model(copy_fixture_into_report(workspace), workspace)

    ranked = rank_findings(model.review.findings)

    assert [finding.id for finding in ranked] == [
        "finding-01",
        "finding-02",
        "finding-03",
        "finding-04",
        "finding-05",
        "finding-06",
    ]
    assert len(ranked) == len(model.review.findings) == 6


def test_bundle_paths_and_renderer_help_are_available() -> None:
    result = subprocess.run(
        [sys.executable, str(RENDERER), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (BUNDLE_ROOT / "SKILL.md").is_file()
    assert (BUNDLE_ROOT / "agents" / "openai.yaml").is_file()
    assert (BUNDLE_ROOT / "references" / "report-model-v1.schema.json").is_file()
    assert (BUNDLE_ROOT / "scripts" / "report_model.py").is_file()
    assert (BUNDLE_ROOT / "scripts" / "render_report.py").is_file()

    metadata = yaml.safe_load(
        (BUNDLE_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    )
    interface = metadata["interface"]
    assert isinstance(interface["display_name"], str)
    assert isinstance(interface["short_description"], str)
    assert isinstance(interface["default_prompt"], str)
