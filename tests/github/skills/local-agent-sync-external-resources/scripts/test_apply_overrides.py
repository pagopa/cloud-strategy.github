import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = (
    REPO_ROOT / ".github/skills/local-agent-sync-external-resources/scripts"
)
sys.path.insert(0, SCRIPT_DIR.as_posix())

from apply_imported_asset_overrides import (  # noqa: E402
    load_registry,
    select_overrides,
    detect_patch_status,
)


def test_load_registry_validates_required_fields(tmp_path: Path) -> None:
    registry = tmp_path / "registry.yaml"
    registry.write_text(
        "overrides:\n"
        "  - id: test\n"
        "    patch_path: patches/test.patch\n"
        "    target_path: .github/skills/test/SKILL.md\n"
        "    apply_strategy: git-apply\n"
        "    expected_content_hash: abc123\n",
        encoding="utf-8",
    )
    result = load_registry(registry)
    assert len(result) == 1
    assert result[0]["id"] == "test"


def test_load_registry_rejects_non_list_overrides(tmp_path: Path) -> None:
    registry = tmp_path / "registry.yaml"
    registry.write_text("overrides: not-a-list\n", encoding="utf-8")
    with pytest.raises(ValueError, match="overrides list"):
        load_registry(registry)


def test_load_registry_rejects_non_mapping_entries(tmp_path: Path) -> None:
    registry = tmp_path / "registry.yaml"
    registry.write_text("overrides:\n  - just-a-string\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        load_registry(registry)


def test_select_overrides_filters_by_id() -> None:
    overrides = [
        {"id": "a", "patch_path": "a.patch"},
        {"id": "b", "patch_path": "b.patch"},
    ]
    assert len(select_overrides(overrides, ["a"])) == 1
    assert select_overrides(overrides, None) == overrides


def test_detect_patch_status_returns_conflict_for_bad_patch(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo_root, check=True, timeout=10)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo_root, check=True, timeout=10)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo_root, check=True, timeout=10)
    (repo_root / "file.txt").write_text("content\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, timeout=10)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=repo_root, check=True, timeout=10)

    bad_patch = tmp_path / "bad.patch"
    bad_patch.write_text(
        "--- a/nonexistent.txt\n+++ b/nonexistent.txt\n@@ -1 +1 @@\n-old\n+new\n",
        encoding="utf-8",
    )

    status = detect_patch_status(repo_root, bad_patch)
    assert status == "conflict"
