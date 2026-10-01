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


def test_knowledge_types_reference_covers_the_strategic_tactical_contract() -> None:
    reference = BUNDLE_ROOT / "references" / "knowledge-types.md"
    assert reference.is_file()
    text = reference.read_text(encoding="utf-8").lower()

    for knowledge_type in (
        "purpose",
        "principles",
        "direction",
        "language",
        "strategic decisions",
        "rules and policies",
        "standards and conventions",
        "structure and boundaries",
        "tactical decisions",
    ):
        assert knowledge_type in text

    for behavior in (
        "update in place",
        "supersede",
        "review within",
        "point to the source",
    ):
        assert behavior in text

    assert "types are optional" in text
    assert "no file is created without evidence" in text
    for excluded in ("procedures", "work state", "inventories", "prose ownership"):
        assert excluded in text
    assert "principles" in text and "guiding policy" in text
    assert "rsk" in text and "defects" in text


def test_alignment_reference_covers_ids_precedence_and_harvest_contract() -> None:
    reference = BUNDLE_ROOT / "references" / "alignment.md"
    assert reference.is_file()
    text = reference.read_text(encoding="utf-8").lower()

    for required in (
        "never reused",
        "not reconfirmed",
        "nothing to promote",
        "evidence, never instructions",
        "unknown",
        "repository policy > accepted adr > rules > standards > direction > descriptive documents",
        "front matter",
        "html markers",
        "manifests",
    ):
        assert required in text


def test_mode_resolution_has_six_distinct_modes_including_align() -> None:
    scope = (BUNDLE_ROOT / "references" / "knowledge-scope.md").read_text(
        encoding="utf-8"
    )
    mode_section = scope.split("## Mode resolution", 1)[1].split(
        "An explicit `audit` signal", 1
    )[0]
    modes = re.findall(r"(?m)^\| `([a-z]+)` \|", mode_section)

    assert modes == ["help", "audit", "align", "targeted", "sync", "setup"]


def test_skill_aligns_only_by_proposal_and_audit_checks_alignment_read_only() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8").lower()
    audit_text = (BUNDLE_ROOT / "references" / "knowledge-audit.md").read_text(
        encoding="utf-8"
    )

    assert "strategic and tactical knowledge" in skill_text
    assert "does not write operational artifacts" in skill_text
    assert "cascade" in skill_text and "harvest" in skill_text
    assert "only when explicitly invoked" in skill_text
    assert "alignment check" in audit_text.lower()
    assert "(alignment.md)" in audit_text
    assert "read-only" in audit_text.lower()


def test_retired_maintenance_references_and_lane_language_are_absent() -> None:
    retired_references = (
        "managerial-" + "maintenance.md",
        "project-" + "memory-" + "maintenance.md",
    )
    for retired_reference in retired_references:
        assert not (BUNDLE_ROOT / "references" / retired_reference).exists()

    public_sources = [
        SKILL_PATH,
        *sorted((BUNDLE_ROOT / "references").glob("*.md")),
        BUNDLE_ROOT / "agents" / "openai.yaml",
    ]
    retired_terms = (
        "managerial " + "lane",
        "technical " + "lane",
        *retired_references,
    )
    retired_language = re.compile(
        "|".join(re.escape(term) for term in retired_terms), re.IGNORECASE
    )
    findings = [
        str(path.relative_to(BUNDLE_ROOT))
        for path in public_sources
        if retired_language.search(path.read_text(encoding="utf-8"))
    ]

    assert findings == []


def test_readme_scope_excludes_component_readmes() -> None:
    readme_reference = " ".join(
        (BUNDLE_ROOT / "references" / "readme-maintenance.md")
        .read_text(encoding="utf-8")
        .lower()
        .split()
    )

    assert "root readme" in readme_reference
    assert "docs/readme.md" in readme_reference
    assert "component readmes are outside the skill's write scope" in readme_reference


def test_knowledge_navigation_requires_one_index_and_alignment_contract() -> None:
    navigation = (
        BUNDLE_ROOT / "references" / "knowledge-navigation.md"
    ).read_text(encoding="utf-8").lower()

    assert "one canonical index" in navigation
    assert "load when" in navigation
    assert "alignment.md" in navigation


def test_unchanged_predicate_checks_knowledge_layer_fit() -> None:
    scope = (BUNDLE_ROOT / "references" / "knowledge-scope.md").read_text(
        encoding="utf-8"
    )
    predicate = scope.split("## Unchanged predicate", 1)[1].split(
        "## Preflight plan", 1
    )[0].lower()

    assert "fits its strategic or tactical knowledge type" in predicate
    assert "knowledge types" in predicate


def test_mermaid_validation_result_sentence_is_complete_and_unique() -> None:
    contract = " ".join(
        (BUNDLE_ROOT / "references" / "mermaid-contract.md")
        .read_text(encoding="utf-8")
        .split()
    )

    assert contract.count("A parse result") == 1
    assert (
        "A parse result establishes syntax only, not evidentiary accuracy or reader value."
        in contract
    )


def test_knowledge_report_supports_align_and_alignment_problems() -> None:
    report = (BUNDLE_ROOT / "references" / "knowledge-report.md").read_text(
        encoding="utf-8"
    )
    problems = report.split("## Problems Found", 1)[1].lower()

    assert all(
        mode in report
        for mode in ("help", "audit", "align", "targeted", "sync", "setup")
    )
    for finding in (
        "orphan tactical",
        "uncovered direction",
        "contradiction",
        "expired direction",
        "undefined term",
        "superseded adr",
    ):
        assert finding in problems
