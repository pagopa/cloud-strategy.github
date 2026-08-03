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
FIXTURES_ROOT = REPO_ROOT / "tests/github/skills/internal-wayfinder-report/fixtures"
RENDERER = BUNDLE_ROOT / "scripts/render_report.py"
SECTION_IDS = ("overview", "solution", "decisions", "scope", "reading", "review")
MERMAID_PINNED_VERSION = "mermaid@11.6.0"


def load_bundle_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    scripts_path = str(path.parent)
    sys.path.insert(0, scripts_path)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(scripts_path)
    return module


render_report_module = load_bundle_module("wayfinder_render_report", RENDERER)
ReportError = getattr(render_report_module, "ReportError", ValueError)
render_report = render_report_module.render_report


def copy_workspace(tmp_path: Path, name: str) -> Path:
    source = FIXTURES_ROOT / name
    workspace = tmp_path / name
    shutil.copytree(source, workspace)
    return workspace


def report_path(workspace: Path) -> Path:
    return workspace / "report" / "report.json"


def load_payload(workspace: Path) -> dict[str, object]:
    return json.loads(report_path(workspace).read_text(encoding="utf-8"))


def write_payload(workspace: Path, payload: dict[str, object]) -> None:
    report_path(workspace).write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def snapshot_source_bytes(workspace: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(workspace): path.read_bytes()
        for path in sorted(workspace.rglob("*"))
        if path.is_file() and "report" not in path.relative_to(workspace).parts
    }


def test_generic_contract_renders_unrelated_fixtures(tmp_path: Path) -> None:
    minimal = copy_workspace(tmp_path, "minimal")
    dense = copy_workspace(tmp_path, "dense")

    minimal_html = render_report(minimal, report_path(minimal)).read_text()
    dense_html = render_report(dense, report_path(dense)).read_text()

    assert "Choose a safe delivery path" in minimal_html
    assert "Coordinate a multi-stage migration" in dense_html
    assert "Terraform" not in minimal_html
    assert "SOPS" not in dense_html


def test_one_evidence_entry_can_support_multiple_blocks(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "minimal")
    payload = load_payload(workspace)

    assert list(payload["evidence"]).count("E01") == 1
    markup = render_report(workspace, report_path(workspace)).read_text()

    assert markup.count('href="../map.md"') >= 2


@pytest.mark.parametrize(
    ("case", "match"),
    [
        ("unknown-evidence", "E99"),
        ("absent-excerpt", "excerpt"),
        ("traversal", "inside the workspace"),
        ("absolute", "inside the workspace"),
        ("url", "inside the workspace"),
        ("directory", "regular file"),
        ("missing-file", "regular file"),
        ("outward-symlink", "regular file"),
    ],
)
def test_invalid_evidence_references_fail_before_output(
    tmp_path: Path, case: str, match: str
) -> None:
    workspace = copy_workspace(tmp_path, "minimal")
    payload = load_payload(workspace)
    evidence = payload["evidence"]
    assert isinstance(evidence, dict)

    if case == "unknown-evidence":
        payload["destination"]["evidence"] = ["E99"]
    elif case == "absent-excerpt":
        evidence["E01"]["excerpt"] = "This text is absent from map.md."
    elif case == "traversal":
        evidence["E01"]["path"] = "../outside.md"
    elif case == "absolute":
        evidence["E01"]["path"] = str((tmp_path / "outside.md").resolve())
    elif case == "url":
        evidence["E01"]["path"] = "https://example.com/evidence.md"
    elif case == "directory":
        evidence["E01"]["path"] = "issues"
    elif case == "missing-file":
        evidence["E01"]["path"] = "missing.md"
    else:
        outside = tmp_path / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        (workspace / "link.md").symlink_to(outside)
        evidence["E01"]["path"] = "link.md"

    write_payload(workspace, payload)

    with pytest.raises(ReportError, match=match):
        render_report(workspace, report_path(workspace))

    assert not (workspace / "report" / "index.html").exists()


def test_renderer_escapes_untrusted_text_and_preserves_sources(
    tmp_path: Path,
) -> None:
    workspace = copy_workspace(tmp_path, "minimal")
    before = snapshot_source_bytes(workspace)
    payload = load_payload(workspace)
    payload["destination"]["text"] = "<script>alert(1)</script>"
    write_payload(workspace, payload)

    index_path = render_report(workspace, report_path(workspace))
    markup = index_path.read_text(encoding="utf-8")

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in markup
    assert "<script>alert(1)</script>" not in markup
    assert 'href="../map.md"' in markup
    assert snapshot_source_bytes(workspace) == before


def test_data_must_be_below_report_directory(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "minimal")
    outside = tmp_path / "outside.json"
    shutil.copyfile(report_path(workspace), outside)

    with pytest.raises(ReportError, match="report"):
        render_report(workspace, outside)

    assert not (workspace / "report" / "index.html").exists()


def test_invalid_json_does_not_leave_partial_output(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "minimal")
    report_path(workspace).write_text("not json", encoding="utf-8")

    with pytest.raises(ReportError, match="JSON"):
        render_report(workspace, report_path(workspace))

    assert not (workspace / "report" / "index.html").exists()


def test_failed_render_preserves_previous_output(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "minimal")
    output = render_report(workspace, report_path(workspace))
    before = output.read_bytes()
    payload = load_payload(workspace)
    payload["destination"]["evidence"] = ["missing"]
    write_payload(workspace, payload)

    with pytest.raises(ReportError):
        render_report(workspace, report_path(workspace))

    assert output.read_bytes() == before


