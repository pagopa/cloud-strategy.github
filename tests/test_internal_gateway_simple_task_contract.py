import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / ".github/skills/internal-gateway-simple-task/SKILL.md"
AGENT_PATH = (
    REPO_ROOT / ".github/skills/internal-gateway-simple-task/agents/openai.yaml"
)
SUPPORT_ROUTING_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-simple-task/references/support-routing.md"
)
RESOLVE_SCRIPT_PATH = (
    REPO_ROOT / ".github/skills/internal-gateway-simple-task/scripts/resolve_simple_task.py"
)
SUGGEST_SCRIPT_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-simple-task/scripts/suggest_support_skills.py"
)

RESOLVE_SPEC = spec_from_file_location("resolve_simple_task", RESOLVE_SCRIPT_PATH)
assert RESOLVE_SPEC is not None and RESOLVE_SPEC.loader is not None
resolve_simple_task = module_from_spec(RESOLVE_SPEC)
sys.modules[RESOLVE_SPEC.name] = resolve_simple_task
RESOLVE_SPEC.loader.exec_module(resolve_simple_task)

SUGGEST_SPEC = spec_from_file_location("suggest_support_skills", SUGGEST_SCRIPT_PATH)
assert SUGGEST_SPEC is not None and SUGGEST_SPEC.loader is not None
suggest_support_skills = module_from_spec(SUGGEST_SPEC)
sys.modules[SUGGEST_SPEC.name] = suggest_support_skills
SUGGEST_SPEC.loader.exec_module(suggest_support_skills)


def test_simple_task_bundle_routes_code_changes_to_internal_tdd() -> None:
    skill_text = SKILL_PATH.read_text()
    agent_text = AGENT_PATH.read_text()
    support_routing_text = SUPPORT_ROUTING_PATH.read_text()

    assert "`internal-tdd`" in skill_text
    assert "load `internal-tdd` before implementation" in skill_text
    assert "load `internal-tdd` before implementation" in agent_text
    assert "Load `internal-tdd`" in support_routing_text


def test_gate_helper_mentions_internal_tdd_for_executable_behavior() -> None:
    decision = resolve_simple_task.build_gate_decision(
        task="Update a validator script",
        lane="edit",
        trivial_kind=None,
        prompt="update code path",
        depth_keywords=[],
        risks=[],
        needs_plan=False,
        needs_review=False,
        needs_critical=False,
        owner_ambiguous=False,
        clarification_overflow=False,
        validation_obvious=True,
        validation_path="pytest -q tests/test_example.py",
        validation_gap="",
    )

    assert "internal-tdd" in decision["readiness_brief"]["executable_behavior"]


def test_support_skill_helper_suggests_internal_tdd_for_code_paths_and_symptom() -> None:
    assert suggest_support_skills.SYMPTOM_METHODS["tdd"][0] == "load-internal-tdd"

    suggestions: dict[str, set[str]] = {}
    suggest_support_skills.suggest_for_path(
        ".github/skills/internal-gateway-simple-task/scripts/resolve_simple_task.py",
        suggestions,
    )

    assert "bundle-contract-check" in suggestions
    assert "load-internal-tdd" in suggestions
    assert "runtime-check" in suggestions
