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
    REPO_ROOT / ".github/skills/internal-review-code/references/anti-patterns-python.md"
)
SKILL_PATH_PATTERN = re.compile(r"\.github/skills/([^/]+)/")


def test_global_guidance_documents_generic_test_placement_rule() -> None:
    agents_text = AGENTS.read_text(encoding="utf-8")
    internal_tdd_text = INTERNAL_TDD.read_text(encoding="utf-8")
    contract_text = INTERNAL_CONTRACT.read_text(encoding="utf-8")
    anti_patterns_text = ANTI_PATTERNS.read_text(encoding="utf-8")

    assert "repository-root `tests/`" in agents_text
    assert "make the owning\n  source or checked behavior obvious" in agents_text
    assert "When adding tests, keep them under repository-root `tests/`" in internal_tdd_text
    assert "test paths under `tests/` should make the covered owner or checked behavior obvious" in contract_text
    assert "without paths that make the covered owner or checked behavior obvious" in anti_patterns_text


def test_github_owned_python_tests_make_owner_obvious() -> None:
    violations: list[str] = []

    for test_path in sorted(TESTS_ROOT.rglob("test_*.py")):
        if test_path.name == "test_repository_test_layout_contract.py":
            continue

        rel_path = test_path.relative_to(TESTS_ROOT)
        text = test_path.read_text(encoding="utf-8")

        if ".github/scripts/run.sh" in text:
            if "github" not in rel_path.parts or "scripts" not in rel_path.parts:
                violations.append(
                    f"{rel_path} should make the .github/scripts owner obvious"
                )
            continue

        skill_match = SKILL_PATH_PATTERN.search(text)
        if skill_match is None:
            continue

        skill_name = skill_match.group(1)
        if "github" not in rel_path.parts or "skills" not in rel_path.parts or skill_name not in rel_path.parts:
            violations.append(
                f"{rel_path} should make the .github/skills/{skill_name}/ owner obvious"
            )

    assert not violations, "\n".join(violations)
