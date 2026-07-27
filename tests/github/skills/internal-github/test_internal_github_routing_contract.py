import re
from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_DIR = REPO_ROOT / ".github/skills/internal-github"
STRATEGIC_SKILL_DIR = REPO_ROOT / ".github/skills/internal-github-strategic"
SKILL_PATH = SKILL_DIR / "SKILL.md"
AGENT_PATH = SKILL_DIR / "agents/openai.yaml"
ROUTING_MATRIX_PATH = SKILL_DIR / "references/routing-matrix.md"
STRATEGIC_SKILL_PATH = STRATEGIC_SKILL_DIR / "SKILL.md"
STRATEGIC_AGENT_PATH = STRATEGIC_SKILL_DIR / "agents/openai.yaml"
STRATEGIC_FRAMING_PATH = STRATEGIC_SKILL_DIR / "references/strategic-framing.md"

EXPECTED_ROUTER_DESCRIPTION = (
    "Official entry point for any GitHub task. Routes every GitHub request "
    "to the right specialist - governance, operations, Actions workflows, "
    "composite actions, PR lifecycle, or Copilot platform research - or to "
    "/internal-github-strategic for high-level decision framing. Use for any "
    "GitHub request, scoped or ambiguous."
)

ROUTED_SPECIALISTS = (
    "internal-github-strategic",
    "internal-github-governance",
    "internal-github-operations",
    "internal-github-actions",
    "internal-github-action-composite",
    "internal-github-pr",
)

ROUTE_CASES = {
    "mono-repo versus multi-repo decision": "internal-github-strategic",
    "organization ruleset design": "internal-github-governance",
    "runner fleet health": "internal-github-operations",
    ".github/workflows/ deployment edit": "internal-github-actions",
    ".github/actions/ action.yml edit": "internal-github-action-composite",
    "merge readiness for one PR": "internal-github-pr",
    "current Copilot frontmatter behavior": "internal-copilot-docs-research",
}

COLLISION_CASES = {
    "OIDC policy": "internal-github-governance",
    "OIDC workflow YAML": "internal-github-actions",
    "required-review policy": "internal-github-governance",
    "readiness of one PR": "internal-github-pr",
    "workflow failure": "internal-github-operations",
    "runner-fleet health": "internal-github-operations",
    "reuse-pattern decision": "internal-github-actions",
    "composite-action authoring": "internal-github-action-composite",
}

SPECIALIST_DESCRIPTIONS = {
    "internal-github-strategic": (
        "Use when /internal-github routes a GitHub platform or operating-model "
        "decision that requires option comparison, tradeoff analysis, or "
        "multi-lens strategic framing."
    ),
    "internal-github-governance": (
        "Use when /internal-github routes a GitHub governance decision covering "
        "rulesets, permissions, Apps, Actions permissions, OIDC trust, "
        "secrets, environments, CODEOWNERS, or Copilot policy."
    ),
    "internal-github-operations": (
        "Use when /internal-github routes a GitHub operational request covering "
        "Actions health, runners, audit evidence, reporting, drift, preflight, "
        "rollout validation, or post-rollout proof."
    ),
    "internal-github-actions": (
        "Use when /internal-github routes GitHub Actions workflow authoring or "
        "debugging under `.github/workflows/`, including `workflow_call` and "
        "reuse-pattern selection."
    ),
    "internal-github-action-composite": (
        "Use when /internal-github routes composite-action work under "
        "`.github/actions/`, including inputs, outputs, shell safety, tests, "
        "documentation, and compatibility."
    ),
    "internal-github-pr": (
        "Use when /internal-github routes pull-request lifecycle work covering "
        "creation, body updates, readiness, reviews, merge, or terminal-state "
        "verification."
    ),
}


def load_frontmatter(path: Path) -> dict[str, object]:
    _, raw_frontmatter, _ = path.read_text().split("---", maxsplit=2)
    return yaml.safe_load(raw_frontmatter)


def test_internal_github_router_is_the_only_user_entry_point() -> None:
    assert SKILL_PATH.is_file()
    frontmatter = load_frontmatter(SKILL_PATH)
    assert frontmatter["name"] == "internal-github"
    assert frontmatter["description"] == EXPECTED_ROUTER_DESCRIPTION
    assert frontmatter["user-invocable"] is True
    assert frontmatter.get("disable-model-invocation") is not True


