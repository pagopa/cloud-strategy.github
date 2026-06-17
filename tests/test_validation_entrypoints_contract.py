from __future__ import annotations

from pathlib import Path


def read_text(relative_path: str) -> str:
    return Path(relative_path).read_text(encoding="utf-8")


def test_makefile_lint_target_covers_docs_lint_without_double_running_from_all() -> (
    None
):
    makefile_text = read_text("Makefile")

    assert "lint: python-version-check docs-lint" in makefile_text
    assert "all: lint test catalog-check" in makefile_text
    assert "all: lint test catalog-check docs-lint" not in makefile_text


def test_makefile_uses_quiet_compileall_for_local_catalog_linting() -> None:
    makefile_text = read_text("Makefile")

    assert "$(PYTHON) -m compileall -q $(PYTHON_PATHS)" in makefile_text
    assert "$(PYTHON) -m compileall $(PYTHON_PATHS)" not in makefile_text


def test_makefile_exposes_explicit_catalog_fast_check_entrypoint() -> None:
    makefile_text = read_text("Makefile")

    assert "catalog-fast-check" in makefile_text
    assert "build_inventory --root . --check" in makefile_text
    assert "check_catalog_consistency --root ." in makefile_text
    assert "validate_internal_skills --root . --strict" in makefile_text
    assert "tests/test_inventory_and_consistency.py" in makefile_text
    assert "tests/test_validation_entrypoints_contract.py" in makefile_text
    assert "tests/test_retained_plan_artifact_contract.py" in makefile_text
    assert "tests/github/scripts/test_cli_entrypoints.py" in makefile_text
    assert "CATALOG_FAST_INCLUDE_TOKEN_RISKS=1" in makefile_text


def test_makefile_does_not_expose_legacy_graphify_wrapper_entrypoints() -> None:
    makefile_text = read_text("Makefile")

    assert (
        ".PHONY: help python-version-check lint catalog-lint catalog-fast-check github-catalog-validation test"
        in makefile_text
    )
    assert "graphify-update:" not in makefile_text
    assert "graphify-check:" not in makefile_text
    assert "graphify-prepare:" not in makefile_text
    assert "graphify_update" not in makefile_text


def test_internal_graphify_wrapper_files_are_removed() -> None:
    assert not Path(".github/skills/internal-graphify/SKILL.md").exists()
    assert not Path(".github/skills/internal-graphify/agents/openai.yaml").exists()


def test_docs_lint_target_does_not_require_npm_network_outside_ci() -> None:
    makefile_text = read_text("Makefile")

    assert "MARKDOWNLINT_VERSION := 0.18.1" in makefile_text
    assert "command -v markdownlint-cli2" in makefile_text
    assert "npm exec --offline --yes markdownlint-cli2@" in makefile_text
    assert 'if [ -n "$${CI:-}" ]; then' in makefile_text
    assert "skipping markdown lint outside CI" in makefile_text


def test_github_catalog_validation_workflow_uses_canonical_wrapper_entrypoints() -> (
    None
):
    workflow_text = read_text(".github/workflows/_github-catalog-validation.yml")

    assert (
        "bash ./.github/scripts/github_catalog_validation.sh --skip-token-risks"
        in workflow_text
    )
    assert (
        "bash ./.github/scripts/github_catalog_validation.sh --token-risks-only"
        in workflow_text
    )
    assert "python ./.github/scripts/github_catalog_validation.py" not in workflow_text


def test_graphify_wrapper_shortcut_is_removed_from_validation_wrappers() -> None:
    root_wrapper = read_text("github_catalog_validation.sh")
    scripts_wrapper = read_text(".github/scripts/github_catalog_validation.sh")
    runner_text = read_text(".github/scripts/run.sh")

    assert "--graphify" not in root_wrapper
    assert "--graphify" not in scripts_wrapper
    assert "graphify_update" not in runner_text


def test_runner_dispatch_includes_diagnostic_cli_aliases() -> None:
    runner_text = read_text(".github/scripts/run.sh")

    assert "analyze_copilot_debug_log|analyze_copilot_debug_log.sh" in runner_text
    assert "benchmark_skill_tokens|benchmark_skill_tokens.py" in runner_text


def test_copilot_analyzer_has_single_canonical_wrapper() -> None:
    assert not Path(".github/scripts/analyze_copilot_prompt_exports.py").exists()
    assert not Path(".github/scripts/analyze_copilot_debug_logs.py").exists()
    assert Path("tools/analyze_copilot_debug_log/prompt_exports.py").exists()
    assert Path("tools/analyze_copilot_debug_log/debug_logs.py").exists()
    assert Path("tools/analyze_copilot_debug_log/cli.py").exists()
    assert Path("tools/analyze_copilot_debug_log/__main__.py").exists()
    assert Path("tools/analyze_copilot_debug_log/run.sh").exists()
    assert Path("tools/analyze_copilot_debug_log/requirements.txt").exists()


def test_code_analysis_workflow_smoke_tests_documented_sync_wrappers() -> None:
    workflow_text = read_text(".github/workflows/_code-analysis.yml")

    assert "bash -n .github/scripts/sync_home_ai_resources.sh" in workflow_text
    assert (
        "bash -n .github/skills/local-agent-sync-install-ai-resources/scripts/run.sh"
        in workflow_text
    )


def test_code_analysis_workflow_smoke_tests_runner_diagnostic_clis() -> None:
    workflow_text = read_text(".github/workflows/_code-analysis.yml")

    assert (
        "bash tools/analyze_copilot_debug_log/run.sh prompt-exports --help"
        in workflow_text
    )
    assert (
        "bash tools/analyze_copilot_debug_log/run.sh debug-logs --help"
        in workflow_text
    )
    assert "./.github/scripts/run.sh analyze_copilot_debug_log --help" in workflow_text
    assert "./.github/scripts/run.sh benchmark_skill_tokens --help" in workflow_text
