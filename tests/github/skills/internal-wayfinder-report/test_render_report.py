from __future__ import annotations

import importlib.util
import json
import shutil
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
BUNDLE_ROOT = REPO_ROOT / ".github/skills/internal-wayfinder-report"
FIXTURE = (
    REPO_ROOT
    / "tests/github/skills/internal-wayfinder-report/fixtures/valid-model.v1.json"
)
RENDERER = BUNDLE_ROOT / "scripts/render_report.py"


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
render_report_module = load_bundle_module("render_report", RENDERER)
ModelError = report_model.ModelError
render_report = render_report_module.render_report


def make_workspace_with_fixture(
    tmp_path: Path,
    *,
    claim_text: str | None = None,
) -> Path:
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
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if claim_text is not None:
        payload["destination"]["text"] = claim_text
    (workspace / "report" / "report-model.v1.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    return workspace


def snapshot_source_bytes(workspace: Path) -> dict[Path, bytes]:
    source_paths = [workspace / "map.md", workspace / "analysis.md"]
    source_paths.extend(sorted((workspace / "issues").glob("*.md")))
    return {path.relative_to(workspace): path.read_bytes() for path in source_paths}


def write_fixture_with_source(workspace: Path, source_path: str) -> Path:
    model_path = workspace / "report" / "report-model.v1.json"
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["destination"]["sources"][0]["path"] = source_path
    model_path.write_text(json.dumps(payload), encoding="utf-8")
    return model_path


def test_render_report_writes_two_views_and_preserves_sources(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    before = snapshot_source_bytes(workspace)

    index_path, review_path = render_report(
        workspace, workspace / "report" / "report-model.v1.json"
    )

    assert (index_path, review_path) == (
        workspace / "report" / "index.html",
        workspace / "report" / "review.html",
    )
    assert "Comprendi il risultato" in index_path.read_text(encoding="utf-8")
    assert "Revisiona la coerenza" in review_path.read_text(encoding="utf-8")
    assert snapshot_source_bytes(workspace) == before


def test_renderer_escapes_claims_and_links_only_inside_workspace(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(
        tmp_path, claim_text="<script>alert(1)</script>"
    )

    render_report(workspace, workspace / "report" / "report-model.v1.json")
    html = (workspace / "report" / "index.html").read_text(encoding="utf-8")

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>alert(1)</script>" not in html
    assert 'href="../map.md"' in html
    assert 'href="../issues/01.md"' in html

    with pytest.raises(ModelError, match="workspace"):
        render_report(
            workspace,
            write_fixture_with_source(workspace, "../outside.md"),
        )


def test_review_shows_five_findings_and_discloses_the_rest(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)

    render_report(workspace, workspace / "report" / "report-model.v1.json")
    html = (workspace / "report" / "review.html").read_text(encoding="utf-8")

    assert html.count('data-finding-card="primary"') == 5
    assert '<details class="secondary-findings">' in html
    assert 'data-finding-card="secondary"' in html
    assert html.index('data-finding-id="finding-01"') < html.index(
        'data-finding-id="finding-06"'
    )


def test_renderer_rejects_model_outside_report_before_writing_html(
    tmp_path: Path,
) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    outside_model = workspace / "model.json"
    shutil.copyfile(workspace / "report" / "report-model.v1.json", outside_model)

    with pytest.raises(ModelError, match="report"):
        render_report(workspace, outside_model)

    assert not (workspace / "report" / "index.html").exists()
    assert not (workspace / "report" / "review.html").exists()


def test_renderer_rejects_invalid_model_before_writing_html(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    model_path = workspace / "report" / "report-model.v1.json"
    model_path.write_text("{\"schema_version\": 2}", encoding="utf-8")

    with pytest.raises(ModelError):
        render_report(workspace, model_path)

    assert not (workspace / "report" / "index.html").exists()
    assert not (workspace / "report" / "review.html").exists()


def test_renderer_rejects_report_path_that_is_a_file(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "map.md").write_text("map", encoding="utf-8")
    (workspace / "analysis.md").write_text("analysis", encoding="utf-8")
    (workspace / "report").write_text("not a directory", encoding="utf-8")

    with pytest.raises(ModelError, match="report"):
        render_report(workspace, workspace / "report" / "report-model.v1.json")

    assert not (workspace / "index.html").exists()
    assert not (workspace / "review.html").exists()


def test_renderer_cli_rejects_invalid_model_without_partial_output(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    model_path = workspace / "report" / "report-model.v1.json"
    model_path.write_text("not json", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(RENDERER),
            "--workspace",
            str(workspace),
            "--model",
            str(model_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert result.stderr.strip()
    assert not (workspace / "report" / "index.html").exists()
    assert not (workspace / "report" / "review.html").exists()
