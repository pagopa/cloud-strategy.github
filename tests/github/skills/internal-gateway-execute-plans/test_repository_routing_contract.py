from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)


def test_execute_plan_handoff_targets_a_real_agent() -> None:
    idea = (REPO_ROOT / ".github/agents/internal-gateway-idea.agent.md").read_text()
    target = REPO_ROOT / ".github/agents/internal-gateway-execute-plans.agent.md"
    assert target.is_file()
    assert 'agent: "internal-gateway-execute-plans"' in idea
    assert "compact" not in idea.lower()
    assert "extended" not in idea.lower()


def test_agent_loads_gateway_and_allows_model_invocation() -> None:
    text = (
        REPO_ROOT / ".github/agents/internal-gateway-execute-plans.agent.md"
    ).read_text()
    assert "internal-gateway-execute-plans" in text
    assert "disable-model-invocation: true" not in text
