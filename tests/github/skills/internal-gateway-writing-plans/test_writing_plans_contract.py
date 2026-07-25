from pathlib import Path

import yaml

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-gateway-writing-plans/SKILL.md"
AGENT_PATH = (
    REPO_ROOT / ".github/skills/internal-gateway-writing-plans/agents/openai.yaml"
)


def _skill_frontmatter() -> dict[str, object]:
    text = SKILL_PATH.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])


def _agent_prompt() -> str:
    payload = yaml.safe_load(AGENT_PATH.read_text(encoding="utf-8"))
    return payload["interface"]["default_prompt"]


def test_skill_requires_hhmm_filenames_for_retained_plans() -> None:
    text = SKILL_PATH.read_text(encoding="utf-8")
    assert "tmp/superpowers/plans/YYYY-MM-DD-HHMM-<feature-name>.md" in text
    assert "tmp/superpowers/specs/" not in text


def test_agent_prompt_mentions_hhmm_filenames_for_plans_only() -> None:
    text = AGENT_PATH.read_text(encoding="utf-8")
    assert "YYYY-MM-DD-HHMM-<feature-name>.md" in text
    assert "specs/" not in text


def test_description_targets_only_approved_implementation_planning() -> None:
    description = str(_skill_frontmatter()["description"])
    assert "approved implementation plan" in description
    assert "retained writing" not in description
    assert "spec writing" not in description


def test_spec_authoring_is_owned_upstream() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    assert "Retained-spec writing stays in the brainstorming lane" in skill
    assert "Use after the user approves implementation-plan writing" in skill
    assert "specs use" not in skill


def test_runtime_prompt_carries_the_narrowed_boundary() -> None:
    prompt = _agent_prompt()
    required = (
        "approved implementation plan",
        "delegated draft",
        "local acceptance gate",
        "internal-gateway-execute-plans",
        "No-Commit Rule",
    )
    for marker in required:
        assert marker in prompt
    assert "specs/" not in prompt


GATES = (
    "Preflight Gate",
    "Delegated Draft Gate",
    "Local Acceptance Gate",
    "Writing Stop",
)


def _assert_in_order(text: str, markers: tuple[str, ...]) -> None:
    positions = [text.index(marker) for marker in markers]
    assert positions == sorted(positions)


def test_skill_uses_ordered_gates_with_completion_criteria() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    _assert_in_order(skill, GATES)
    assert skill.count("Completion criterion:") == len(GATES)


def test_delegated_output_is_draft_until_local_acceptance() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    assert "Delegated output remains draft-only" in skill
    assert "objective checks pass" in skill
    assert "human judgment checks pass" in skill
    assert "revise the draft in place" in skill


def test_accepted_plan_routes_to_the_repository_execution_gateway() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    assert "`internal-gateway-execute-plans`" in skill
    assert "Stop after reporting the accepted plan path" in skill
