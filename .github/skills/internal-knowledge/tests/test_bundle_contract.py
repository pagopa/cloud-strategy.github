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
    "references/knowledge-scope.md",
    "references/knowledge-topology.md",
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


def test_readme_reference_keeps_omission_reporting_discipline() -> None:
    reference = (BUNDLE_ROOT / "references" / "readme-maintenance.md").read_text(
        encoding="utf-8"
    )

    assert reference.count("omitted-with-reason") == 3
    assert "omit it silently" not in reference


def test_skill_resolves_one_mode_before_writing() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    for mode in ("`help`", "`targeted`", "`refresh`", "`bootstrap`"):
        assert mode in skill_text
    assert "never installs a check" in skill_text
    assert "enforcement gap" in skill_text


def test_scope_reference_keeps_write_gates_mechanical() -> None:
    reference = (BUNDLE_ROOT / "references" / "knowledge-scope.md").read_text(
        encoding="utf-8"
    )

    for section in (
        "## Mode resolution",
        "## Help mode",
        "## Layout declaration and drift",
        "## Write allowlist",
        "## Unchanged predicate",
        "## Preflight plan",
        "## Waves",
        "## Enforcement gap",
    ):
        assert section in reference
    assert "at most ten authored documents" in reference
    assert "`help` ends with the proposed prompt" in reference


def test_topology_reference_keeps_documentation_mode_anti_scope() -> None:
    reference = (BUNDLE_ROOT / "references" / "knowledge-topology.md").read_text(
        encoding="utf-8"
    )

    assert "Never create empty mode directories" in reference
    assert "Never add a documentation-mode field" in reference
    assert "Never propose a check that enforces documentation modes" in reference
    assert "none evidenced" in reference
