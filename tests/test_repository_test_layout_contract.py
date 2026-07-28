import re
import shlex
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
TESTS_ROOT = REPO_ROOT / "tests"
MAKEFILE = REPO_ROOT / "Makefile"
SKILL_PATH_PATTERN = re.compile(r"\.github/skills/([a-z0-9-]+)(?:/|[\"'])")
AGENT_PATH_PATTERN = re.compile(r"\.github/agents/([a-z0-9-]+)\.agent\.md")


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
        agent_owner_is_obvious = (
            "github" in rel_path.parts
            and "agents" in rel_path.parts
            and any(
                owner in rel_path.parts or owner.replace("-", "_") in test_path.stem
                for owner in owners
            )
        )
        script_owner_is_obvious = (
            ".github/scripts" in text
            and "github" in rel_path.parts
            and "scripts" in rel_path.parts
        )
        if (
            skill_or_agent_owner_is_obvious
            or agent_owner_is_obvious
            or script_owner_is_obvious
        ):
            continue

        if not owners:
            continue

        owner_names = ", ".join(sorted(owners))
        violations.append(
            f"{rel_path} should make one of the referenced owners obvious: {owner_names}"
        )

    assert not violations, "\n".join(violations)


def test_catalog_fast_check_lists_existing_test_files() -> None:
    makefile_text = MAKEFILE.read_text(encoding="utf-8")
    line = next(
        line
        for line in makefile_text.splitlines()
        if line.startswith("CATALOG_FAST_TESTS :=")
    )
    test_paths = shlex.split(line.split(":=", 1)[1].strip())
    missing_paths = [path for path in test_paths if not (REPO_ROOT / path).is_file()]

    assert not missing_paths, (
        f"catalog-fast-check lists missing tests: {', '.join(missing_paths)}"
    )
