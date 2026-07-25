import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest
import yaml

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
SIMPLE_LANES_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-simple-task/references/simple-lanes.md"
)
CLARIFICATION_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-simple-task/references/clarification-gate.md"
)
PLAN_MODE_PATH = (
    REPO_ROOT
    / ".github/skills/internal-gateway-simple-task/references/plan-mode.md"
)
ROOT_AGENT_PATH = (
    REPO_ROOT / ".github/agents/internal-gateway-simple-task.agent.md"
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


def test_simple_task_bundle_routes_code_changes_to_internal_tdd() -> None:
    skill_text = SKILL_PATH.read_text()
    agent_text = AGENT_PATH.read_text()
    support_routing_text = SUPPORT_ROUTING_PATH.read_text()

    assert "`/internal-tdd`" in skill_text
    assert "load `/internal-tdd` before implementation" in skill_text
    assert "load `/internal-tdd` before implementation" in agent_text
    assert "Load `/internal-tdd`" in support_routing_text


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
    gate_requirements = decision.get("gate_requirements")
    assert isinstance(gate_requirements, dict)
    assert set(gate_requirements.keys()) <= {"validation", "final_evidence"}


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
        row for row in decision["gate_requirements"] if row["gate"] == "clarification"
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


def test_code_simplification_requires_explicit_authorization() -> None:
    skill_text = SKILL_PATH.read_text()

    assert "`/addyosmani-code-simplification`: on-demand method owner" in skill_text
    assert "explicit code-simplification request" in skill_text
    assert "already-approved simplification remediation" in skill_text
    assert "establish a passing behavior baseline" in skill_text
    assert (
        "do not create a simplification pass after unrelated implementation"
        in skill_text
    )
    assert "Only the five referenced skill names appear in this bundle." in skill_text
    assert "addyosmani-code-simplification" not in AGENT_PATH.read_text()


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


def test_default_gate_text_is_compact(capsys) -> None:
    resolve_simple_task.render_gate_text(_full_gate_decision())

    lines = capsys.readouterr().out.splitlines()
    assert lines == [
        "🧭 full-gate: Enable the global Copilot link",
        "🛠️ Scope: Single-lane edit work.",
        "🧪 Check: pytest -q tests/example.py",
        (
            "⚠️ Risk: Task still fits one bounded run but needs the full gate"
            " before action."
        ),
    ]


def test_trivial_gate_text_needs_no_extra_approval(capsys) -> None:
    decision = resolve_simple_task.build_gate_decision(
        task="Fix a typo",
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
        validation_path="make docs-lint",
        validation_gap="",
    )

    resolve_simple_task.render_gate_text(decision)

    output = capsys.readouterr().out
    assert len(output.splitlines()) == 4
    assert "✈️ Action:" not in output
    assert "Readiness Brief:" not in output
    assert "Gate Evidence:" not in output


def test_stopped_gate_text_surfaces_blocker_and_action(capsys) -> None:
    decision = resolve_simple_task.build_gate_decision(
        task="Redesign the workflow",
        lane="edit",
        trivial_kind=None,
        prompt="",
        depth_keywords=[],
        risks=[],
        needs_plan=True,
        needs_review=False,
        needs_critical=False,
        owner_ambiguous=False,
        clarification_overflow=False,
        validation_obvious=False,
        validation_path="make skill-lint",
        validation_gap="",
    )

    resolve_simple_task.render_gate_text(decision)

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 4
    assert lines[0].startswith("🧭 Stop:")
    assert "plan-recommended" in lines[1]
    assert "✈️ Action:" in lines[3]


def test_gate_cli_json_retains_complete_internal_requirements() -> None:
    import json
    import subprocess

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

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["readiness_brief"]["anti_scope"]
    assert payload["readiness_brief"]["stop_conditions"]
    assert payload["gate_requirements"]
    assert "gate_evidence" not in payload


def test_gate_cli_approval_required_stops() -> None:
    import json
    import subprocess

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

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["gate_outcome"] == "stop-with-reason"
    assert "approval-required" in payload["reason_codes"]


def test_simple_task_bundle_documents_compact_projection() -> None:
    skill_text = SKILL_PATH.read_text()
    runtime_text = AGENT_PATH.read_text()

    for marker in [
        "compact user-facing projection",
        "internal readiness record",
        "🎯",
        "🧭",
        "🛠️",
        "🧪",
        "⚠️",
        "✅",
        "💡",
        "✈️",
    ]:
        assert marker in skill_text

    for marker in [
        "gate requirements",
        "no more than four content lines",
        "approval boundary",
    ]:
        assert marker in runtime_text

    assert "normal chat must not dump" in skill_text
    assert "`--format json`" in skill_text


def test_nontrivial_validation_gap_stops_before_execution() -> None:
    decision = resolve_simple_task.build_gate_decision(
        task="Update an unvalidated contract",
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
        validation_path="",
        validation_gap="No local validator",
    )

    assert decision["gate_outcome"] == "stop-with-reason"
    assert decision["next_action"] == "stop"
    assert "validation-gap" in decision["reason_codes"]


def test_security_risk_with_validation_gap_stops_before_execution() -> None:
    decision = resolve_simple_task.build_gate_decision(
        task="Change a security-sensitive policy",
        lane="edit",
        trivial_kind=None,
        prompt="",
        depth_keywords=[],
        risks=["security"],
        needs_plan=False,
        needs_review=False,
        needs_critical=False,
        owner_ambiguous=False,
        clarification_overflow=False,
        validation_obvious=False,
        validation_path="",
        validation_gap="No local security check",
    )

    assert decision["gate_outcome"] == "stop-with-reason"
    assert decision["next_action"] == "stop"
    assert "material-risk:security" in decision["reason_codes"]
    assert "validation-gap" in decision["reason_codes"]


def test_unnamed_obvious_validation_cannot_enable_trivial_skip() -> None:
    decision = resolve_simple_task.build_gate_decision(
        task="Tiny edit",
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
        validation_obvious=True,
        validation_path="",
        validation_gap="",
    )

    assert decision["gate_outcome"] != "trivial-skip"
    assert decision["next_action"] == "stop"
    assert "validation-path-missing" in decision["reason_codes"]


def test_full_gate_does_not_pause_for_unrequested_approval() -> None:
    decision = _full_gate_decision()

    assert decision["gate_outcome"] == "full-gate"
    assert decision["next_action"] == "execute"
    assert decision["needs_explicit_approval"] is False


def test_gate_decision_names_requirements_without_claiming_evidence() -> None:
    decision = _full_gate_decision()

    assert "gate_evidence" not in decision
    requirements = decision["gate_requirements"]
    assert {row["gate"] for row in requirements} == set(resolve_simple_task.GATE_ROWS)
    assert all("expected_evidence" in row for row in requirements)
    assert all("status" not in row for row in requirements)


def test_full_gate_text_has_at_most_four_lines_and_no_extra_approval(capsys) -> None:
    resolve_simple_task.render_gate_text(_full_gate_decision())

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) <= 4
    assert not any("Confirm before" in line for line in lines)
    assert any("pytest -q tests/example.py" in line for line in lines)