def test_routed_specialists_are_model_invocable() -> None:
    for specialist in ROUTED_SPECIALISTS:
        skill_path = REPO_ROOT / ".github/skills" / specialist / "SKILL.md"
        frontmatter = load_frontmatter(skill_path)
        assert frontmatter["user-invocable"] is False
        assert frontmatter.get("disable-model-invocation") is not True
        assert frontmatter["description"] == SPECIALIST_DESCRIPTIONS[specialist]
        assert "$internal-github" not in frontmatter["description"]
        assert "Do not use for" not in frontmatter["description"]
        assert "manual" not in frontmatter["description"]


def test_internal_github_router_contract() -> None:
    skill_text = SKILL_PATH.read_text()
    normalized_skill_text = " ".join(skill_text.lower().split())

    router_markers = (
        "classify the requested deliverable",
        "## When to use",
        "## Destination table",
        "## Classification algorithm",
        "## Multi-deliverable sequencing",
        "## Completion criteria",
        "/internal-github-strategic",
    )
    for marker in router_markers:
        assert marker.lower() in normalized_skill_text


def test_strategic_skill_has_one_terminal_deliverable() -> None:
    skill_text = STRATEGIC_SKILL_PATH.read_text()

    required_markers = (
        "decision statement",
        "assumptions",
        "viable options",
        "recommendation",
        "tradeoffs",
        "reversibility",
        "validation needs",
    )
    for marker in required_markers:
        assert marker in skill_text.lower()


def test_specialist_bundles_have_no_routing_language() -> None:
    specialist_ids = (
        "internal-github-strategic",
        "internal-github-governance",
        "internal-github-operations",
        "internal-github-pr",
        "internal-github-actions",
        "internal-github-action-composite",
    )
    forbidden_headings = (
        "## Handoffs",
        "## Cross-references",
        "## Referenced skills",
        "## Relationship to adjacent skills",
        "## When not to use",
        "## Anti-patterns",
    )
    for specialist_id in specialist_ids:
        skill_dir = REPO_ROOT / ".github/skills" / specialist_id
        text_paths = [skill_dir / "SKILL.md", *sorted(skill_dir.glob("references/*.md"))]
        for text_path in text_paths:
            text = text_path.read_text()
            if text_path.name == "SKILL.md":
                text = text.split("---", maxsplit=2)[-1]
            for forbidden in forbidden_headings:
                assert forbidden not in text
            for forbidden in (
                "handoff",
                "hand off",
                "manual invocation",
                "return to",
                "next owner",
                "route back",
            ):
                assert forbidden not in text.lower(), (
                    f"{text_path.name} keeps {forbidden}"
                )


def test_terminal_lane_skills_have_single_owner_contracts() -> None:
    required_markers = {
        "internal-github-governance": (
            "scope",
            "control",
            "trust boundary",
            "exception",
            "rollout validation",
        ),
        "internal-github-operations": (
            "confirmed",
            "inferred",
            "rollout",
            "rollback",
            "runner",
            "workflow",
            "audit",
        ),
        "internal-github-pr": (
            "template",
            "actual diff",
            "review state",
            "validation evidence",
            "terminal state",
        ),
    }
    for specialist_id, markers in required_markers.items():
        skill_text = (
            REPO_ROOT / ".github/skills" / specialist_id / "SKILL.md"
        ).read_text().lower()
        for marker in markers:
            assert marker in skill_text, f"{specialist_id} lacks {marker}"


def test_actions_and_composite_have_distinct_terminal_contracts() -> None:
    actions_text = (
        REPO_ROOT / ".github/skills/internal-github-actions/SKILL.md"
    ).read_text().lower()
    composite_text = (
        REPO_ROOT / ".github/skills/internal-github-action-composite/SKILL.md"
    ).read_text().lower()

    for marker in ("workflow behavior", "workflow_call", "reuse-pattern selection"):
        assert marker in actions_text
    for marker in ("action.yml", "input validation", "output", "shell"):
        assert marker in composite_text

    assert "internal-github-action-composite" not in actions_text
    assert "internal-github-actions" not in composite_text


def test_internal_github_interface_names_the_entry_point() -> None:
    interface = yaml.safe_load(AGENT_PATH.read_text())["interface"]

    assert interface == {
        "display_name": "Internal GitHub",
        "short_description": "Official GitHub entry point and router",
        "default_prompt": (
            "Use /internal-github as the entry point for this GitHub request "
            "and invoke the minimum routed specialist set."
        ),
    }


