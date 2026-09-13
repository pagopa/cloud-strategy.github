import configparser
import re
import shlex
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
TESTS_ROOT = REPO_ROOT / "tests"
SCRIPTS_ROOT = REPO_ROOT / ".github/scripts"
TOOLS_ROOT = REPO_ROOT / ".github/tools"
GITHUB_TESTS_ROOT = TESTS_ROOT / "github"
SKILLS_ROOT = REPO_ROOT / ".github/skills"
MAKEFILE = REPO_ROOT / "Makefile"
PYTEST_CONFIG = REPO_ROOT / "pytest.ini"
SKILL_PATH_PATTERN = re.compile(r"\.github/skills/([a-z0-9-]+)(?:/|[\"'])")
AGENT_PATH_PATTERN = re.compile(r"\.github/agents/([a-z0-9-]+)\.agent\.md")
IGNORED_RUNTIME_ENTRIES = {".pytest_cache", ".venv", "__pycache__", "graphify-out"}
EXPECTED_SCRIPT_FILES = {
    "benchmark-skill-tokens.py",
    "graphify-file-change-hook.sh",
    "install-graphify-hooks.sh",
}
EXPECTED_TOOL_AREAS = {"catalog", "common", "inventory", "skills", "tokens"}


def test_github_automation_layout_is_functional_and_minimal() -> None:
    script_entries = {
        path.name
        for path in SCRIPTS_ROOT.iterdir()
        if path.name not in IGNORED_RUNTIME_ENTRIES
    }
    tool_directories = {
        path.name
        for path in TOOLS_ROOT.iterdir()
        if path.is_dir() and path.name not in IGNORED_RUNTIME_ENTRIES
    }

    assert script_entries == EXPECTED_SCRIPT_FILES
    assert tool_directories == EXPECTED_TOOL_AREAS
    assert (TOOLS_ROOT / "run.sh").is_file()
    assert (TOOLS_ROOT / "requirements.txt").is_file()
    assert not (TOOLS_ROOT / "copilot_tools").exists()


def test_github_tool_tests_mirror_production_areas() -> None:
    test_areas = {
        path.name
        for path in (GITHUB_TESTS_ROOT / "tools").iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }

    assert test_areas == EXPECTED_TOOL_AREAS
    assert (GITHUB_TESTS_ROOT / "scripts").is_dir()


def test_github_owned_python_tests_make_owner_obvious() -> None:
    violations: list[str] = []

    for test_root in (TESTS_ROOT,):
        test_paths = set(test_root.rglob("test_*.py")) | set(
            test_root.rglob("test-*.py")
        )
        for test_path in sorted(test_paths):
            if test_path.name == "test_repository_test_layout_contract.py":
                continue

            rel_path = test_path.relative_to(test_root)
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
            tool_owner_is_obvious = (
                "github" in rel_path.parts and "tools" in rel_path.parts
            )
            if (
                skill_or_agent_owner_is_obvious
                or agent_owner_is_obvious
                or script_owner_is_obvious
                or tool_owner_is_obvious
            ):
                continue

            if not owners:
                continue

            owner_names = ", ".join(sorted(owners))
            violations.append(
                f"{test_path.relative_to(REPO_ROOT)} should make one of the referenced owners obvious: {owner_names}"
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


def test_skill_tests_are_co_located_with_live_skill_bundles() -> None:
    legacy_root = TESTS_ROOT / "github/skills"
    legacy_files = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in legacy_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    orphaned_skill_test_roots = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in SKILLS_ROOT.glob("*/tests")
        if not (path.parent / "SKILL.md").is_file()
    )

    assert not legacy_files, (
        "skill-owned tests and fixtures must live under their bundle; stale paths: "
        + ", ".join(legacy_files)
    )
    assert not orphaned_skill_test_roots, (
        "skill test roots must belong to a live bundle: "
        + ", ".join(orphaned_skill_test_roots)
    )


def test_pytest_config_discovers_root_and_skill_test_roots() -> None:
    config = configparser.ConfigParser()
    config.read(PYTEST_CONFIG, encoding="utf-8")

    assert config["pytest"]["testpaths"].split() == [
        "tests",
        ".github/skills",
    ]
    assert config["pytest"]["python_files"].split() == [
        "test_*.py",
        "test-*.py",
    ]
