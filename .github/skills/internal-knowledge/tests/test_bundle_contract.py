"""Structural contract tests for the repository knowledge skill."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

BUNDLE_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = BUNDLE_ROOT / "SKILL.md"
BUNDLE_REFERENCES = {
    "references/adr-maintenance.md",
    "references/architecture-maintenance.md",
    "references/knowledge-audit.md",
    "references/knowledge-scope.md",
    "references/knowledge-topology.md",
    "references/madr-minimal.md",
    "references/managerial-maintenance.md",
    "references/project-memory-maintenance.md",
    "references/readme-maintenance.md",
    "references/standards-maintenance.md",
}


def read_bundle_text(relative_path: str) -> str:
    return (BUNDLE_ROOT / relative_path).read_text(encoding="utf-8")


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

    assert linked_references == BUNDLE_REFERENCES
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


def test_architecture_reference_is_reader_proportional() -> None:
    reference = read_bundle_text("references/architecture-maintenance.md")

    assert "Use only the sections needed for the stated reader outcome" in reference
    assert "Do not create empty sections" in reference
    assert "Use exactly these level-two headings in this order" not in reference


def test_readme_reference_does_not_require_diagram_boilerplate() -> None:
    reference = read_bundle_text("references/readme-maintenance.md")

    assert "Use Mermaid only when at least three material evidenced relationships" in reference
    assert "No diagram is provided" not in reference
    assert "a README carrying neither outcome is incomplete" not in reference


def test_standards_reference_classifies_by_semantics_not_enforcement() -> None:
    reference = read_bundle_text("references/standards-maintenance.md")

    assert "Automated enforcement does not change the semantic category" in reference
    assert "move it to the `RULES.md`" not in reference


def test_guides_cover_evidenced_reader_work_beyond_declaration_effects() -> None:
    reference = read_bundle_text("references/standards-maintenance.md")

    assert "task, recovery, troubleshooting" in reference
    assert "One guide per evidenced reader journey" in reference


def test_skill_projection_names_one_detailed_contract_owner() -> None:
    skill = read_bundle_text("SKILL.md")

    assert "one detailed owner" in skill
    assert "material omission" in skill
    assert "targeted" in skill
    assert "self-contained" in skill


def test_public_prompt_projects_scope_without_host_dependencies() -> None:
    payload = yaml.safe_load(read_bundle_text("agents/openai.yaml"))
    prompt = payload["interface"]["default_prompt"]

    for anchor in (
        "five modes",
        "help",
        "audit",
        "targeted",
        "sync",
        "setup",
        "read-only",
        "selective durable",
        "one detailed owner",
        "enforcement gap",
        "common core",
        "technical lane",
        "managerial lane",
        "authoring choice",
        "not a runtime profile",
        "proposal",
        "accepted decision",
        "current implementation",
        "observed outcome",
        "bounded handoff",
        "instruction owner",
        "self-contained vocabulary",
        "README index",
        "generated files",
        "historical records",
    ):
        assert anchor in prompt
    for retired_or_host_specific in (
        "knowledge-map.yaml",
        "docs/knowledge-components.txt",
        ".github/actions/",
        "two signals make promotion the default",
        "one Mermaid topology diagram",
    ):
        assert retired_or_host_specific not in prompt
    assert "/Users/" not in prompt
    assert "../" not in prompt


def test_evaluations_cover_the_public_contract_projection() -> None:
    scenarios = read_bundle_text("evals/evaluation_scenarios.md")

    assert "### Keep public projections aligned" in scenarios
    assert "one detailed owner" in scenarios
    assert "host-specific" in scenarios


def test_lane_scenarios_have_standalone_prompts_and_expected_boundaries() -> None:
    scenarios = read_bundle_text("evals/evaluation_scenarios.md")

    for heading in (
        "### Standalone technical setup",
        "### Standalone managerial setup",
        "### Mixed-lane realignment",
        "### Route a missing instruction owner",
        "### Keep proposal and approval separate",
        "### Keep public projections aligned across lanes",
    ):
        start = scenarios.index(heading)
        section = scenarios[start : scenarios.find("\n### ", start + len(heading))]
        assert "**Prompt:**" in section
        assert "**Expected:**" in section

    assert "without importing host manifests or paths" in scenarios
    assert "without a host repository, host manifest, host script" in scenarios
    assert "without host dependencies" in scenarios
    assert "never auto-promote" in scenarios


def test_readme_reference_guards_generated_block_interaction() -> None:
    reference = (BUNDLE_ROOT / "references" / "readme-maintenance.md").read_text(
        encoding="utf-8"
    )

    assert "go before the opening marker of a generated block" in reference
    assert "still collecting the anchors they define" in reference
    assert "replacing each whitespace character, not each run of them" in reference


def test_skill_resolves_one_mode_before_writing() -> None:
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    for mode in ("`help`", "`audit`", "`targeted`", "`sync`", "`setup`"):
        assert mode in skill_text
    assert "audit` when it explicitly asks" in skill_text
    assert "before interpreting any named path" in skill_text
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
    assert "coherent batch" in reference
    assert "not a fixed quota" in reference
    assert "The ceiling is not a target" in reference
    assert "`help` ends with the proposed prompt" in reference


def test_topology_reference_keeps_documentation_mode_anti_scope() -> None:
    reference = (BUNDLE_ROOT / "references" / "knowledge-topology.md").read_text(
        encoding="utf-8"
    )

    assert "Never create empty mode directories" in reference
    assert "Never add a documentation-mode field" in reference
    assert "Never propose a check that enforces documentation modes" in reference
    assert "none evidenced" in reference


def test_targeted_scope_has_no_implicit_root_write() -> None:
    scope = read_bundle_text("references/knowledge-scope.md")

    assert "In `targeted`, the allowlist is the normalized set of user-supplied destinations." in scope
    assert "The layout root document is the single exception in `targeted`" not in scope


def test_unchanged_requires_the_stated_reader_outcome() -> None:
    scope = read_bundle_text("references/knowledge-scope.md")

    assert "material omission" in scope
    assert "no material addition for its stated reader outcome" in scope


def test_scope_accepts_considered_not_evidenced_without_creating_an_artifact() -> None:
    topology = read_bundle_text("references/knowledge-topology.md")

    assert "considered, not evidenced" in topology
    assert "never create an artifact merely to satisfy a row" in topology


def test_topology_promotion_requires_a_semantic_or_ownership_boundary() -> None:
    topology = read_bundle_text("references/knowledge-topology.md")

    assert "distinct ubiquitous language" in topology
    assert "bounded context" in topology
    assert "decoupled team ownership" in topology
    assert "two signals make promotion the default" not in topology


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
    assert "diagram only when it improves comprehension" in skill_text


def test_evals_cover_under_delivery_branches() -> None:
    scenarios = (BUNDLE_ROOT / "evals" / "evaluation_scenarios.md").read_text(
        encoding="utf-8"
    )

    for heading in (
        "### Resist domain promotion from tooling differences",
        "### Discover a standard and a principle during setup",
        "### Author a component README with a diagram",
        "### Justify a wave below the ceiling",
        "### Keep a short README proportional",
        "### Extend an existing document for a material omission",
        "### Keep a standard semantic when a check is added",
        "### Guide a recovery or troubleshooting task",
        "### Keep architecture structure proportional",
        "### Keep public projections aligned",
        "### Check ownership before excluding a managed path",
        "### Update only the docs bucket",
        "### Update only the README bucket",
        "### Stop when sync means the sync contract",
        "### Re-run setup when drift reappears",
        "### Map the old mode vocabulary to the new one",
    ):
        assert heading in scenarios


def test_evaluations_cover_audit_memory_and_projection_cases() -> None:
    scenarios = read_bundle_text("evals/evaluation_scenarios.md")

    for heading in (
        "### Audit an explicit file without authoring",
        "### Report partial audit coverage",
        "### Keep semantic contradictions as findings",
        "### Retain selective project memory",
        "### Audit a README-only request without authoring",
        "### Keep public projections aligned",
        "### Keep a short README proportional",
        "### Keep architecture structure proportional",
        "### Keep a standard semantic when a check is added",
    ):
        assert heading in scenarios

    assert "an enforced convention is a rule, not a standard" not in scenarios


def test_bundle_owners_keep_audit_and_memory_contracts_local() -> None:
    audit = read_bundle_text("references/knowledge-audit.md")
    memory = read_bundle_text("references/project-memory-maintenance.md")

    for phrase in (
        "bounded",
        "read-only",
        "actual coverage",
        "exclusions",
        "unknown",
        "did not persist a report",
    ):
        assert phrase in audit
    for phrase in (
        "canonical owner",
        "approved",
        "historical",
        "implementation-complete",
        "backlog",
        "automatic promotion",
    ):
        assert phrase in memory


def test_cross_file_contract_preserves_reference_boundaries() -> None:
    standards = read_bundle_text("references/standards-maintenance.md")
    architecture = read_bundle_text("references/architecture-maintenance.md")
    readme = read_bundle_text("references/readme-maintenance.md")
    adr = read_bundle_text("references/adr-maintenance.md")
    skill = read_bundle_text("SKILL.md")

    assert "Automated enforcement does not change the semantic category" in standards
    assert "Use only the sections needed for the stated reader outcome" in architecture
    assert "Use Mermaid only when at least three material evidenced relationships" in readme
    assert "accepted ADR bodies" in skill
    assert "accepted ADR body is immutable" in adr
    assert "generated block byte-for-byte" in readme


def test_skill_defines_common_core_and_two_authoring_lanes() -> None:
    skill = read_bundle_text("SKILL.md")
    topology = read_bundle_text("references/knowledge-topology.md")
    managerial_path = BUNDLE_ROOT / "references" / "managerial-maintenance.md"
    assert managerial_path.is_file()
    managerial = managerial_path.read_text(encoding="utf-8")

    for phrase in (
        "common core",
        "technical lane",
        "managerial lane",
        "lane choice is an authoring choice",
    ):
        assert phrase in skill
    for phrase in (
        "README index",
        "project orientation",
        "roadmap",
        "maintenance route",
        "evidence-backed technical extension",
    ):
        assert phrase in topology
    assert "purpose, priorities, initiatives, proposals, and observed outcomes" in managerial


def test_lane_selection_is_not_a_runtime_profile() -> None:
    skill = read_bundle_text("SKILL.md")
    topology = read_bundle_text("references/knowledge-topology.md")

    assert "not a runtime profile" in skill
    assert "Never add a profile field" in topology
    assert "Never create a profile directory" in topology
    assert "Never create a profile registry" in topology


def test_managerial_contract_preserves_proposal_and_approval_states() -> None:
    managerial_path = BUNDLE_ROOT / "references" / "managerial-maintenance.md"
    assert managerial_path.is_file()
    managerial = managerial_path.read_text(encoding="utf-8")

    for phrase in (
        "proposal",
        "accepted decision",
        "current implementation",
        "observed outcome",
        "must not auto-promote",
    ):
        assert phrase in managerial


def test_missing_instruction_routes_use_a_bounded_owner_handoff() -> None:
    audit = read_bundle_text("references/knowledge-audit.md")
    managerial_path = BUNDLE_ROOT / "references" / "managerial-maintenance.md"
    assert managerial_path.is_file()
    managerial = managerial_path.read_text(encoding="utf-8")

    assert "bounded handoff" in audit
    assert "instruction owner" in audit
    assert "report the gap before complete setup" in managerial


def test_coherent_batches_do_not_use_a_fixed_ten_document_quota() -> None:
    scope = read_bundle_text("references/knowledge-scope.md")

    assert "coherent batch" in scope
    assert "ten-document ceiling" in scope
    assert "not a fixed quota" in scope


def test_topology_distinguishes_indexes_extensions_generated_and_history() -> None:
    topology = read_bundle_text("references/knowledge-topology.md")
    readme = read_bundle_text("references/readme-maintenance.md")

    assert "README index" in topology
    assert "legitimate extension" in topology
    assert "generated files" in topology
    assert "historical records" in topology
    assert "preserve generated blocks" in readme


def test_evaluations_cover_lane_setup_alignment_audit_and_proposals() -> None:
    scenarios = read_bundle_text("evals/evaluation_scenarios.md")

    for heading in (
        "### Standalone technical setup",
        "### Standalone managerial setup",
        "### Mixed-lane realignment",
        "### Route a missing instruction owner",
        "### Keep proposal and approval separate",
        "### Keep public projections aligned across lanes",
    ):
        assert heading in scenarios
