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
    "references/standards-maintenance.md",
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


def test_readme_reference_makes_the_diagram_disposition_exhaustive() -> None:
    reference = (BUNDLE_ROOT / "references" / "readme-maintenance.md").read_text(
        encoding="utf-8"
    )

    assert "the two outcomes are exhaustive" in reference
    assert "`No diagram is provided`" in reference
    assert "carrying neither outcome is incomplete" in reference
    assert "parsing it offline when no renderer is reachable" in reference


def test_readme_reference_guards_generated_block_interaction() -> None:
    reference = (BUNDLE_ROOT / "references" / "readme-maintenance.md").read_text(
        encoding="utf-8"
    )

    assert "go before the opening marker of a generated block" in reference
    assert "still collecting the anchors they define" in reference
    assert "replacing each whitespace character, not each run of them" in reference


def test_skill_resolves_one_mode_before_writing() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    for mode in ("`help`", "`targeted`", "`sync`", "`setup`"):
        assert mode in skill_text
    assert "bucket" in skill_text
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


def test_topology_binds_the_promotion_threshold() -> None:
    reference = (BUNDLE_ROOT / "references" / "knowledge-topology.md").read_text(
        encoding="utf-8"
    )

    assert "two signals make promotion the default" in reference
    assert "Relative size is not a signal" in reference
    assert "The plan accounts for every row" in reference


def test_scope_defines_the_bucket_mechanism() -> None:
    reference = (BUNDLE_ROOT / "references" / "knowledge-scope.md").read_text(
        encoding="utf-8"
    )

    assert "## Buckets" in reference
    assert "classified by file name" in reference
    assert "outside the requested bucket" in reference
    assert "is not a sync contract over managed copies" in reference
    assert "escalation inherits the requested bucket" in reference
    assert "never starts a layout migration" in reference
    assert "not only on first use" in reference
    assert "is shape and escalates" in reference


def test_scope_extends_omission_discipline_beyond_directories() -> None:
    reference = (BUNDLE_ROOT / "references" / "knowledge-scope.md").read_text(
        encoding="utf-8"
    )

    assert "every row of the evidence table" in reference
    assert "Silent omission is a defect" in reference
    assert "The ceiling is not a target" in reference


def test_scope_keeps_waves_from_partitioning_obligations() -> None:
    reference = (BUNDLE_ROOT / "references" / "knowledge-scope.md").read_text(
        encoding="utf-8"
    )

    assert "partitions documents, never the obligations" in reference
    assert "each wave looked finished on its own" in reference


def test_scope_requires_ownership_evidence_and_non_vacuous_counts() -> None:
    reference = (BUNDLE_ROOT / "references" / "knowledge-scope.md").read_text(
        encoding="utf-8"
    )

    assert "A directory pattern is not evidence of ownership" in reference
    assert "as counts, not as a verdict" in reference
    assert "compatible with having checked nothing" in reference


def test_topology_enumerates_signals_before_the_layout_decision() -> None:
    reference = (BUNDLE_ROOT / "references" / "knowledge-topology.md").read_text(
        encoding="utf-8"
    )

    assert "Enumerate that list explicitly" in reference
    assert "before the layout is selected" in reference
    assert "enumeration precedes the ADR" in reference


def test_skill_loads_authoring_references_before_the_plan() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "before drafting the plan" in skill_text
    assert "Mermaid topology diagram" in skill_text


def test_evals_cover_under_delivery_branches() -> None:
    scenarios = (BUNDLE_ROOT / "evals" / "evaluation_scenarios.md").read_text(
        encoding="utf-8"
    )

    for heading in (
        "### Promote a domain the evidence supports",
        "### Discover a standard and a principle during setup",
        "### Author a component README with a diagram",
        "### Justify a wave below the ceiling",
        "### Resolve the diagram disposition of every authored README",
        "### Check ownership before excluding a managed path",
        "### Update only the docs bucket",
        "### Update only the README bucket",
        "### Stop when sync means the sync contract",
        "### Re-run setup when drift reappears",
        "### Map the old mode vocabulary to the new one",
    ):
        assert heading in scenarios
