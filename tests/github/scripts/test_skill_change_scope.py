from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
sys.path.insert(0, str(REPO_ROOT / ".github/scripts"))

from lib.skill_change_scope import (  # noqa: E402
    collect_changed_paths,
    detect_protected_skill_changes,
    protected_skill_bundle,
    validate_allowlist,
)


def test_protected_skill_bundle_classifies_direct_skill_descendants() -> None:
    assert protected_skill_bundle(".github/skills/internal-python/SKILL.md") is None
    assert protected_skill_bundle(".github/skills/local-sync-repos/SKILL.md") is None
    assert (
        protected_skill_bundle(".github/skills/mattpocock-tdd/SKILL.md")
        == ".github/skills/mattpocock-tdd"
    )
    assert (
        protected_skill_bundle(".github/skills/grill-me/SKILL.md")
        == ".github/skills/grill-me"
    )
    assert protected_skill_bundle(".github/skills/grill-me") is None
    assert protected_skill_bundle(".github/other/grill-me/SKILL.md") is None
    assert protected_skill_bundle(".github/skills/../grill-me/SKILL.md") is None


@pytest.mark.parametrize(
    "entry",
    [
        ".github/skills",
        ".github/skills/grill-me/SKILL.md",
        "/workspace/.github/skills/grill-me",
        "../.github/skills/grill-me",
        ".github/skills/grill-*",
        ".github/skills/internal-python",
        ".github/skills/local-sync-repos",
    ],
)
def test_validate_allowlist_rejects_non_exact_protected_bundle(entry: str) -> None:
    with pytest.raises(ValueError):
        validate_allowlist([entry])


def test_validate_allowlist_returns_exact_protected_bundle_paths() -> None:
    assert validate_allowlist(
        [
            ".github/skills/grill-me",
            ".github/skills/mattpocock-tdd",
            ".github/skills/grill-me",
        ]
    ) == (".github/skills/grill-me", ".github/skills/mattpocock-tdd")


def test_detect_protected_skill_changes_requires_exact_allowlist() -> None:
    changed = [
        ".github/skills/grill-me/SKILL.md",
        ".github/skills/internal-python/SKILL.md",
        ".github/skills/local-sync-repos/SKILL.md",
    ]

    findings = detect_protected_skill_changes(changed, [])
    assert [finding.code for finding in findings] == ["protected-skill-change"]
    assert findings[0].severity == "blocking"
    assert findings[0].path == ".github/skills/grill-me"

    assert (
        detect_protected_skill_changes(
            changed,
            [".github/skills/grill-me"],
        )
        == []
    )


def _run_git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def test_collect_changed_paths_includes_worktree_and_base_ref_changes(
    tmp_path: Path,
) -> None:
    _run_git(tmp_path, "init", "-q")

    def _run_git_git(*args: str) -> None:
        _run_git(tmp_path, *args)

    _run_git_git("config", "user.email", "tests@example.com")
    _run_git_git("config", "user.name", "Skill scope tests")

    tracked = tmp_path / ".github/skills/grill-me/SKILL.md"
    tracked.parent.mkdir(parents=True)
    tracked.write_text("base\n", encoding="utf-8")
    deleted = tmp_path / ".github/skills/grill-me/DELETED.md"
    deleted.write_text("delete me\n", encoding="utf-8")
    _run_git_git("add", ".")
    _run_git_git("commit", "-q", "-m", "base")
    base_ref = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    tracked.write_text("committed\n", encoding="utf-8")
    _run_git_git("add", str(tracked.relative_to(tmp_path)))
    _run_git_git("commit", "-q", "-m", "committed change")

    renamed = tmp_path / ".github/skills/grill-me/RENAMED.md"
    tracked.rename(renamed)
    deleted.unlink()
    _run_git_git("add", "-u")

    unstaged = tmp_path / ".github/skills/grill-me/UNSTAGED.md"
    unstaged.write_text("unstaged\n", encoding="utf-8")
    untracked = tmp_path / ".github/skills/grill-me/UNTRACKED.md"
    untracked.write_text("untracked\n", encoding="utf-8")

    changed = set(collect_changed_paths(tmp_path, base_ref=base_ref))
    assert ".github/skills/grill-me/SKILL.md" in changed
    assert ".github/skills/grill-me/RENAMED.md" in changed
    assert ".github/skills/grill-me/DELETED.md" in changed
    assert ".github/skills/grill-me/UNSTAGED.md" in changed
    assert ".github/skills/grill-me/UNTRACKED.md" in changed
