import re
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-execute-plans"
SKILL = BUNDLE / "SKILL.md"
AGENT = BUNDLE / "agents/openai.yaml"

REQUIRED_CORE_OWNERS = (
    "/superpowers-executing-plans",
    "/internal-tdd",
    "/superpowers-verification-before-completion",
    "/addyosmani-code-simplification",
)
ALLOWED_STATUSES = ("DONE", "PARTIAL", "BLOCKED", "NEEDS_REVIEW")


def test_bundle_delegates_execution_and_keeps_local_guardrails() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    runtime = AGENT.read_text(encoding="utf-8")
    combined = f"{skill}\n{runtime}"
    assert all(owner in combined for owner in REQUIRED_CORE_OWNERS)
    assert "self-contained" not in combined
    assert "references/execution-contract.md" in skill
    assert "references/status-contract.md" in skill
    assert "scripts/plan_execution.py" in skill


def test_status_names_and_replacement_scope_are_exact() -> None:
    text = (BUNDLE / "references/status-contract.md").read_text()
    assert set(re.findall(r"`(DONE|PARTIAL|BLOCKED|NEEDS_REVIEW)`", text)) == set(
        ALLOWED_STATUSES
    )
    assert "<plan-basename>.*.md" not in text
    assert "exact allowed sibling filenames" in text


def test_runtime_prompt_projects_the_delegated_contract() -> None:
    text = AGENT.read_text(encoding="utf-8")
    assert all(owner in text for owner in REQUIRED_CORE_OWNERS)
    assert "plan fingerprint" in text
    assert "fresh task-level evidence" in text
    assert "no Git mutation" in text


def test_execution_contract_recovers_before_stopping_on_external_failures() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    execution = (BUNDLE / "references/execution-contract.md").read_text()
    status = (BUNDLE / "references/status-contract.md").read_text()
    runtime = AGENT.read_text(encoding="utf-8")
    combined = "\n".join((skill, execution, status, runtime))
    required = (
        "baseline/final delta",
        "bounded recovery",
        "Failure Classification",
        "Recovery Attempts",
        "pre-existing or unrelated",
        "concise user-facing report",
    )
    for marker in required:
        assert marker in combined

    assert "NEEDS_REVIEW" in status
    assert "task-local regression" in execution
