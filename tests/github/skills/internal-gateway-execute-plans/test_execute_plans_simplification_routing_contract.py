from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL_PATH = REPO_ROOT / ".github/skills/internal-gateway-execute-plans/SKILL.md"
AGENT_PATH = (
    REPO_ROOT / ".github/skills/internal-gateway-execute-plans/agents/openai.yaml"
)


def test_plan_execution_routes_only_preapproved_simplification() -> None:
    skill_text = SKILL_PATH.read_text()

    assert "`addyosmani-code-simplification`: plan-bound method owner" in skill_text
    assert "current approved plan task explicitly requires" in skill_text
    assert "approved review remediation" in skill_text
    assert "never introduce it as cleanup outside the approved plan" in skill_text
    assert "establish the passing behavior baseline" in skill_text
    assert "rerun the same focused validation" in skill_text


def test_plan_execution_agent_does_not_preload_simplification() -> None:
    assert "addyosmani-code-simplification" not in AGENT_PATH.read_text()
