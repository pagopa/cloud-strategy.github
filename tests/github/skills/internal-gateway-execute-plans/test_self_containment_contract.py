from pathlib import Path
import re

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-gateway-execute-plans"
SKILL = BUNDLE / "SKILL.md"
AGENT = BUNDLE / "agents/openai.yaml"

FORBIDDEN_RUNTIME_OWNERS = (
    "superpowers-executing-plans",
    "superpowers-subagent-driven-development",
    "superpowers-verification-before-completion",
    "superpowers-finishing-a-development-branch",
    "internal-tdd",
    "addyosmani-code-simplification",
)
ALLOWED_STATUSES = ("DONE", "PARTIAL", "BLOCKED", "NEEDS_REVIEW")


def test_bundle_has_only_local_runtime_dependencies() -> None:
    bundle_text = "\n".join(
        path.read_text()
        for path in sorted(BUNDLE.rglob("*"))
        if path.is_file() and path.suffix in {".md", ".yaml", ".py"}
    )
    for owner in FORBIDDEN_RUNTIME_OWNERS:
        assert owner not in bundle_text
    assert "references/execution-contract.md" in SKILL.read_text()
    assert "references/status-contract.md" in SKILL.read_text()
    assert "scripts/plan_execution.py" in SKILL.read_text()


def test_skill_defines_the_complete_execution_state_machine() -> None:
    text = SKILL.read_text()
    phases = (
        "Bind plan",
        "Workspace preflight",
        "Plan review",
        "Task preflight",
        "Test-first gate",
        "Execution unit",
        "Task transition",
        "Plan closeout",
        "Stop",
    )
    positions = [text.index(phase) for phase in phases]
    assert positions == sorted(positions)
    assert all(word in text for word in ("Plan-bound", "Evidence-gated", "Fail-fast"))


def test_status_names_and_replacement_scope_are_exact() -> None:
    text = (BUNDLE / "references/status-contract.md").read_text()
    assert set(re.findall(r"`(DONE|PARTIAL|BLOCKED|NEEDS_REVIEW)`", text)) == set(ALLOWED_STATUSES)
    assert "<plan-basename>.*.md" not in text
    assert "exact allowed sibling filenames" in text


def test_runtime_prompt_projects_the_autonomous_contract() -> None:
    text = AGENT.read_text()
    assert "self-contained" in text
    assert "plan fingerprint" in text
    assert "fresh task-level evidence" in text
    assert "no Git mutation" in text
    assert not any(owner in text for owner in FORBIDDEN_RUNTIME_OWNERS)
