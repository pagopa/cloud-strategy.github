import re
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_DIR = REPO_ROOT / ".github/skills/internal-gcp"
LEGACY_SKILL_DIR = REPO_ROOT / ".github/skills" / ("internal-gcp-" + "strategic")
SKILL_PATH = SKILL_DIR / "SKILL.md"
AGENT_PATH = SKILL_DIR / "agents/openai.yaml"
ROUTING_MATRIX_PATH = SKILL_DIR / "references/routing-matrix.md"
LENS_PLAYBOOK_PATH = SKILL_DIR / "references/lens-playbook.md"

EXPECTED_DESCRIPTION = (
    "Use when a Google Cloud task cannot be routed confidently to a specific GCP "
    "skill because the request is materially ambiguous, has multiple GCP domains "
    "with no clear primary owner, or requires clarification before selecting the "
    "correct specialist, or when the user needs high-level Google Cloud platform "
    "decision support or tradeoff framing before implementation. Do not use for "
    "clearly scoped organization structure, governance or IAM, or operations or "
    "validation tasks."
)


def load_frontmatter(path: Path) -> dict[str, object]:
    _, raw_frontmatter, _ = path.read_text().split("---", maxsplit=2)
    return yaml.safe_load(raw_frontmatter)


def test_internal_gcp_replaces_the_legacy_bundle() -> None:
    assert SKILL_PATH.is_file()
    assert not LEGACY_SKILL_DIR.exists()
    assert load_frontmatter(SKILL_PATH) == {
        "name": "internal-gcp",
        "description": EXPECTED_DESCRIPTION,
    }


def test_internal_gcp_contract_is_router_and_strategic() -> None:
    skill_text = SKILL_PATH.read_text()

    router_markers = (
        "material routing uncertainty",
        "Do not activate only because the task concerns Google Cloud",
        "Do not activate when one specialist clearly owns the next step",
        "Select the minimum specialist set",
        "Explicit `$internal-gcp` invocation remains valid",
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


def test_internal_gcp_interface_names_router_and_strategic() -> None:
    interface = yaml.safe_load(AGENT_PATH.read_text())["interface"]

    assert interface == {
        "display_name": "Internal GCP",
        "short_description": "GCP routing and strategic decision support",
        "default_prompt": (
            "Use $internal-gcp to route an unclear GCP task to the minimum "
            "specialist set, or to frame a Google Cloud decision when the next "
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


GCP_SKILL_PATHS = sorted((REPO_ROOT / ".github/skills").glob("internal-gcp*/SKILL.md"))
LEGACY_SKILL_ID = "internal-gcp-" + "strategic"
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
    "internal-gcp-organization-structure": "Use when ",
    "internal-gcp-governance": "Use when ",
    "internal-gcp-operations": "Use when ",
}


def test_gcp_family_has_no_legacy_or_generic_skill_references() -> None:
    assert len(GCP_SKILL_PATHS) == 4

    for path in GCP_SKILL_PATHS:
        skill_text = path.read_text()
        assert LEGACY_SKILL_ID not in skill_text
        for forbidden_name in FORBIDDEN_GENERIC_REFERENCES:
            assert f"`{forbidden_name}`" not in skill_text


def test_specialists_name_internal_gcp_only_as_uncertainty_fallback() -> None:
    specialist_paths = [path for path in GCP_SKILL_PATHS if path != SKILL_PATH]

    for path in specialist_paths:
        skill_text = path.read_text()
        assert "`internal-gcp`" in skill_text
        assert "material routing uncertainty" in skill_text


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


def test_inventory_lists_only_the_canonical_internal_gcp_bundle() -> None:
    inventory_text = (REPO_ROOT / ".github/INVENTORY.md").read_text()

    assert ".github/skills/internal-gcp/SKILL.md" in inventory_text
    assert LEGACY_SKILL_ID not in inventory_text
