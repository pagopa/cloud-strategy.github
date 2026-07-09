import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
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


def test_simple_task_skill_has_one_compact_execution_contract() -> None:
    skill_text = SKILL_PATH.read_text()

    assert "## Execution Contract" in skill_text
    assert "## Execution Loop" in skill_text
    assert "## Simple Code Discipline" not in skill_text
    assert "## Generic Executable Behavior Rule" not in skill_text
    assert "## Simple Procedure" not in skill_text


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


def test_trivial_skip_does_not_emit_gate_evidence_ledger() -> None:
    decision = resolve_simple_task.build_gate_decision(
        task="fix typo",
        lane="edit",
        trivial_kind="tiny-edit",
        prompt="",
        depth_keywords=[],
        risks=[],
        needs_plan=False,
        needs_review=False,
        needs_critical=False,
        owner_ambiguous=False,
        clarification_overflow=False,
        validation_obvious=False,
        validation_path="make lint",
        validation_gap="",
    )
    assert decision["gate_outcome"] == "trivial-skip"
    gate_evidence = decision.get("gate_evidence")
    assert gate_evidence is None or (
        isinstance(gate_evidence, dict)
        and set(gate_evidence.keys()) <= {"validation", "final_evidence"}
    ), f"trivial-skip must not emit a 9-row ledger; got {gate_evidence!r}"


def test_full_gate_can_require_clarification() -> None:
    decision = resolve_simple_task.build_gate_decision(
        task="task that needs one bounded clarification",
        lane="unspecified",
        trivial_kind=None,
        prompt="",
        depth_keywords=[],
        risks=[],
        needs_plan=False,
        needs_review=False,
        needs_critical=False,
        owner_ambiguous=False,
        clarification_overflow=False,
        needs_clarification=True,
        validation_obvious=False,
        validation_path="make lint",
        validation_gap="",
    )
    assert decision["gate_outcome"] == "full-gate"
    clarification_row = next(
        row for row in decision["gate_evidence"] if row["gate"] == "clarification"
    )
    assert clarification_row["required"] is True


def test_clarification_overflow_alone_stops() -> None:
    decision = resolve_simple_task.build_gate_decision(
        task="task with too many clarifications",
        lane="unspecified",
        trivial_kind=None,
        prompt="",
        depth_keywords=[],
        risks=[],
        needs_plan=False,
        needs_review=False,
        needs_critical=False,
        owner_ambiguous=False,
        clarification_overflow=True,
        validation_obvious=False,
        validation_path="make lint",
        validation_gap="",
    )
    assert decision["gate_outcome"] == "stop-with-reason"


def test_claim_requirements_return_documented_methods() -> None:
    requirements = resolve_simple_task.resolve_claim_requirements(["fixed"])
    methods = [r["method"] for r in requirements]
    assert "reproduce-loop" in methods
    assert "scope-check" in methods
    assert "superpowers-verification-before-completion" in methods


def test_suggest_does_not_emit_worktree_mapping() -> None:
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SUGGEST_SCRIPT_PATH), "--symptom", "bug", "--symptom", "tdd", "src/app.py"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert "diagnose" in result.stdout
    assert "load-internal-tdd" in result.stdout
    assert "isolate-workspace-needed" not in result.stdout


def test_code_simplification_requires_explicit_authorization() -> None:
    skill_text = SKILL_PATH.read_text()

    assert (
        "`addyosmani-code-simplification`: on-demand method owner"
        in skill_text
    )
    assert "explicit code-simplification request" in skill_text
    assert "already-approved simplification remediation" in skill_text
    assert "establish a passing behavior baseline" in skill_text
    assert (
        "do not create a simplification pass after unrelated implementation"
        in skill_text
    )
    assert "Only the five referenced skill names appear in this bundle." in skill_text
    assert "addyosmani-code-simplification" not in AGENT_PATH.read_text()
