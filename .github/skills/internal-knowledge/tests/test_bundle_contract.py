"""Structural contract tests for the authoring-only knowledge skill."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


BUNDLE_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = BUNDLE_ROOT / "SKILL.md"
AUTHORING_REFERENCES = {
    "references/adr-maintenance.md",
    "references/architecture-maintenance.md",
    "references/madr-minimal.md",
    "references/readme-maintenance.md",
}


def test_skill_frontmatter_is_portable() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(skill_text.split("---", 2)[1])

    assert set(frontmatter) <= {
        "name",
        "description",
        "metadata",
        "license",
        "compatibility",
    }
    assert frontmatter["name"] == "internal-knowledge"
    assert isinstance(frontmatter["description"], str)
    assert len(frontmatter["description"]) <= 1024


def test_skill_declares_only_authoring_references() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    linked_references = set(
        re.findall(r"\[[^]]+\]\((references/[^)]+)\)", skill_text)
    )

    assert linked_references == AUTHORING_REFERENCES
    assert all((BUNDLE_ROOT / reference).is_file() for reference in linked_references)


def test_all_bundle_markdown_links_resolve() -> None:
    missing: list[str] = []

    for markdown_path in BUNDLE_ROOT.rglob("*.md"):
        text = markdown_path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]+\]\(([^)#]+)(?:#[^)]+)?\)", text):
            if "://" in target:
                continue
            if not (markdown_path.parent / target).resolve().is_file():
                missing.append(f"{markdown_path.relative_to(BUNDLE_ROOT)} -> {target}")

    assert missing == []


def test_bundle_includes_concrete_evaluation_scenarios() -> None:
    scenarios = BUNDLE_ROOT / "evals" / "evaluation_scenarios.md"

    assert scenarios.is_file()
