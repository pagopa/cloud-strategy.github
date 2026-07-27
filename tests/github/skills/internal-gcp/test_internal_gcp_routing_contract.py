from pathlib import Path

import pytest
import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILLS_ROOT = REPO_ROOT / ".github/skills"
ROUTER_ID = "internal-gcp"
SPECIALISTS = {
    "internal-gcp-organization-structure": (
        "organization structure",
        ("folder", "billing", "project", "Shared VPC"),
    ),
    "internal-gcp-governance": (
        "governance",
        ("IAM", "workload identity", "service-account", "Org Policy"),
    ),
    "internal-gcp-operations": (
        "operations",
        ("monitoring", "backup", "recovery", "evidence"),
    ),
    "internal-gcp-strategic": (
        "strategic decision support",
        ("decision", "tradeoff", "options", "assumptions"),
    ),
}
FORBIDDEN_SPECIALIST_TEXT = (
    "handoff",
    "hand off",
    "route back",
    "routing uncertainty",
    "when not to use",
    "does not replace",
    "out-of-scope",
    "not enough",
)


def load_frontmatter(path: Path) -> dict[str, object]:
    _, raw_frontmatter, _ = path.read_text().split("---", maxsplit=2)
    return yaml.safe_load(raw_frontmatter)


def skill_path(skill_id: str) -> Path:
    return SKILLS_ROOT / skill_id / "SKILL.md"


def skill_body(path: Path) -> str:
    return path.read_text().split("---", maxsplit=2)[2]


def interface(skill_id: str) -> dict[str, str]:
    path = SKILLS_ROOT / skill_id / "agents/openai.yaml"
    return yaml.safe_load(path.read_text())["interface"]


def test_router_is_the_only_general_gcp_entrypoint() -> None:
    router = load_frontmatter(skill_path(ROUTER_ID))
    assert router["name"] == ROUTER_ID
    assert "disable-model-invocation" not in router
    assert "official and default" in router["description"].lower()
    assert "any Google Cloud request" in router["description"]

    for skill_id in SPECIALISTS:
        frontmatter = load_frontmatter(skill_path(skill_id))
        assert "disable-model-invocation" not in frontmatter
        assert frontmatter["description"].startswith(
            f"Use when /{ROUTER_ID} selects "
        )
        assert "any Google Cloud request" not in frontmatter["description"]
        assert "Do not use" not in frontmatter["description"]


def test_router_invokes_every_specialist_by_operational_name() -> None:
    body = skill_body(skill_path(ROUTER_ID))
    for skill_id in SPECIALISTS:
        assert f"/{skill_id}" in body
    assert "reading the chosen skill" not in body.lower()
    assert "handoff" not in body.lower()
    assert "disable-model-invocation" not in body


@pytest.mark.parametrize("skill_id", SPECIALISTS)
def test_specialists_are_positive_and_lane_local(skill_id: str) -> None:
    all_ids = {ROUTER_ID, *SPECIALISTS}
    _, trigger_terms = SPECIALISTS[skill_id]
    path = skill_path(skill_id)
    description = load_frontmatter(path)["description"]
    body = skill_body(path)
    combined = "\n".join(
        [body, *[p.read_text() for p in sorted(path.parent.glob("references/*.md"))]]
    )

    assert all(term.lower() in description.lower() for term in trigger_terms)
    assert not any(term in combined.lower() for term in FORBIDDEN_SPECIALIST_TEXT)
    assert "## When not to use" not in combined
    for sibling_id in all_ids - {skill_id}:
        assert sibling_id not in combined


def test_specialist_descriptions_are_distinct() -> None:
    descriptions = {
        skill_id: load_frontmatter(skill_path(skill_id))["description"]
        for skill_id in SPECIALISTS
    }
    assert len(set(descriptions.values())) == len(SPECIALISTS)


@pytest.mark.parametrize("skill_id", SPECIALISTS)
def test_specialist_description_names_its_leading_branch(skill_id: str) -> None:
    branch, _ = SPECIALISTS[skill_id]
    description = load_frontmatter(skill_path(skill_id))["description"]
    assert branch in description.lower()


ROUTING_SCENARIOS = {
    "Shared VPC host and service-project placement": "internal-gcp-organization-structure",
    "Org Policy rollout with IAM exceptions": "internal-gcp-governance",
    "Restore evidence and recovery validation": "internal-gcp-operations",
    "Compare two GCP platform options and recommend one": "internal-gcp-strategic",
}


def test_router_agent_metadata_names_default_entrypoint() -> None:
    router_prompt = interface(ROUTER_ID)["default_prompt"]
    assert "$internal-gcp" in router_prompt
    assert "official and default" in router_prompt.lower()


@pytest.mark.parametrize("skill_id", SPECIALISTS)
def test_specialist_agent_metadata_is_router_scoped(skill_id: str) -> None:
    prompt = interface(skill_id)["default_prompt"]
    assert f"${skill_id}" in prompt
    assert "$internal-gcp selects" in prompt


def test_router_matrix_covers_should_trigger_and_multidomain_cases() -> None:
    matrix = (SKILLS_ROOT / ROUTER_ID / "references/routing-matrix.md").read_text()
    for scenario, owner in ROUTING_SCENARIOS.items():
        assert scenario in matrix
        assert f"/{owner}" in matrix
    assert "primary deliverable" in matrix.lower()
    assert "domain count" in matrix.lower()


@pytest.mark.parametrize("skill_id", [ROUTER_ID, *SPECIALISTS])
def test_reference_has_one_explicit_context_pointer(skill_id: str) -> None:
    path = skill_path(skill_id)
    body = skill_body(path)
    references = sorted(path.parent.glob("references/*.md"))
    assert len(references) == 1
    assert f"references/{references[0].name}" in body


def test_inventory_lists_the_complete_gcp_family() -> None:
    inventory = (REPO_ROOT / ".github/INVENTORY.md").read_text()
    for skill_id in {ROUTER_ID, *SPECIALISTS}:
        assert f".github/skills/{skill_id}/SKILL.md" in inventory
