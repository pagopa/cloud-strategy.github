"""Structural contract tests for the repository knowledge skill."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

BUNDLE_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = BUNDLE_ROOT / "SKILL.md"


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


def test_skill_links_every_bundle_reference() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    linked_references = set(re.findall(r"\[[^]]+\]\((references/[^)#]+)", skill_text))
    bundle_references = {
        path.relative_to(BUNDLE_ROOT).as_posix()
        for path in (BUNDLE_ROOT / "references").glob("*.md")
    }

    assert bundle_references
    assert linked_references == bundle_references


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


def test_every_evaluation_scenario_has_prompt_and_expected_fields() -> None:
    scenarios = (BUNDLE_ROOT / "evals" / "evaluation_scenarios.md").read_text(
        encoding="utf-8"
    )
    sections = re.split(r"(?m)^### ", scenarios)[1:]

    assert sections
    incomplete = [
        section.splitlines()[0]
        for section in sections
        if "**Prompt:**" not in section or "**Expected:**" not in section
    ]
    assert incomplete == []
