"""Behavior tests for the portable knowledge operating modes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


BUNDLE_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_CLI = BUNDLE_ROOT / "scripts" / "knowledge.py"


def run_cli(repo_root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(KNOWLEDGE_CLI), *arguments, "--repo-root", str(repo_root), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )


def initialize_repo(repo_root: Path) -> None:
    repo_root.mkdir()
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)


def test_audit_is_report_only(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    before = sorted(path.relative_to(repo_root) for path in repo_root.rglob("*") if ".git" not in path.parts)

    result = run_cli(repo_root, "audit")

    after = sorted(path.relative_to(repo_root) for path in repo_root.rglob("*") if ".git" not in path.parts)
    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["mode"] == "audit"
    assert report["status"] == "missing"
    assert report["findings"]
    assert before == after
    assert report["ci_assets"] == {}


def test_bootstrapped_documentation_setup_passes_audit(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    (repo_root / "docs").mkdir()
    (repo_root / "README.md").write_text("# Consumer\n", encoding="utf-8")
    (repo_root / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)

    bootstrap_result = run_cli(repo_root, "bootstrap")
    audit_result = run_cli(repo_root, "audit")

    report = json.loads(audit_result.stdout)
    assert bootstrap_result.returncode == 0
    assert audit_result.returncode == 0
    assert report["status"] == "passed"
    assert report["findings"] == []
    assert report["ci_assets"] == {}


def test_impact_reports_references_without_writing(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    (repo_root / "README.md").write_text("See docs/guide.md\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)

    result = run_cli(repo_root, "impact", "--target", "docs/guide.md")

    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["mode"] == "impact"
    assert report["references"] == {"docs/guide.md": ["README.md"]}
    assert not (repo_root / "docs").exists()


def test_update_all_requires_resupplied_allowlist(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    (repo_root / "README.md").write_text("# Consumer\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)

    result = run_cli(repo_root, "update", "--all")

    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["status"] == "approval-required"
    assert report["resolved_targets"] == ["README.md"]
    assert not (repo_root / "docs" / "knowledge-map.yaml").exists()


def test_update_writes_only_explicit_safe_target(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    (repo_root / "guide.md").write_text("# Guide\n", encoding="utf-8")

    result = run_cli(repo_root, "update", "--target", "guide.md")

    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["updated_targets"] == ["guide.md"]
    assert (repo_root / "docs" / "knowledge-map.yaml").is_file()


def test_update_never_writes_agent_policy(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    initialize_repo(repo_root)
    agents_file = repo_root / "AGENTS.md"
    agents_file.write_text("original\n", encoding="utf-8")

    result = run_cli(repo_root, "update", "--target", "AGENTS.md")

    report = json.loads(result.stdout)
    assert result.returncode == 2
    assert report["status"] == "blocked"
    assert agents_file.read_text(encoding="utf-8") == "original\n"
