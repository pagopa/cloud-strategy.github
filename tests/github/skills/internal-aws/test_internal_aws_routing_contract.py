import re
from pathlib import Path

import yaml


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_DIR = REPO_ROOT / ".github/skills/internal-aws"
LEGACY_SKILL_DIR = REPO_ROOT / ".github/skills" / ("internal-aws-" + "strategic")
SKILL_PATH = SKILL_DIR / "SKILL.md"
AGENT_PATH = SKILL_DIR / "agents/openai.yaml"
ROUTING_MATRIX_PATH = SKILL_DIR / "references/routing-matrix.md"

EXPECTED_DESCRIPTION = (
    "Use when an AWS task cannot be routed confidently to a specific AWS "
    "skill because the request is materially ambiguous, has multiple AWS domains "
    "with no clear primary owner, or requires clarification before selecting the "
    "correct specialist, or when the user needs high-level AWS platform "
    "decision support or tradeoff framing before implementation. Do not use for "
    "clearly scoped organization structure, governance or IAM, operations or "
    "validation, Lambda, or current AWS documentation research tasks."
)


def load_frontmatter(path: Path) -> dict[str, object]:
    _, raw_frontmatter, _ = path.read_text().split("---", maxsplit=2)
    return yaml.safe_load(raw_frontmatter)


def test_internal_aws_replaces_the_legacy_bundle() -> None:
    assert SKILL_PATH.is_file()
    assert not LEGACY_SKILL_DIR.exists()
    assert load_frontmatter(SKILL_PATH) == {
        "name": "internal-aws",
        "description": EXPECTED_DESCRIPTION,
    }


def test_internal_aws_contract_is_router_and_strategic() -> None:
    skill_text = SKILL_PATH.read_text()

    router_markers = (
        "material routing uncertainty",
        "Do not activate only because the task concerns AWS",
        "Do not activate when one specialist clearly owns the next step",
        "Select the minimum specialist set",
        "Explicit `$internal-aws` invocation remains valid",
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


def test_internal_aws_interface_names_router_and_strategic() -> None:
    interface = yaml.safe_load(AGENT_PATH.read_text())["interface"]

    assert interface == {
        "display_name": "Internal AWS",
        "short_description": "AWS routing and strategic decision support",
        "default_prompt": (
            "Use $internal-aws to route an unclear AWS task to the minimum "
            "specialist set, or to frame an AWS decision when the next "
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


AWS_SKILL_PATHS = sorted(
    (REPO_ROOT / ".github/skills").glob("internal-aws*/SKILL.md")
)
LEGACY_SKILL_ID = "internal-aws-" + "strategic"
FORBIDDEN_GENERIC_REFERENCES = (
    "internal-bash-script",
    "internal-python-script",
    "internal-python",
    "internal-python-project",
    "internal-nodejs",
    "internal-nodejs-project",
    "internal-terraform",
)


def test_aws_family_has_no_legacy_or_generic_skill_references() -> None:
    assert len(AWS_SKILL_PATHS) == 6

    for path in AWS_SKILL_PATHS:
        skill_text = path.read_text()
        assert LEGACY_SKILL_ID not in skill_text
        for forbidden_name in FORBIDDEN_GENERIC_REFERENCES:
            assert f"`{forbidden_name}`" not in skill_text


def test_specialists_name_internal_aws_only_as_uncertainty_fallback() -> None:
    specialist_paths = [path for path in AWS_SKILL_PATHS if path != SKILL_PATH]

    for path in specialist_paths:
        skill_text = path.read_text()
        assert "`internal-aws`" in skill_text
        assert "material routing uncertainty" in skill_text


LANE_SKILL_IDS = (
    "internal-aws-governance",
    "internal-aws-lambda",
    "internal-aws-mcp-research",
    "internal-aws-operations",
    "internal-aws-organization-structure",
)

SKILL_REFERENCE_PATTERN = re.compile(
    r"`((?:internal|awesome|openai|superpowers|agent-os|antigravity|addyosmani"
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
        text_paths = [skill_dir / "SKILL.md", *sorted(skill_dir.glob("references/*.md"))]
        for text_path in text_paths:
            skill_text = text_path.read_text()
            for heading in REMOVED_SECTION_HEADINGS:
                assert heading not in skill_text, f"{skill_id} keeps {heading}"
            references = set(SKILL_REFERENCE_PATTERN.findall(skill_text))
            assert references <= {"internal-aws"}, (
                f"{text_path.name} references {sorted(references)}"
            )
            assert "handoff" not in skill_text.lower(), (
                f"{text_path.name} still mentions handoffs"
            )


def test_mcp_capability_map_uses_the_canonical_fallback_name() -> None:
    capability_map = (
        REPO_ROOT
        / ".github/skills/internal-aws-mcp-research/references/mcp-capabilities.md"
    ).read_text()

    assert LEGACY_SKILL_ID not in capability_map
    assert "`internal-aws`" in capability_map


def test_inventory_lists_only_the_canonical_internal_aws_bundle() -> None:
    inventory_text = (REPO_ROOT / ".github/INVENTORY.md").read_text()

    assert ".github/skills/internal-aws/SKILL.md" in inventory_text
    assert LEGACY_SKILL_ID not in inventory_text
