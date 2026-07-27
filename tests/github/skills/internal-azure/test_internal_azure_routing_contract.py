import re
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_DIR = REPO_ROOT / ".github/skills/internal-azure"
STRATEGIC_SKILL_DIR = REPO_ROOT / ".github/skills/internal-azure-strategic"
SKILL_PATH = SKILL_DIR / "SKILL.md"
AGENT_PATH = SKILL_DIR / "agents/openai.yaml"
ROUTING_MATRIX_PATH = SKILL_DIR / "references/routing-matrix.md"
STRATEGIC_SKILL_PATH = STRATEGIC_SKILL_DIR / "SKILL.md"
STRATEGIC_AGENT_PATH = STRATEGIC_SKILL_DIR / "agents/openai.yaml"
LENS_PLAYBOOK_PATH = STRATEGIC_SKILL_DIR / "references/lens-playbook.md"

DIRECT_SPECIALISTS = {
    "internal-azure-organization-structure",
    "internal-azure-governance",
    "internal-azure-operations",
    "internal-azure-devops",
    "internal-azure-strategic",
}

FORBIDDEN_SPECIALIST_LANGUAGE = (
    "handoff",
    "route back",
    "when not to use",
    "do not use",
    "outside this lane",
)


def assert_reach_only_specialist(skill_id: str) -> None:
    path = REPO_ROOT / ".github/skills" / skill_id / "SKILL.md"
    frontmatter = load_frontmatter(path)
    assert "disable-model-invocation" not in frontmatter
    assert frontmatter["description"].startswith("Use when /internal-azure ")
    bundle_text = "\n".join(
        candidate.read_text()
        for candidate in [path, *sorted(path.parent.glob("references/*.md"))]
    ).lower()
    for phrase in FORBIDDEN_SPECIALIST_LANGUAGE:
        assert phrase not in bundle_text

def load_frontmatter(path: Path) -> dict[str, object]:
    _, raw_frontmatter, _ = path.read_text().split("---", maxsplit=2)
    return yaml.safe_load(raw_frontmatter)


def test_internal_azure_router_is_the_unflagged_entry_point() -> None:
    assert SKILL_PATH.is_file()
    frontmatter = load_frontmatter(SKILL_PATH)
    assert frontmatter["name"] == "internal-azure"
    assert "Azure platform" in frontmatter["description"]
    assert "any Azure task" not in frontmatter["description"]


def test_router_invokes_direct_specialists() -> None:
    text = SKILL_PATH.read_text()
    for skill_id in DIRECT_SPECIALISTS:
        assert f"/{skill_id}" in text
    assert "reading the chosen skill" not in text.lower()
    assert "disable-model-invocation" not in text
    assert "handoff" not in text.lower()


def test_router_is_platform_scoped_and_deliverable_driven() -> None:
    skill_text = SKILL_PATH.read_text()
    assert "Azure platform" in skill_text
    assert "immediate deliverable" in skill_text


def test_organization_structure_is_reach_only_and_workflow_ordered() -> None:
    assert_reach_only_specialist("internal-azure-organization-structure")
    skill_text = (
        REPO_ROOT
        / ".github/skills/internal-azure-organization-structure/SKILL.md"
    ).read_text().lower()
    markers = (
        "azure objective",
        "placement choice",
        "rollout unit",
        "validation conditions",
    )
    positions = [skill_text.index(marker) for marker in markers]
    assert positions == sorted(positions)


def test_governance_is_reach_only_and_workflow_complete() -> None:
    assert_reach_only_specialist("internal-azure-governance")
    skill_text = (
        REPO_ROOT / ".github/skills/internal-azure-governance/SKILL.md"
    ).read_text().lower()
    for marker in (
        "governance objective",
        "control scope",
        "authorization",
        "exception",
        "rollout",
        "completion criteria",
    ):
        assert marker in skill_text

    reference_text = (
        REPO_ROOT / ".github/skills/internal-azure-governance/references/guardrail-map.md"
    ).read_text().lower()
    assert "preventive" in reference_text
    assert "detective" in reference_text
    assert "authorization" in reference_text
    assert "workload identity" in reference_text


