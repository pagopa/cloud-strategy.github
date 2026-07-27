import json
import re
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github/skills"
SKILL_DIR = SKILLS_ROOT / "internal-aws"
SKILL_PATH = SKILL_DIR / "SKILL.md"
AGENT_PATH = SKILL_DIR / "agents/openai.yaml"
ROUTING_MATRIX_PATH = SKILL_DIR / "references/routing-matrix.md"
FIXTURE_PATH = (
    REPO_ROOT
    / "tests/github/skills/internal-aws/fixtures/routing_cases.json"
)

AWS_SPECIALIST_IDS = (
    "internal-aws-governance",
    "internal-aws-lambda",
    "internal-aws-mcp-research",
    "internal-aws-operations",
    "internal-aws-organization-structure",
    "internal-aws-strategic",
)

ROUTED_DESTINATIONS = (
    *AWS_SPECIALIST_IDS,
    "antigravity-aws-cost-optimizer",
)

EXPECTED_SPECIALIST_DESCRIPTIONS = {
    "internal-aws-organization-structure": (
        "Use when /internal-aws selects the AWS organization-structure lane "
        "for Organizations, accounts, OUs, delegated administrators, "
        "StackSets topology, or platform-level network placement."
    ),
    "internal-aws-governance": (
        "Use when /internal-aws selects the AWS governance lane for IAM "
        "operating models, trust policies, federation, permission boundaries, "
        "SCPs, tag policies, exception controls, or access guardrails."
    ),
    "internal-aws-operations": (
        "Use when /internal-aws selects the AWS operations lane for "
        "monitoring, logging, rollout validation, backup and restore proof, "
        "DR evidence, reporting, or audit evidence."
    ),
    "internal-aws-mcp-research": (
        "Use when /internal-aws selects the AWS research lane to retrieve "
        "current official AWS documentation, regional availability, service "
        "behavior, IAM state, or policy-simulation evidence."
    ),
    "internal-aws-lambda": (
        "Use when /internal-aws selects the AWS Lambda lane for handlers, "
        "event sources, runtimes, packaging, retries, concurrency, cold "
        "starts, or Lambda-specific configuration."
    ),
    "internal-aws-strategic": (
        "Use when /internal-aws selects the AWS strategic lane for option "
        "comparison, multi-lens tradeoffs, cost-value analysis, blast radius, "
        "or reversibility before implementation."
    ),
}

EXPECTED_ROUTER_DESCRIPTION = (
    "Use first for every AWS request. Classify the primary deliverable and "
    "invoke the minimum specialist lane for AWS structure, governance, "
    "operations, Lambda, current documentation or IAM evidence, strategic "
    "decisions, or cost optimization."
)

FORBIDDEN_ROUTING_LANGUAGE = (
    "handoff",
    "hand off",
    "route back",
    "outside this lane",
    "out-of-scope",
)

SKILL_REFERENCE_PATTERN = re.compile(
    r"(?<![a-z0-9-])(?:internal-aws(?:-[a-z0-9-]+)?|"
    r"antigravity-aws-cost-optimizer)(?![a-z0-9-])"
)


def load_frontmatter(path: Path) -> dict[str, object]:
    _, raw_frontmatter, _ = path.read_text(encoding="utf-8").split(
        "---", maxsplit=2
    )
    return yaml.safe_load(raw_frontmatter)


def _body(path: Path) -> str:
    parts = path.read_text(encoding="utf-8").split("---", maxsplit=2)
    return parts[2] if len(parts) == 3 else parts[-1]


def _specialist_paths() -> list[Path]:
    return [SKILLS_ROOT / skill_id / "SKILL.md" for skill_id in AWS_SPECIALIST_IDS]


def test_internal_aws_router_is_the_canonical_entry_point() -> None:
    assert load_frontmatter(SKILL_PATH) == {
        "name": "internal-aws",
        "description": EXPECTED_ROUTER_DESCRIPTION,
    }


def test_specialist_descriptions_identify_router_selection() -> None:
    for skill_id, expected in EXPECTED_SPECIALIST_DESCRIPTIONS.items():
        frontmatter = load_frontmatter(SKILLS_ROOT / skill_id / "SKILL.md")
        assert frontmatter["description"] == expected


