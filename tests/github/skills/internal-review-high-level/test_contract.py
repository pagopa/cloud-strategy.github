from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE = REPO_ROOT / ".github/skills/internal-review-high-level"
SKILL = BUNDLE / "SKILL.md"
RUNTIME = BUNDLE / "agents/openai.yaml"
PLAN_AUDIT = BUNDLE / "references/plan-completion-audit.md"
AUDIT_DISPATCH = BUNDLE / "references/audit-dispatch.md"


def test_high_level_has_two_core_routes_and_isolates_plan_audit() -> None:
    text = SKILL.read_text(encoding="utf-8")

    assert "## Branch selection" in text
    assert "### Systems-fit review" in text
    assert "### Architecture and orientation" in text
    assert "## Compatibility-only plan audit" in text
    assert "plan-completion-audit.md" in text
    assert PLAN_AUDIT.exists()


def test_high_level_removes_dispatch_and_duplicate_severity_contracts() -> None:
    text = SKILL.read_text(encoding="utf-8")

    assert "audit-dispatch.md" not in text
    assert not AUDIT_DISPATCH.exists()
    assert "## Severity mappings" not in text
    assert "Do not delegate" in text
    assert "recommendation-only" in text


def test_high_level_runtime_names_real_routes_and_uses_slash_invocation() -> None:
    text = RUNTIME.read_text(encoding="utf-8")

    assert "/internal-review-high-level" in text
    assert "$internal-review-high-level" not in text
    assert "systems-fit" in text
    assert "architecture" in text
    assert "orientation" in text