def test_operations_is_reach_only_and_evidence_workflow_ordered() -> None:
    assert_reach_only_specialist("internal-azure-operations")
    skill_text = (
        REPO_ROOT / ".github/skills/internal-azure-operations/SKILL.md"
    ).read_text().split("---", maxsplit=2)[2].lower()
    markers = (
        "operational objective",
        "evidence state",
        "rollout unit",
        "preflight",
        "observation signals",
        "recovery proof",
        "completion criteria",
    )
    positions = [skill_text.index(marker) for marker in markers]
    assert positions == sorted(positions)

    reference_text = (
        REPO_ROOT / ".github/skills/internal-azure-operations/references/validation-and-evidence.md"
    ).read_text().lower()
    for marker in ("backup success", "restore proof", "dr exercise"):
        assert marker in reference_text


def test_azure_devops_is_reach_only_and_pipeline_workflow_complete() -> None:
    assert_reach_only_specialist("internal-azure-devops")
    skill_text = (
        REPO_ROOT / ".github/skills/internal-azure-devops/SKILL.md"
    ).read_text().lower()
    assert "## handoffs" not in skill_text
    for marker in (
        "request classification",
        "repository convention discovery",
        "pipeline or automation design",
        "security controls",
        "focused validation",
    ):
        assert marker in skill_text

    reference_text = (
        REPO_ROOT / ".github/skills/internal-azure-devops/references/pipelines.md"
    ).read_text().lower()
    assert "pipeline" in reference_text
    assert "routing" not in reference_text


def test_strategic_is_reach_only_and_decision_workflow_proportional() -> None:
    assert_reach_only_specialist("internal-azure-strategic")
    skill_text = (
        REPO_ROOT / ".github/skills/internal-azure-strategic/SKILL.md"
    ).read_text().split("---", maxsplit=2)[2].lower()
    markers = (
        "decision statement",
        "assumptions",
        "minimum lenses",
        "options",
        "recommendation and explain",
        "risk",
        "reversibility",
        "completion criteria",
    )
    positions = [skill_text.index(marker) for marker in markers]
    assert positions == sorted(positions)
    assert "bc/dr" not in skill_text

    playbook_text = LENS_PLAYBOOK_PATH.read_text().lower()
    assert "## bc/dr activation" in playbook_text
    assert playbook_text.count("bc/dr activation") == 1


def test_internal_azure_strategic_contract() -> None:
    skill_text = STRATEGIC_SKILL_PATH.read_text()

    strategic_markers = (
        "## When to use",
        "## Workflow",
        "## Proportional output",
        "decision statement",
        "references/lens-playbook.md",
    )
    for marker in strategic_markers:
        assert marker in skill_text


def test_internal_azure_interface_names_the_entry_point() -> None:
    interface = yaml.safe_load(AGENT_PATH.read_text())["interface"]

    assert interface == {
        "display_name": "Internal Azure",
        "short_description": "Azure platform entry point and deliverable selector",
        "default_prompt": "Use $internal-azure to select the right Azure platform specialist for the immediate deliverable.",
    }


def test_internal_azure_strategic_has_agent_metadata() -> None:
    interface = yaml.safe_load(STRATEGIC_AGENT_PATH.read_text())["interface"]

    assert interface["display_name"] == "Internal Azure Strategic"
    assert interface["short_description"]
    assert interface["default_prompt"]


def test_routing_matrix_covers_direct_adjacent_and_multi_deliverable_cases() -> None:
    matrix_text = ROUTING_MATRIX_PATH.read_text()

    for heading in (
        "## Direct specialist cases",
        "## Strategic decision cases",
        "## Adjacent-owner cases",
        "## Multi-deliverable ordering",
    ):
        assert heading in matrix_text

    for skill_id in (
        "internal-cloud-policy",
        "internal-terraform",
        "awesome-copilot-azure-role-selector",
        "awesome-copilot-azure-resource-health-diagnose",
        "awesome-copilot-azure-devops-cli",
        "awesome-copilot-azure-pricing",
    ):
        assert f"/{skill_id}" in matrix_text


def test_lens_playbook_keeps_strategic_depth() -> None:
    playbook_text = LENS_PLAYBOOK_PATH.read_text()

    for heading in (
        "## Common lens combinations",
        "## Decision note pattern",
        "## Depth control",
    ):
        assert heading in playbook_text


