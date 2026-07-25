import re
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
TESTS_ROOT = REPO_ROOT / "tests"
AGENTS = REPO_ROOT / "AGENTS.md"
INTERNAL_TDD = REPO_ROOT / ".github/skills/internal-tdd/SKILL.md"
INTERNAL_CONTRACT = REPO_ROOT / "INTERNAL_CONTRACT.md"
ANTI_PATTERNS = (
    REPO_ROOT / ".github/skills/internal-python/references/review-anti-patterns.md"
)
SKILL_PATH_PATTERN = re.compile(r"\.github/skills/([a-z0-9-]+)(?:/|[\"'])")
AGENT_PATH_PATTERN = re.compile(r"\.github/agents/([a-z0-9-]+)\.agent\.md")


def test_global_guidance_documents_generic_test_placement_rule() -> None:
    agents_text = AGENTS.read_text(encoding="utf-8")
    internal_tdd_text = INTERNAL_TDD.read_text(encoding="utf-8")
    contract_text = INTERNAL_CONTRACT.read_text(encoding="utf-8")
    anti_patterns_text = ANTI_PATTERNS.read_text(encoding="utf-8")

    assert "repository-root `tests/`" in agents_text
    assert "make the owning\n  source or checked behavior obvious" in agents_text
    assert (
        "When adding tests, keep them under repository-root `tests/`"
        in internal_tdd_text
    )
    assert (
        "test paths under `tests/` should make the covered owner or checked behavior obvious"
        in contract_text
    )
    assert (
        "without paths that make the covered owner or checked behavior obvious"
        in anti_patterns_text
    )


def test_github_owned_python_tests_make_owner_obvious() -> None:
    violations: list[str] = []

    for test_path in sorted(TESTS_ROOT.rglob("test_*.py")):
        if test_path.name == "test_repository_test_layout_contract.py":
            continue

        rel_path = test_path.relative_to(TESTS_ROOT)
        text = test_path.read_text(encoding="utf-8")

        owners = set(SKILL_PATH_PATTERN.findall(text))
        owners.update(AGENT_PATH_PATTERN.findall(text))
        skill_or_agent_owner_is_obvious = (
            "github" in rel_path.parts
            and "skills" in rel_path.parts
            and any(owner in rel_path.parts for owner in owners)
        )
        script_owner_is_obvious = (
            ".github/scripts" in text
            and "github" in rel_path.parts
            and "scripts" in rel_path.parts
        )
        if skill_or_agent_owner_is_obvious or script_owner_is_obvious:
            continue

        if not owners:
            continue

        owner_names = ", ".join(sorted(owners))
        violations.append(
            f"{rel_path} should make one of the referenced owners obvious: {owner_names}"
        )

    assert not violations, "\n".join(violations)
