from __future__ import annotations

from pathlib import Path

TEST_OWNERS = {
    "tests/github/scripts/test_cli_entrypoints.py": {
        ".github/scripts/github_catalog_validation.py",
        ".github/scripts/audit_copilot_catalog.py",
        ".github/scripts/build_inventory.py",
        ".github/scripts/check_catalog_consistency.py",
        ".github/scripts/detect_token_risks.py",
        ".github/scripts/graphify_update.py",
        ".github/scripts/sync_copilot_catalog.py",
        ".github/scripts/validate_internal_skills.py",
    },
    "tests/github/scripts/lib/test_fingerprinting.py": {
        ".github/scripts/lib/fingerprinting.py",
    },
    "tests/github/scripts/lib/test_internal_skills.py": {
        ".github/scripts/lib/internal_skills.py",
    },
    "tests/github/scripts/lib/test_shared.py": {
        ".github/scripts/lib/shared.py",
    },
    "tests/test_inventory_and_consistency.py": {
        ".github/scripts/lib/catalog_checks.py",
        ".github/scripts/lib/inventory.py",
    },
    "tests/test_home_ai_resources_sync.py": {
        ".github/scripts/sync_home_ai_resources.py",
    },
    "tests/test_sync_and_token_risks.py": {
        ".github/scripts/lib/syncing.py",
        ".github/scripts/lib/token_risks.py",
    },
    "tests/github/scripts/test_benchmark_skill_tokens.py": {
        ".github/scripts/benchmark_skill_tokens.py",
    },
    "tests/github/scripts/test_analyze_copilot_debug_logs.py": {
        ".github/scripts/analyze_copilot_debug_logs.py",
    },
}


def test_all_repo_owned_python_scripts_have_declared_test_owners() -> None:
    source_scripts = {
        path.as_posix()
        for path in Path(".github/scripts").rglob("*.py")
        if ".venv" not in path.parts
        and "__pycache__" not in path.parts
        and path.name != "__init__.py"
    }
    declared_scripts = {
        script_path
        for covered_scripts in TEST_OWNERS.values()
        for script_path in covered_scripts
    }

    assert declared_scripts == source_scripts
    assert all(Path(script_path).is_file() for script_path in declared_scripts)
    assert all(Path(test_path).is_file() for test_path in TEST_OWNERS)
