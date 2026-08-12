from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE_ROOT = REPO_ROOT / ".github/skills/internal-wayfinder-report"
FIXTURES_ROOT = REPO_ROOT / "tests/github/skills/internal-wayfinder-report/fixtures"
COLLECTOR = BUNDLE_ROOT / "scripts/collect_source_notes.py"


def copy_workspace(tmp_path: Path, name: str) -> Path:
    source = FIXTURES_ROOT / name
    workspace = tmp_path / name
    shutil.copytree(source, workspace)
    return workspace


def snapshot_source_bytes(workspace: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(workspace): path.read_bytes()
        for path in sorted(workspace.rglob("*"))
        if path.is_file() and "report" not in path.relative_to(workspace).parts
    }


def run_collector(
    workspace: Path, max_preview_lines: int = 2
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(COLLECTOR),
            "--workspace",
            str(workspace),
            "--format",
            "json",
            "--max-preview-lines",
            str(max_preview_lines),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_dense_inventory_is_sorted_structural_and_bounded(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "dense")

    result = run_collector(workspace)

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    sources = payload["sources"]
    paths = [item["path"] for item in sources]
    assert paths == sorted(paths)
    assert set(paths) == {
        "analysis.md",
        "issues/01-decision.md",
        "issues/02-dependency.md",
        "map.md",
    }
    assert all("report/" not in path for path in paths)

    expected_headings = {
        "analysis.md": "Dense Analysis",
        "issues/01-decision.md": "Decision 01",
        "issues/02-dependency.md": "Dependency 02",
        "map.md": "Dense Map",
    }
    for item in sources:
        path = workspace / item["path"]
        source_text = path.read_text(encoding="utf-8")
        assert item["bytes"] == path.stat().st_size
        assert item["lines"] == len(source_text.splitlines(keepends=True))
        assert item["headings"] == [
            {"line": 1, "text": expected_headings[item["path"]]}
        ]
        assert [window["heading"] for window in item["windows"]] == [
            expected_headings[item["path"]]
        ]
        assert all(len(window["lines"]) <= 2 for window in item["windows"])
        assert item["windows"][0]["start_line"] == 1
        assert item["windows"][0]["lines"][0] == f"# {expected_headings[item['path']]}"


@pytest.mark.parametrize(
    "missing", ["map.md", "analysis.md", "issues", "report/report.json"]
)
def test_missing_required_paths_fail_with_bounded_error(
    tmp_path: Path, missing: str
) -> None:
    workspace = copy_workspace(tmp_path, "minimal")
    missing_path = workspace / missing
    if missing == "issues":
        shutil.rmtree(missing_path)
    else:
        missing_path.unlink()

    result = run_collector(workspace)

    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr
    assert len(result.stderr) <= 240
    assert "Traceback" not in result.stderr


def test_outside_symlink_is_rejected_without_source_leak(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "minimal")
    outside = tmp_path / "outside.md"
    outside.write_text("secret source body must not leak\n", encoding="utf-8")
    (workspace / "issues" / "outside.md").symlink_to(outside)

    result = run_collector(workspace)

    assert result.returncode != 0
    assert "secret source body must not leak" not in result.stdout
    assert "secret source body must not leak" not in result.stderr


def test_helper_preserves_source_bytes(tmp_path: Path) -> None:
    workspace = copy_workspace(tmp_path, "dense")
    before = snapshot_source_bytes(workspace)

    result = run_collector(workspace)

    assert result.returncode == 0
    assert snapshot_source_bytes(workspace) == before
