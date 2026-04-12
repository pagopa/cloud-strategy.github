from __future__ import annotations

from pathlib import Path

import pytest
from lib.shared import (Finding, all_files_under, dedupe_preserve_order,
                        find_repo_root, finding_sort_key,
                        is_consumer_sync_excluded_path, is_local_asset,
                        path_list, resolve_markdown_target, split_frontmatter,
                        strip_frontmatter)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_split_frontmatter_and_strip_frontmatter_return_expected_parts() -> None:
    text = "---\nname: demo\nitems:\n  - one\n---\nBody\n"

    frontmatter, body = split_frontmatter(text)

    assert frontmatter == {"name": "demo", "items": ["one"]}
    assert body == "Body\n"
    assert strip_frontmatter(text) == "Body\n"


def test_split_frontmatter_returns_empty_mapping_for_invalid_yaml() -> None:
    text = "---\nname: [broken\n---\nBody\n"

    frontmatter, body = split_frontmatter(text)

    assert frontmatter == {}
    assert body == "Body\n"


@pytest.mark.parametrize(
    ("relative_path", "is_local", "is_excluded"),
    [
        (".github/agents/local-helper.agent.md", True, False),
        (".github/skills/local-demo/SKILL.md", True, False),
        (".github/agents/internal-sync-helper.agent.md", False, True),
        (".github/skills/internal-demo/agents/internal-sync-helper.yaml", False, True),
        ("docs/readme.md", False, False),
    ],
)
def test_local_and_consumer_excluded_path_helpers(
    relative_path: str, is_local: bool, is_excluded: bool
) -> None:
    assert is_local_asset(relative_path) is is_local
    assert is_consumer_sync_excluded_path(relative_path) is is_excluded


def test_find_repo_root_and_resolve_markdown_target(tmp_path: Path) -> None:
    root = tmp_path
    current_file = root / ".github/agents/internal-router.agent.md"
    (root / ".github/agents").mkdir(parents=True, exist_ok=True)
    (root / "docs").mkdir(parents=True, exist_ok=True)
    current_file.write_text("# router\n", encoding="utf-8")

    assert find_repo_root(root / "nested" / "deeper") == root
    assert (
        resolve_markdown_target(root, current_file, "AGENTS.md") == root / "AGENTS.md"
    )
    assert (
        resolve_markdown_target(root, current_file, ".github/copilot-instructions.md")
        == root / ".github/copilot-instructions.md"
    )
    assert (
        resolve_markdown_target(root, current_file, "../README.md#usage")
        == (root / ".github/README.md").resolve()
    )
    assert resolve_markdown_target(root, current_file, "https://example.com") is None
    assert resolve_markdown_target(root, current_file, "/absolute/path.md") is None


def test_all_files_under_path_list_and_dedupe_preserve_order(tmp_path: Path) -> None:
    root = tmp_path
    write_file(root / ".github/agents/internal-fast.agent.md", "# fast\n")
    write_file(root / ".github/agents/README.md", "# ignored\n")
    write_file(root / ".github/agents/__pycache__/cache.pyc", "")
    write_file(root / ".github/agents/local-helper.agent.md", "# local\n")

    assert all_files_under(root, ".github/agents") == [
        ".github/agents/internal-fast.agent.md",
        ".github/agents/local-helper.agent.md",
    ]
    assert path_list(root, ".github/agents/*.agent.md") == [
        ".github/agents/internal-fast.agent.md",
        ".github/agents/local-helper.agent.md",
    ]
    assert dedupe_preserve_order(["one", "two", "one", "three", "two"]) == [
        "one",
        "two",
        "three",
    ]


def test_finding_sort_key_orders_blocking_findings_before_non_blocking() -> None:
    findings = [
        Finding("non-blocking", "z-code", "b.md", "message", "suggestion"),
        Finding("blocking", "a-code", "a.md", "message", "suggestion"),
    ]

    ordered = sorted(findings, key=finding_sort_key)

    assert ordered[0].severity == "blocking"
    assert ordered[0].path == "a.md"