def test_render_is_deterministic_on_repeated_runs(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "minimal")

    first = render_report(workspace, report_path(workspace)).read_bytes()
    second = render_report(workspace, report_path(workspace)).read_bytes()

    assert first == second


def test_findings_are_ranked_by_impact_certainty_propagation_then_id(
    tmp_path: Path,
) -> None:
    workspace = copy_workspace(tmp_path, "dense")
    markup = render_report(workspace, report_path(workspace)).read_text()

    assert markup.index('data-finding-id="F02"') < markup.index(
        'data-finding-id="F03"'
    )
    assert markup.index('data-finding-id="F03"') < markup.index(
        'data-finding-id="F01"'
    )


def test_duplicate_finding_ids_are_rejected(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "dense")
    payload = load_payload(workspace)
    findings = payload["findings"]
    assert isinstance(findings, list)
    findings[1]["id"] = findings[0]["id"]
    write_payload(workspace, payload)

    with pytest.raises(ReportError, match="unique"):
        render_report(workspace, report_path(workspace))


def test_cli_uses_data_and_rejects_legacy_model_flag(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "minimal")

    result = subprocess.run(
        [
            sys.executable,
            str(RENDERER),
            "--workspace",
            str(workspace),
            "--data",
            str(report_path(workspace)),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (workspace / "report" / "index.html").is_file()


def test_unknown_block_kind_is_rejected_with_json_location(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "minimal")
    payload = load_payload(workspace)
    payload["sections"]["overview"]["blocks"][0]["kind"] = "unsupported"
    write_payload(workspace, payload)

    with pytest.raises(ReportError, match=r"sections\.overview\.blocks\[0\]"):
        render_report(workspace, report_path(workspace))


def test_sections_render_once_in_canonical_order(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "dense")
    markup = render_report(workspace, report_path(workspace)).read_text()
    offsets = [markup.index(f'id="{section_id}"') for section_id in SECTION_IDS]

    assert offsets == sorted(offsets)
    assert all(markup.count(f'id="{section_id}"') == 1 for section_id in SECTION_IDS)


def test_diagrams_are_evidence_backed_and_stay_in_declared_sections(
    tmp_path: Path,
) -> None:
    workspace = copy_workspace(tmp_path, "dense")
    payload = load_payload(workspace)
    diagram_blocks = [
        (section_id, block)
        for section_id, section in payload["sections"].items()
        for block in section["blocks"]
        if block["kind"] == "diagram"
    ]
    markup = render_report(workspace, report_path(workspace)).read_text()

    assert 2 <= len(diagram_blocks) <= 4
    assert len({section_id for section_id, _ in diagram_blocks}) >= 2
    assert all(block["claim"]["evidence"] for _, block in diagram_blocks)
    assert markup.count('class="diagram card"') == len(diagram_blocks)
    for section_id, block in diagram_blocks:
        section_start = markup.index(f'id="{section_id}"')
        following = [
            markup.index(f'id="{candidate}"', section_start + 1)
            for candidate in SECTION_IDS
            if f'id="{candidate}"' in markup[section_start + 1 :]
        ]
        section_end = min(following, default=len(markup))
        diagram_source = block["source"].replace("-->", "--&gt;")
        section_markup = markup[section_start:section_end]
        assert diagram_source in section_markup


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
    assert "color-scheme: light" in template_text
    assert "--accent-mid" in template_text
    assert "--warm-accent" in template_text
    assert "decision-board:has(> :only-child)" in template_text
    assert 'href="#reading"' in template_text
    assert "prefers-color-scheme: dark" not in template_text
    assert "--accent-2" not in template_text
    assert "@media print" in template_text
    assert "@media (max-width: 820px)" in template_text


def test_template_uses_only_the_generic_body_contract() -> None:
    template_text = (BUNDLE_ROOT / "templates" / "report.html").read_text(
        encoding="utf-8"
    )

    assert "${body}" in template_text
    assert "${metrics}" in template_text
    for legacy_placeholder in ("${understand}", "${review}", "${preview_attributes}"):
        assert legacy_placeholder not in template_text
    assert "template-outline" not in template_text


def test_diagram_source_stays_visible_without_javascript(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "dense")
    markup = render_report(workspace, report_path(workspace)).read_text()

    target_position = markup.index('class="diagram-target"')
    fallback_position = markup.index('class="diagram-fallback"')
    source_position = markup.index('class="diagram-source"')
    assert target_position < fallback_position < source_position
    assert '<p class="diagram-fallback">' in markup
    assert '<p class="diagram-error" role="alert" hidden>' in markup
    assert '<details class="diagram-debug">' in markup
    assert "A[Prepare] --&gt; B[Validate] --&gt; C[Cut over]" in markup
    assert 'class="diagram-source" hidden' not in markup


def test_template_never_ships_a_placeholder_integrity_value() -> None:
    template_text = (BUNDLE_ROOT / "templates" / "report.html").read_text(
        encoding="utf-8"
    )

    for match in re.finditer(r'integrity="([^"]*)"', template_text):
        assert re.fullmatch(r"sha384-[A-Za-z0-9+/]{60,}={0,2}", match.group(1))


def test_bundle_has_one_runtime_script_and_no_legacy_contract() -> None:
    scripts = sorted(path.name for path in (BUNDLE_ROOT / "scripts").glob("*.py"))

    assert scripts == ["render_report.py"]
    assert not (BUNDLE_ROOT / "references/report-model-v1.schema.json").exists()
    assert not (BUNDLE_ROOT / "templates/sample").exists()

    result = subprocess.run(
        [sys.executable, str(RENDERER), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--data" in result.stdout
    assert "--model" not in result.stdout
    assert "--preview" not in result.stdout
