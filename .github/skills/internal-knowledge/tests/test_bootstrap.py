"""Behavior tests for portable bootstrap output."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml


BUNDLE_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP = BUNDLE_ROOT / "scripts" / "bootstrap.py"


def run_bootstrap(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BOOTSTRAP), "--repo-root", str(repo_root)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_bootstrap_derives_manifest_from_target_repository(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    (repo_root / "docs").mkdir(parents=True)
    (repo_root / "README.md").write_text("# Consumer\n", encoding="utf-8")
    (repo_root / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)

    result = run_bootstrap(repo_root)

    assert result.returncode == 0, result.stderr
    manifest = yaml.safe_load(
        (repo_root / "docs" / "knowledge-map.yaml").read_text(encoding="utf-8")
    )
    paths = {component["path"] for component in manifest["components"]}
    assert "README.md" in paths
    assert "docs/guide.md" in paths
    assert "docs/aws.md" not in paths
    assert all(component.get("why") and component.get("owner") for component in manifest["components"])


def test_bootstrap_does_not_emit_action_assets(tmp_path: Path) -> None:
    repo_root = tmp_path / "consumer"
    repo_root.mkdir()

    result = run_bootstrap(repo_root)

    assert result.returncode == 0, result.stderr
    assert not (repo_root / ".github" / "actions" / "knowledge-check").exists()
    assert result.stdout.strip().splitlines() == [
        str(repo_root / "docs" / "knowledge-map.yaml")
    ]