def test_routed_destinations_allow_model_invocation() -> None:
    for skill_id in AWS_SPECIALIST_IDS:
        frontmatter = load_frontmatter(SKILLS_ROOT / skill_id / "SKILL.md")
        assert frontmatter.get("disable-model-invocation") is not True


def test_router_uses_slash_prefixed_operational_destinations() -> None:
    router_text = SKILL_PATH.read_text(encoding="utf-8")
    for destination in ROUTED_DESTINATIONS:
        assert f"/{destination}" in router_text


def test_specialists_contain_no_forbidden_routing_language() -> None:
    for skill_path in _specialist_paths():
        text_paths = [skill_path, *sorted(skill_path.parent.glob("references/*.md"))]
        for text_path in text_paths:
            text = text_path.read_text(encoding="utf-8").lower()
            assert not any(term in text for term in FORBIDDEN_ROUTING_LANGUAGE), (
                f"{text_path} contains forbidden routing language"
            )


def test_specialists_contain_no_sibling_skill_identifiers() -> None:
    for skill_path in _specialist_paths():
        text_paths = [skill_path, *sorted(skill_path.parent.glob("references/*.md"))]
        for text_path in text_paths:
            text = _body(text_path) if text_path == skill_path else text_path.read_text()
            references = set(SKILL_REFERENCE_PATTERN.findall(text))
            assert not references, f"{text_path} references {sorted(references)}"


def test_specialist_metadata_is_purpose_specific() -> None:
    for skill_id in AWS_SPECIALIST_IDS:
        interface = yaml.safe_load(
            (SKILLS_ROOT / skill_id / "agents/openai.yaml").read_text(
                encoding="utf-8"
            )
        )["interface"]
        assert interface["default_prompt"].find(f"${skill_id}") >= 0
        assert interface["short_description"]
        assert "AWS" in interface["short_description"]
        assert not re.search(r"(?<!A)aws", interface["short_description"])


def test_routing_fixture_covers_the_approved_destinations() -> None:
    cases = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert isinstance(cases, list)
    assert len({case["id"] for case in cases}) == len(cases)

    for case in cases:
        assert set(case) == {
            "id",
            "kind",
            "prompt",
            "expected_sequence",
            "reason",
        }
        if case["kind"] == "near-miss":
            assert case["expected_sequence"] == []
        else:
            assert case["expected_sequence"]
        assert set(case["expected_sequence"]) <= set(ROUTED_DESTINATIONS)

    destinations = {
        destination
        for case in cases
        for destination in case["expected_sequence"]
    }
    assert destinations == set(ROUTED_DESTINATIONS)
    assert sum(case["kind"] == "near-miss" for case in cases) >= 2
    assert sum(case["kind"] == "multi-owner" for case in cases) >= 2


def test_inventory_lists_exactly_the_expected_aws_bundles() -> None:
    inventory_text = (REPO_ROOT / ".github/INVENTORY.md").read_text(encoding="utf-8")
    expected_paths = {
        f".github/skills/{skill_id}/SKILL.md"
        for skill_id in ("internal-aws", *AWS_SPECIALIST_IDS)
    }
    listed_paths = {
        line.strip().lstrip("- `").rstrip("`")
        for line in inventory_text.splitlines()
        if ".github/skills/internal-aws" in line and "/SKILL.md" in line
    }
    assert listed_paths == expected_paths


def test_routing_matrix_has_the_new_primary_deliverable_shape() -> None:
    matrix_text = ROUTING_MATRIX_PATH.read_text(encoding="utf-8")
    for heading in (
        "## Single-owner cases",
        "## Primary-owner disambiguation",
        "## Permitted multi-deliverable sequences",
        "## Near-miss distinctions",
    ):
        assert heading in matrix_text


def test_router_interface_names_the_canonical_entry_point() -> None:
    interface = yaml.safe_load(AGENT_PATH.read_text(encoding="utf-8"))["interface"]
    assert interface == {
        "display_name": "Internal AWS",
        "short_description": "Canonical entry point for every AWS request",
        "default_prompt": (
            "Use $internal-aws to classify this AWS request and invoke the "
            "minimum specialist lane."
        ),
    }
