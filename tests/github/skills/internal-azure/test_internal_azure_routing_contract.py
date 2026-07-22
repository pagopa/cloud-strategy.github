from pathlib import Path

import yaml


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_DIR = REPO_ROOT / ".github/skills/internal-azure"
LEGACY_SKILL_DIR = REPO_ROOT / ".github/skills" / ("internal-azure-" + "strategic")
SKILL_PATH = SKILL_DIR / "SKILL.md"
AGENT_PATH = SKILL_DIR / "agents/openai.yaml"
ROUTING_MATRIX_PATH = SKILL_DIR / "references/routing-matrix.md"
LENS_PLAYBOOK_PATH = SKILL_DIR / "references/lens-playbook.md"

EXPECTED_DESCRIPTION = (
    "Use when an Azure task cannot be routed confidently to a specific Azure "
    "skill because the request is materially ambiguous, has multiple Azure "
    "domains with no clear primary owner, or requires clarification before "
    "selecting the correct specialist, or when the user needs high-level Azure "
    "platform decision support or tradeoff framing before implementation. "
    "Do not use for clearly scoped organization structure, governance or "
    "identity, operations or validation, or Azure DevOps pipeline tasks."
)


def load_frontmatter(path: Path) -> dict[str, object]:
    _, raw_frontmatter, _ = path.read_text().split("---", maxsplit=2)
    return yaml.safe_load(raw_frontmatter)


def test_internal_azure_replaces_the_legacy_bundle() -> None:
    assert SKILL_PATH.is_file()
    assert not LEGACY_SKILL_DIR.exists()
    assert load_frontmatter(SKILL_PATH) == {
        "name": "internal-azure",
        "description": EXPECTED_DESCRIPTION,
    }


def test_internal_azure_contract_is_router_and_strategic() -> None:
    skill_text = SKILL_PATH.read_text()

    router_markers = (
        "material routing uncertainty",
        "Do not activate only because the task concerns Azure",
        "Do not activate when one specialist clearly owns the next step",
        "Select the minimum specialist set",
        "Explicit `$internal-azure` invocation remains valid",
    )
    for marker in router_markers:
        assert marker in skill_text

    strategic_markers = (
        "Identify the decision first, not the implementation tool",
        "Compare realistic options, not strawmen.",
        "Keep tradeoffs concrete.",
    )
    for marker in strategic_markers:
        assert marker in skill_text


def test_internal_azure_interface_names_router_and_strategic() -> None:
    interface = yaml.safe_load(AGENT_PATH.read_text())["interface"]

    assert interface == {
        "display_name": "Internal Azure",
        "short_description": "Azure routing and strategic decision support",
        "default_prompt": (
            "Use $internal-azure to route an unclear Azure task to the minimum "
            "specialist set, or to frame an Azure decision when the next "
            "step is not yet structure, governance, operations, or delivery."
        ),
    }


def test_routing_matrix_covers_positive_negative_and_multi_domain_cases() -> None:
    matrix_text = ROUTING_MATRIX_PATH.read_text()

    for heading in (
        "## Fallback-positive cases",
        "## Direct-specialist negative cases",
        "## Multi-domain primary-owner cases",
        "## Review rule",
    ):
        assert heading in matrix_text


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
LEGACY_SKILL_ID = "internal-azure-" + "strategic"
FORBIDDEN_GENERIC_REFERENCES = (
    "internal-bash-script",
    "internal-python-script",
    "internal-python",
    "internal-python-project",
    "internal-nodejs",
    "internal-nodejs-project",
    "internal-terraform",
)

EXPECTED_SPECIALIST_DESCRIPTION_PREFIXES = {
    "internal-azure-organization-structure": "Use when ",
    "internal-azure-governance": "Use when ",
    "internal-azure-operations": "Use when ",
    "internal-azure-devops": "Use when ",
}


def test_azure_family_has_no_legacy_or_generic_skill_references() -> None:
    assert len(AZURE_SKILL_PATHS) == 5

    for path in AZURE_SKILL_PATHS:
        skill_text = path.read_text()
        assert LEGACY_SKILL_ID not in skill_text
        for forbidden_name in FORBIDDEN_GENERIC_REFERENCES:
            assert f"`{forbidden_name}`" not in skill_text


def test_specialists_name_internal_azure_only_as_uncertainty_fallback() -> None:
    specialist_paths = [path for path in AZURE_SKILL_PATHS if path != SKILL_PATH]

    for path in specialist_paths:
        skill_text = path.read_text()
        assert "`internal-azure`" in skill_text
        assert "material routing uncertainty" in skill_text


def test_specialist_descriptions_carry_positive_and_negative_triggers() -> None:
    for path in AZURE_SKILL_PATHS:
        frontmatter = load_frontmatter(path)
        name = frontmatter["name"]
        if name == "internal-azure":
            continue
        assert name in EXPECTED_SPECIALIST_DESCRIPTION_PREFIXES
        description = frontmatter["description"]
        assert description.startswith(
            EXPECTED_SPECIALIST_DESCRIPTION_PREFIXES[name]
        )
        assert "Do not use" in description


def test_inventory_lists_only_the_canonical_internal_azure_bundle() -> None:
    inventory_text = (REPO_ROOT / ".github/INVENTORY.md").read_text()

    assert ".github/skills/internal-azure/SKILL.md" in inventory_text
    assert LEGACY_SKILL_ID not in inventory_text


def test_repo_profiles_reference_the_canonical_internal_azure_bundle() -> None:
    profiles = yaml.safe_load(
        (REPO_ROOT / ".github/repo-profiles.yml").read_text()
    )
    azure_skills = profiles["profiles"]["azure-platform"]["recommended_skills"]

    assert "skills/internal-azure/SKILL.md" in azure_skills
    assert not any(LEGACY_SKILL_ID in entry for entry in azure_skills)
