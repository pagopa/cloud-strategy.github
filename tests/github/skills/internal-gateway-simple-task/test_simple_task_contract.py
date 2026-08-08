import json
import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
RESOLVE_SCRIPT_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-simple-task/scripts/resolve_simple_task.py"
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


def test_support_skill_helper_suggests_internal_tdd_for_code_paths_and_symptom() -> (
    None
):
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
    assert "gate_evidence" not in decision


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

    clarification_row = next(
        row for row in decision["gate_requirements"] if row["gate"] == "clarification"
    )
    assert decision["gate_outcome"] == "full-gate"
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
    methods = [requirement["method"] for requirement in requirements]

    assert {
        "reproduce-loop",
        "scope-check",
        "superpowers-verification-before-completion",
    } <= set(methods)


def test_covered_claim_uses_selected_internal_tdd_posture() -> None:
    requirement = next(
        item
        for item in resolve_simple_task.CLAIM_REQUIREMENTS["covered"]
        if item["method"] == "internal-tdd"
    )

    assert "selected posture" in requirement["evidence"]
    assert "failing-then-passing" not in requirement["evidence"]


def test_suggest_cli_returns_runtime_support_without_worktree_mapping() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SUGGEST_SCRIPT_PATH),
            "--symptom",
            "bug",
            "--symptom",
            "tdd",
            "src/app.py",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert "diagnose" in result.stdout
    assert "load-internal-tdd" in result.stdout
    assert "isolate-workspace-needed" not in result.stdout


def _full_gate_decision() -> dict[str, object]:
    return resolve_simple_task.build_gate_decision(
        task="Enable the global Copilot link",
        lane="edit",
        trivial_kind=None,
        prompt="",
        depth_keywords=[],
        risks=[],
        needs_plan=False,
        needs_review=False,
        needs_critical=False,
        owner_ambiguous=False,
        clarification_overflow=False,
        validation_obvious=False,
        validation_path="pytest -q tests/example.py",
        validation_gap="",
    )


def test_render_gate_text_is_compact(capsys) -> None:
    resolve_simple_task.render_gate_text(_full_gate_decision())

    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("🧭 full-gate:")
    assert len(lines) == 4


def test_gate_cli_json_retains_internal_requirements() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RESOLVE_SCRIPT_PATH),
            "gate",
            "--task",
            "Enable the global Copilot link",
            "--lane",
            "edit",
            "--validation-path",
            "pytest -q tests/example.py",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["readiness_brief"]["anti_scope"]
    assert payload["readiness_brief"]["stop_conditions"]
    assert payload["gate_requirements"]
    assert "gate_evidence" not in payload


def test_gate_cli_approval_required_stops() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(RESOLVE_SCRIPT_PATH),
            "gate",
            "--task",
            "Execute an approval-bound rollout",
            "--lane",
            "edit",
            "--approval-required",
            "--validation-path",
            "Run the approved rollout check",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["gate_outcome"] == "stop-with-reason"
    assert "approval-required" in payload["reason_codes"]