AZURE_SKILL_PATHS = sorted(
    (REPO_ROOT / ".github/skills").glob("internal-azure*/SKILL.md")
)
STRATEGIC_SKILL_ID = "internal-azure-strategic"
TRIGGER_FIXTURES = (
    ("management-group layout", "internal-azure-organization-structure"),
    ("RBAC operating model", "internal-azure-governance"),
    ("restore exercise evidence", "internal-azure-operations"),
    ("pipeline YAML review", "internal-azure-devops"),
    ("choosing between landing-zone alternatives", "internal-azure-strategic"),
    ("concrete Terraform edit", "internal-terraform"),
    ("concrete Azure Policy definition", "internal-cloud-policy"),
    ("current SKU price", "awesome-copilot-azure-pricing"),
    ("generic application code hosted on Azure", None),
)
FORBIDDEN_GENERIC_REFERENCES = (
    "internal-bash-script",
    "internal-python-script",
    "internal-python",
    "internal-python-project",
    "internal-nodejs",
    "internal-nodejs-project",
    "internal-terraform",
)


def test_azure_family_shape_and_generic_reference_ban() -> None:
    assert len(AZURE_SKILL_PATHS) == 6

    for path in AZURE_SKILL_PATHS:
        skill_text = path.read_text()
        for forbidden_name in FORBIDDEN_GENERIC_REFERENCES:
            assert f"`{forbidden_name}`" not in skill_text


def test_specialists_are_reach_only_and_self_contained() -> None:
    assert len(DIRECT_SPECIALISTS) == 5
    for skill_id in DIRECT_SPECIALISTS:
        assert_reach_only_specialist(skill_id)


LANE_SKILL_IDS = (
    "internal-azure-governance",
    "internal-azure-operations",
    "internal-azure-organization-structure",
    "internal-azure-devops",
    "internal-azure-strategic",
)

SKILL_REFERENCE_PATTERN = re.compile(
    r"`((?:internal|awesome|openai|superpowers|antigravity|addyosmani"
    r"|local|mattpocock|terraform|vercel|customize|grill|graphify)-[a-z0-9-]+)`"
)

REMOVED_SECTION_HEADINGS = (
    "## Handoffs",
    "## Cross-references",
    "## Referenced skills",
    "## Relationship to adjacent skills",
    "## When not to use",
)


def test_lane_skills_have_no_sibling_references_or_handoffs() -> None:
    for skill_id in LANE_SKILL_IDS:
        skill_dir = REPO_ROOT / ".github/skills" / skill_id
        text_paths = [
            skill_dir / "SKILL.md",
            *sorted(skill_dir.glob("references/*.md")),
        ]
        for text_path in text_paths:
            skill_text = text_path.read_text()
            for heading in REMOVED_SECTION_HEADINGS:
                assert heading not in skill_text, f"{skill_id} keeps {heading}"
            references = set(SKILL_REFERENCE_PATTERN.findall(skill_text))
            assert references <= {"internal-azure"}, (
                f"{text_path.name} references {sorted(references)}"
            )
            assert "handoff" not in skill_text.lower(), (
                f"{text_path.name} still mentions handoffs"
            )


def test_specialist_descriptions_are_positive_and_reachable() -> None:
    for skill_id in DIRECT_SPECIALISTS:
        frontmatter = load_frontmatter(
            REPO_ROOT / ".github/skills" / skill_id / "SKILL.md"
        )
        assert frontmatter["description"].startswith("Use when /internal-azure ")
        assert "Do not use" not in frontmatter["description"]


def test_inventory_lists_the_router_and_the_strategic() -> None:
    inventory_text = (REPO_ROOT / ".github/INVENTORY.md").read_text()

    assert ".github/skills/internal-azure/SKILL.md" in inventory_text
    assert ".github/skills/internal-azure-strategic/SKILL.md" in inventory_text


def test_azure_profile_includes_router_and_all_direct_specialists() -> None:
    profiles = yaml.safe_load((REPO_ROOT / ".github/repo-profiles.yml").read_text())
    configured = set(profiles["profiles"]["azure-platform"]["recommended_skills"])
    required = {
        "skills/internal-azure/SKILL.md",
        *{f"skills/{skill_id}/SKILL.md" for skill_id in DIRECT_SPECIALISTS},
    }
    assert required <= configured


def test_trigger_evaluation_fixtures_have_deterministic_matrix_coverage() -> None:
    matrix_text = ROUTING_MATRIX_PATH.read_text().lower()
    # Descriptions and fixtures are deterministic; live model invocation frequency
    # remains a validation gap that this repository cannot measure.
    for scenario, expected_skill in TRIGGER_FIXTURES:
        assert scenario.lower() in matrix_text
        if expected_skill is None:
            assert "no forced azure specialist" in matrix_text
        else:
            assert f"/{expected_skill}" in matrix_text