def test_stop_text_names_boundary_evidence_and_action(capsys) -> None:
    decision = resolve_simple_task.build_gate_decision(
        task="Broad plan",
        lane="edit",
        trivial_kind=None,
        prompt="",
        depth_keywords=[],
        risks=[],
        needs_plan=True,
        needs_review=False,
        needs_critical=False,
        owner_ambiguous=False,
        clarification_overflow=False,
        validation_obvious=False,
        validation_path="make skill-lint",
        validation_gap="",
    )

    resolve_simple_task.render_gate_text(decision)
    output = capsys.readouterr().out
    lines = output.splitlines()

    assert len(lines) <= 4
    assert "retained plan" in output
    assert "plan-recommended" in output
    assert "Provide" in output
    assert "✈️" in output
    assert "still fits one bounded run" not in output


def test_skill_exposes_each_conditional_reference_with_a_context_pointer() -> None:
    skill_text = SKILL_PATH.read_text()

    for reference in [
        "references/clarification-gate.md",
        "references/plan-mode.md",
        "references/simple-lanes.md",
        "references/support-routing.md",
    ]:
        assert reference in skill_text


def test_runtime_prompt_matches_clarification_and_approval_contract() -> None:
    skill_text = SKILL_PATH.read_text()
    runtime_text = AGENT_PATH.read_text()

    required = [
        "only when a missing bounded fact blocks the active lane",
        "approval boundary",
        "gate requirements",
        "no more than four content lines",
    ]
    for marker in required:
        assert marker in skill_text
        assert marker in runtime_text

    assert "Use `grill-me` when the task is non-trivial" not in runtime_text
    assert "Always surface" not in runtime_text