def test_router_uses_one_way_slash_prefixed_invocations() -> None:
    router_text = SKILL_PATH.read_text()

    for destination in (*ROUTED_SPECIALISTS, "internal-copilot-docs-research"):
        assert f"/{destination}" in router_text

    for legacy_marker in (
        "Hand off by reading",
        "handoff by file read",
        "disable-model-invocation",
        "Do not retain ownership",
    ):
        assert legacy_marker not in router_text


def test_specialists_do_not_operationally_invoke_family_siblings() -> None:
    for specialist in ROUTED_SPECIALISTS:
        specialist_dir = REPO_ROOT / ".github/skills" / specialist
        text = "\n".join(
            path.read_text()
            for path in [specialist_dir / "SKILL.md", *specialist_dir.glob("references/*.md")]
        )
        for sibling in ROUTED_SPECIALISTS:
            if sibling == specialist:
                continue
            assert f"/{sibling}" not in text


def test_routing_matrix_classifies_primary_deliverables() -> None:
    matrix_text = " ".join(
        ROUTING_MATRIX_PATH.read_text().lower().replace("`", "").split()
    )

    for scenario, owner in ROUTE_CASES.items():
        assert scenario.lower() in matrix_text
        assert f"/{owner}" in matrix_text

    for scenario, owner in COLLISION_CASES.items():
        assert scenario.lower() in matrix_text
        assert f"/{owner}" in matrix_text


def test_internal_github_strategic_has_agent_metadata() -> None:
    interface = yaml.safe_load(STRATEGIC_AGENT_PATH.read_text())["interface"]

    assert interface["display_name"] == "Internal GitHub Strategic"
    assert interface["short_description"]
    assert interface["default_prompt"]


def test_routing_matrix_covers_positive_negative_and_multi_domain_cases() -> None:
    matrix_text = ROUTING_MATRIX_PATH.read_text()

    for heading in (
        "## Direct routes",
        "## Collision rules",
        "## Multi-deliverable sequencing",
        "## Near misses",
    ):
        assert heading in matrix_text


def test_strategic_framing_keeps_strategic_depth() -> None:
    framing_text = STRATEGIC_FRAMING_PATH.read_text()

    for heading in (
        "## Common lens combinations",
        "## Decision note pattern",
        "## Depth control",
    ):
        assert heading in framing_text


def test_profiles_include_the_github_entry_point() -> None:
    profiles = yaml.safe_load((REPO_ROOT / ".github/repo-profiles.yml").read_text())["profiles"]

    for profile_name, profile in profiles.items():
        skills = set(profile.get("recommended_skills", []))
        has_actions = "skills/internal-github-actions/SKILL.md" in skills
        has_composite = "skills/internal-github-action-composite/SKILL.md" in skills
        if has_actions or has_composite:
            assert "skills/internal-github/SKILL.md" in skills, profile_name
        if has_actions:
            assert has_composite, profile_name


GITHUB_SKILL_PATHS = sorted(
    (REPO_ROOT / ".github/skills").glob("internal-github*/SKILL.md")
)
STRATEGIC_SKILL_ID = "internal-github-strategic"
FORBIDDEN_GENERIC_REFERENCES = (
    "internal-bash-script",
    "internal-python-script",
    "internal-python",
    "internal-python-project",
    "internal-nodejs",
    "internal-nodejs-project",
    "internal-terraform",
)


def test_github_family_shape_and_generic_reference_ban() -> None:
    assert len(GITHUB_SKILL_PATHS) == 7

    for path in GITHUB_SKILL_PATHS:
        skill_text = path.read_text()
        for forbidden_name in FORBIDDEN_GENERIC_REFERENCES:
            assert f"`{forbidden_name}`" not in skill_text


LANE_SKILL_IDS = (
    "internal-github-governance",
    "internal-github-operations",
    "internal-github-pr",
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
            assert references <= {"internal-github"}, (
                f"{text_path.name} references {sorted(references)}"
            )
            assert "handoff" not in skill_text.lower(), (
                f"{text_path.name} still mentions handoffs"
            )


def test_inventory_lists_the_router_and_the_strategic() -> None:
    inventory_text = (REPO_ROOT / ".github/INVENTORY.md").read_text()

    assert ".github/skills/internal-github/SKILL.md" in inventory_text
    assert ".github/skills/internal-github-strategic/SKILL.md" in inventory_text
