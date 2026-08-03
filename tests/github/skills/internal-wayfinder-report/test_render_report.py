from __future__ import annotations

import importlib.util
import json
import re
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
report_view = load_bundle_module(
    "report_view", BUNDLE_ROOT / "scripts" / "report_view.py"
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


def test_render_writes_one_page_and_preserves_sources(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    before = snapshot_source_bytes(workspace)

    index_path = render_report(
        workspace, workspace / "report" / "report-model.v1.json"
    )

    assert index_path == workspace / "report" / "index.html"
    markup = index_path.read_text(encoding="utf-8")
    assert 'id="overview"' in markup
    assert 'id="review"' in markup
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


def test_findings_are_ordered_by_rank(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)

    render_report(workspace, workspace / "report" / "report-model.v1.json")
    html = (workspace / "report" / "index.html").read_text(encoding="utf-8")

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


def test_report_uses_progressive_section_order(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    model_path = workspace / "report" / "report-model.v1.json"

    index_path = render_report(workspace, model_path)

    assert index_path == workspace / "report" / "index.html"
    assert not (workspace / "report" / "review.html").exists()
    markup = index_path.read_text(encoding="utf-8")
    offsets = [
        markup.index(f'id="{section}"')
        for section in ("overview", "solution", "decisions", "scope", "review")
    ]
    assert offsets == sorted(offsets)


def test_render_is_byte_identical_on_repeated_runs(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    model_path = workspace / "report" / "report-model.v1.json"

    first = render_report(workspace, model_path).read_bytes()
    second = render_report(workspace, model_path).read_bytes()

    assert first == second


def test_render_rejects_template_missing_required_placeholder(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    model_path = workspace / "report" / "report-model.v1.json"
    broken = tmp_path / "broken.html"
    broken.write_text("<html>${title}</html>", encoding="utf-8")

    with pytest.raises(ModelError) as error:
        render_report(workspace, model_path, template_path=broken)

    assert "placeholder" in str(error.value)
    assert not (workspace / "report" / "index.html").exists()


def test_render_rejects_unknown_template_placeholder(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    model_path = workspace / "report" / "report-model.v1.json"
    template = tmp_path / "unknown.html"
    known = "".join(
        "${" + name + "}" for name in sorted(render_report_module.REQUIRED_PLACEHOLDERS)
    )
    template.write_text(known + "${sconosciuto}", encoding="utf-8")

    with pytest.raises(ModelError):
        render_report(workspace, model_path, template_path=template)

    assert not (workspace / "report" / "index.html").exists()


def test_render_rejects_missing_template_file(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    model_path = workspace / "report" / "report-model.v1.json"

    with pytest.raises(ModelError):
        render_report(workspace, model_path, template_path=tmp_path / "assente.html")

    assert not (workspace / "report" / "index.html").exists()


def test_bundle_template_declares_every_required_placeholder() -> None:
    template_text = (BUNDLE_ROOT / "templates" / "report.html").read_text(
        encoding="utf-8"
    )

    for placeholder in render_report_module.REQUIRED_PLACEHOLDERS:
        assert "${" + placeholder + "}" in template_text


def test_sources_are_collapsed_but_complete(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    index_path = render_report(workspace, workspace / "report" / "report-model.v1.json")

    markup = index_path.read_text(encoding="utf-8")

    assert '<details class="sources">' in markup
    assert "<summary>Fonti (" in markup
    assert '<details class="sources" open' not in markup
    assert 'href="../map.md"' in markup


def test_decision_status_has_no_generated_mermaid_edges(
    tmp_path: Path,
) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    model_path = workspace / "report" / "report-model.v1.json"
    payload = json.loads(model_path.read_text(encoding="utf-8"))
    payload["understand"]["diagrams"] = []
    model_path.write_text(json.dumps(payload), encoding="utf-8")

    markup = render_report(workspace, model_path).read_text(encoding="utf-8")

    assert 'class="decision-board"' in markup
    assert 'data-decision-state="resolved"' in markup
    assert 'class="diagram"' not in markup
    assert "-->" not in markup


def test_ranked_findings_are_complete_with_only_first_open(
    tmp_path: Path,
) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    markup = render_report(
        workspace, workspace / "report" / "report-model.v1.json"
    ).read_text(encoding="utf-8")

    assert markup.count('class="finding-disclosure"') == 6
    assert markup.count('class="finding-disclosure" open') == 1
    assert markup.index('data-finding-id="finding-01"') < markup.index(
        'data-finding-id="finding-06"'
    )


def test_finding_summary_explains_its_rank(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    markup = render_report(
        workspace, workspace / "report" / "report-model.v1.json"
    ).read_text(encoding="utf-8")

    assert "propagazione" in markup
    assert "Perché è in cima" in markup


def test_specified_without_implementation_is_marked_as_a_gap(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    model_path = workspace / "report" / "report-model.v1.json"
    payload = json.loads(model_path.read_text(encoding="utf-8"))
    payload["understand"]["implementation"]["implemented"] = []
    model_path.write_text(json.dumps(payload), encoding="utf-8")

    markup = render_report(workspace, model_path).read_text(encoding="utf-8")

    assert "Nessuna prova di implementazione" in markup


def test_preview_renders_the_bundled_sample_into_the_target_directory(
    tmp_path: Path,
) -> None:
    target = tmp_path / "anteprima"

    index_path = render_report_module.render_preview(target)

    assert index_path == target / "report" / "index.html"
    assert (target / "map.md").is_file()
    assert (target / "analysis.md").is_file()
    markup = index_path.read_text(encoding="utf-8")
    assert 'id="overview"' in markup
    assert 'id="review"' in markup


def test_preview_default_directory_is_outside_the_wayfinder_slug_namespace() -> None:
    assert render_report_module.DEFAULT_PREVIEW_DIR == Path(
        "tmp/.wayfinder-report-preview"
    )
    assert ".wayfinder/" not in str(render_report_module.DEFAULT_PREVIEW_DIR)


def test_cli_requires_workspace_and_model_without_preview(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(RENDERER), "--workspace", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--model" in result.stderr


def test_cli_preview_writes_one_page(tmp_path: Path) -> None:
    target = tmp_path / "cli-anteprima"

    result = subprocess.run(
        [sys.executable, str(RENDERER), "--preview", str(target)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (target / "report" / "index.html").is_file()
    assert not (target / "report" / "review.html").exists()


MERMAID_PINNED_VERSION = "mermaid@11.6.0"


def test_template_mermaid_block_is_pinned_and_hardened() -> None:
    template_text = (BUNDLE_ROOT / "templates" / "report.html").read_text(
        encoding="utf-8"
    )

    assert MERMAID_PINNED_VERSION in template_text
    assert 'crossorigin="anonymous"' in template_text
    assert 'referrerpolicy="no-referrer"' in template_text
    assert "securityLevel: 'strict'" in template_text
    assert "htmlLabels: false" in template_text
    assert "startOnLoad: false" in template_text
    assert "source.textContent" in template_text
    assert "innerHTML = result.svg" in template_text
    assert "window.mermaid.parse" in template_text
    assert "diagram-fallback" in template_text
    assert "diagram-error" in template_text
    assert 'role="alert"' in template_text
    assert "catch(function (error)" in template_text
    assert "data-copy-target" in template_text
    assert "navigator.clipboard" in template_text
    assert "prefers-color-scheme: dark" in template_text
    assert "@media print" in template_text
    assert "@media (max-width: 720px)" in template_text


def test_template_never_ships_a_placeholder_integrity_value() -> None:
    template_text = (BUNDLE_ROOT / "templates" / "report.html").read_text(
        encoding="utf-8"
    )

    for match in re.finditer(r'integrity="([^"]*)"', template_text):
        assert re.fullmatch(r"sha384-[A-Za-z0-9+/]{60,}={0,2}", match.group(1))


def test_diagram_source_stays_visible_without_javascript(tmp_path: Path) -> None:
    workspace = make_workspace_with_fixture(tmp_path)
    markup = render_report(
        workspace, workspace / "report" / "report-model.v1.json"
    ).read_text(encoding="utf-8")

    target_position = markup.index('class="diagram-target"')
    fallback_position = markup.index('class="diagram-fallback"')
    source_position = markup.index('class="diagram-source"')
    assert target_position < fallback_position < source_position
    assert '<p class="diagram-fallback">' in markup
    assert '<p class="diagram-error" role="alert" hidden>' in markup
    assert '<details class="diagram-debug">' in markup
    assert "A[Sources] --&gt; B[Model] --&gt; C[Views]" in markup
    assert 'class="diagram-source" hidden' not in markup
