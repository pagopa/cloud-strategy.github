import re
from pathlib import Path


REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
TESTS_ROOT = REPO_ROOT / "tests"
INTERNAL_CONTRACT = REPO_ROOT / "INTERNAL_CONTRACT.md"
ANTI_PATTERNS = (
    REPO_ROOT / ".github/skills/internal-review-code/references/anti-patterns-python.md"
)
SKILL_PATH_PATTERN = re.compile(r"\.github/skills/([^/]+)/")


def test_contract_documents_discoverable_mirrored_test_paths() -> None:
    contract_text = INTERNAL_CONTRACT.read_text(encoding="utf-8")
    anti_patterns_text = ANTI_PATTERNS.read_text(encoding="utf-8")

    assert "testing-python-tests-mirror-source-layout" in contract_text
    assert "tests/github/..." in contract_text
    assert "flat root-level files such as `tests/test_*.py` are reserved" in contract_text
    assert "discoverable mirrored source paths" in anti_patterns_text


def test_github_owned_python_tests_live_in_mirrored_paths() -> None:
    violations: list[str] = []

    for test_path in sorted(TESTS_ROOT.rglob("test_*.py")):
        if test_path.name == "test_repository_test_layout_contract.py":
            continue

        rel_path = test_path.relative_to(TESTS_ROOT)
        text = test_path.read_text(encoding="utf-8")

        if ".github/scripts/run.sh" in text:
            if rel_path.parts[:2] != ("github", "scripts"):
                violations.append(
                    f"{rel_path} should live under tests/github/scripts/ for .github/scripts coverage"
                )
            continue

        skill_match = SKILL_PATH_PATTERN.search(text)
        if skill_match is None:
            continue

        expected_prefix = ("github", "skills", skill_match.group(1))
        if rel_path.parts[:3] != expected_prefix:
            expected = "/".join(expected_prefix)
            violations.append(
                f"{rel_path} should live under tests/{expected}/ for .github/skills/{skill_match.group(1)}/ coverage"
            )

    assert not violations, "\n".join(violations)
