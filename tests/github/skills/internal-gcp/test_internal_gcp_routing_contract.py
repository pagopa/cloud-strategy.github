import re
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_DIR = REPO_ROOT / ".github/skills/internal-gcp"
STRATEGIC_SKILL_DIR = REPO_ROOT / ".github/skills/internal-gcp-strategic"
SKILL_PATH = SKILL_DIR / "SKILL.md"
AGENT_PATH = SKILL_DIR / "agents/openai.yaml"
ROUTING_MATRIX_PATH = SKILL_DIR / "references/routing-matrix.md"
STRATEGIC_SKILL_PATH = STRATEGIC_SKILL_DIR / "SKILL.md"
STRATEGIC_AGENT_PATH = STRATEGIC_SKILL_DIR / "agents/openai.yaml"
LENS_PLAYBOOK_PATH = STRATEGIC_SKILL_DIR / "references/lens-playbook.md"

EXPECTED_ROUTER_DESCRIPTION = (
    "Official entry point for any Google Cloud task. Routes every GCP "
    "request to the right specialist - organization structure, governance, "
    "or operations - or to internal-gcp-strategic for high-level decision "
    "framing. Use for any Google Cloud request, scoped or ambiguous."
)

EXPECTED_STRATEGIC_DESCRIPTION = (
    "Use when you need high-level Google Cloud decision support, tradeoff "
    "framing, or multi-lens analysis before implementation, or when "
    "internal-gcp routes a strategic question here. Invoke manually "
    "($internal-gcp-strategic) or via internal-gcp handoff. Do not use for "
    "clearly scoped specialist tasks with a known owner."
)


def load_frontmatter(path: Path) -> dict[str, object]:
    _, raw_frontmatter, _ = path.read_text().split("---", maxsplit=2)
    return yaml.safe_load(raw_frontmatter)


def test_internal_gcp_router_is_the_unflagged_entry_point() -> None:
    assert SKILL_PATH.is_file()
    assert load_frontmatter(SKILL_PATH) == {
        "name": "internal-gcp",
        "description": EXPECTED_ROUTER_DESCRIPTION,
    }


def test_internal_gcp_strategic_is_user_invoked_only() -> None:
    assert STRATEGIC_SKILL_PATH.is_file()
    assert load_frontmatter(STRATEGIC_SKILL_PATH) == {
        "name": "internal-gcp-strategic",
        "description": EXPECTED_STRATEGIC_DESCRIPTION,
        "disable-model-invocation": True,
    }


def test_internal_gcp_router_contract() -> None:
    skill_text = SKILL_PATH.read_text()

    router_markers = (
        "Official entry point and lightweight router",
        "## When to use",
        "## Destinations",
        "`internal-gcp-strategic`",
        "Hand off by reading the chosen skill's `SKILL.md`",
        "disable-model-invocation: true",
    )
    for marker in router_markers:
        assert marker in skill_text


def test_internal_gcp_strategic_contract() -> None:
    skill_text = STRATEGIC_SKILL_PATH.read_text()

    strategic_markers = (
        "## When to use",
        "## Optional lens activation",
        "## Adaptive output modes",
        "Identify the decision first, not the implementation tool",
        "`internal-gcp` handoff or explicit manual invocation",
    )
    for marker in strategic_markers:
        assert marker in skill_text


def test_internal_gcp_interface_names_the_entry_point() -> None:
    interface = yaml.safe_load(AGENT_PATH.read_text())["interface"]

    assert interface == {
        "display_name": "Internal GCP",
        "short_description": "Official GCP entry point and router",
        "default_prompt": (
            "Use $internal-gcp as the entry point for any Google Cloud "
            "task; it routes to the minimum specialist set, or to "
            "$internal-gcp-strategic for decision framing."
        ),
    }


def test_internal_gcp_strategic_has_agent_metadata() -> None:
    interface = yaml.safe_load(STRATEGIC_AGENT_PATH.read_text())["interface"]

    assert interface["display_name"] == "Internal GCP Strategic"
    assert interface["short_description"]
    assert interface["default_prompt"]


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


GCP_SKILL_PATHS = sorted((REPO_ROOT / ".github/skills").glob("internal-gcp*/SKILL.md"))
STRATEGIC_SKILL_ID = "internal-gcp-strategic"
FORBIDDEN_GENERIC_REFERENCES = (
    "internal-bash-script",
    "internal-python-script",
    "internal-python",
    "internal-python-project",
    "internal-nodejs",
    "internal-nodejs-project",
    "internal-terraform",
)


def test_gcp_family_shape_and_generic_reference_ban() -> None:
    assert len(GCP_SKILL_PATHS) == 5

    for path in GCP_SKILL_PATHS:
        skill_text = path.read_text()
        for forbidden_name in FORBIDDEN_GENERIC_REFERENCES:
            assert f"`{forbidden_name}`" not in skill_text


def test_specialists_name_internal_gcp_only_as_uncertainty_fallback() -> None:
    specialist_paths = [
        path
        for path in GCP_SKILL_PATHS
        if path != SKILL_PATH and path != STRATEGIC_SKILL_PATH
    ]
    assert len(specialist_paths) == 3

    for path in specialist_paths:
        skill_text = path.read_text()
        assert "`internal-gcp`" in skill_text
        assert "material routing uncertainty" in skill_text


def test_strategic_hands_back_to_the_router() -> None:
    skill_text = STRATEGIC_SKILL_PATH.read_text()

    assert "`internal-gcp`" in skill_text
    assert "explicit manual invocation" in skill_text


LANE_SKILL_IDS = (
    "internal-gcp-governance",
    "internal-gcp-operations",
    "internal-gcp-organization-structure",
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
            assert references <= {"internal-gcp"}, (
                f"{text_path.name} references {sorted(references)}"
            )
            assert "handoff" not in skill_text.lower(), (
                f"{text_path.name} still mentions handoffs"
            )


EXPECTED_SPECIALIST_DESCRIPTION_PREFIXES = {
    "internal-gcp-organization-structure": "Use when ",
    "internal-gcp-governance": "Use when ",
    "internal-gcp-operations": "Use when ",
    "internal-gcp-strategic": "Use when ",
}


def test_specialist_descriptions_carry_positive_and_negative_triggers() -> None:
    for path in GCP_SKILL_PATHS:
        frontmatter = load_frontmatter(path)
        name = frontmatter["name"]
        if name == "internal-gcp":
            continue
        assert name in EXPECTED_SPECIALIST_DESCRIPTION_PREFIXES
        description = frontmatter["description"]
        assert description.startswith(EXPECTED_SPECIALIST_DESCRIPTION_PREFIXES[name])
        assert "Do not use" in description


def test_inventory_lists_the_router_and_the_strategic() -> None:
    inventory_text = (REPO_ROOT / ".github/INVENTORY.md").read_text()

    assert ".github/skills/internal-gcp/SKILL.md" in inventory_text
    assert ".github/skills/internal-gcp-strategic/SKILL.md" in inventory_text