def test_lane_reference_keeps_gate_evidence_internal() -> None:
    lanes_text = SIMPLE_LANES_PATH.read_text()

    assert "`gate-ledger`" not in lanes_text
    assert "compact user-facing projection" in lanes_text


def test_clarification_reference_has_no_broken_stop_rules_pointer() -> None:
    clarification_text = CLARIFICATION_PATH.read_text()

    assert "Stop rules above" not in clarification_text
    assert "Stop Conditions above" in clarification_text


@pytest.mark.parametrize(
    ("overrides", "expected_outcome"),
    [
        (
            {
                "task": "Answer from one local file",
                "lane": "answer",
                "trivial_kind": "focused-read",
                "validation_path": "Cite the inspected file",
            },
            "trivial-skip",
        ),
        (
            {
                "task": "Fix one reproduced unit-test failure",
                "lane": "diagnose",
                "validation_path": "pytest -q tests/example.py",
            },
            "full-gate",
        ),
        (
            {
                "task": "Review a pull request for findings",
                "lane": "validate",
                "needs_review": True,
                "validation_path": "Inspect the existing diff",
            },
            "stop-with-reason",
        ),
        (
            {
                "task": "Design a cross-cutting governance workflow",
                "lane": "edit",
                "risks": ["architecture", "governance"],
                "validation_gap": "Design direction is not approved",
            },
            "stop-with-reason",
        ),
        (
            {
                "task": "Execute an approval-bound rollout",
                "lane": "edit",
                "approval_required": True,
                "validation_path": "Run the approved rollout check",
            },
            "stop-with-reason",
        ),
    ],
)
def test_gate_boundary_matrix(
    overrides: dict[str, object],
    expected_outcome: str,
) -> None:
    defaults: dict[str, object] = {
        "task": "bounded task",
        "lane": "edit",
        "trivial_kind": None,
        "prompt": "",
        "depth_keywords": [],
        "risks": [],
        "needs_plan": False,
        "needs_review": False,
        "needs_critical": False,
        "owner_ambiguous": False,
        "clarification_overflow": False,
        "needs_clarification": False,
        "validation_obvious": False,
        "validation_path": "",
        "validation_gap": "",
        "approval_required": False,
    }
    defaults.update(overrides)

    decision = resolve_simple_task.build_gate_decision(**defaults)
    assert decision["gate_outcome"] == expected_outcome


def _frontmatter(path: Path) -> dict[str, object]:
    raw_text = path.read_text()
    _, yaml_text, _ = raw_text.split("---", 2)
    parsed = yaml.safe_load(yaml_text)
    assert isinstance(parsed, dict)
    return parsed


def test_skill_and_agent_remain_user_invoked() -> None:
    skill_frontmatter = _frontmatter(SKILL_PATH)
    agent_frontmatter = _frontmatter(ROOT_AGENT_PATH)

    assert skill_frontmatter["disable-model-invocation"] is True
    assert agent_frontmatter["disable-model-invocation"] is True
