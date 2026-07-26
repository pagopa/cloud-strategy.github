from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SKILL = REPO_ROOT / ".github/skills/internal-tdd/SKILL.md"
CROSS_SKILL_CONTRACT = (
    REPO_ROOT
    / "tests/github/skills/internal-skill-creator/test_cross_skill_invocation_contract.py"
)


def test_operational_cross_skill_calls_use_slash_prefix() -> None:
    text = SKILL.read_text(encoding="utf-8")

    assert "load `/superpowers-test-driven-development`" in text
    assert (
        "`/superpowers-verification-before-completion` before positive claims" in text
    )
    assert '"internal-tdd": {' in CROSS_SKILL_CONTRACT.read_text(encoding="utf-8")


def test_mandatory_routing_has_precedence_over_recommended_guardrails() -> None:
    text = SKILL.read_text(encoding="utf-8")

    assert "`mandatory` takes precedence over `recommended`" in text
    assert "behavior-neutral" in text
    assert "Public-interface changes" in text


def test_undiagnosed_bugs_route_to_debugging_first() -> None:
    text = SKILL.read_text(encoding="utf-8")

    assert "Undiagnosed bugs" in text
    assert "route first to `/internal-debugging`" in text
    assert "reproducer or root cause" in text


def test_regression_only_requires_stop_disclosure_and_recovery() -> None:
    text = SKILL.read_text(encoding="utf-8")

    assert "`regression-only` is not a completed state" in text
    assert "must stop" in text
    assert "disclose the test-first violation" in text
    assert "establish a recovery path" in text
