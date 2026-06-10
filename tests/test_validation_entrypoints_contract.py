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


def test_makefile_exposes_explicit_graphify_update_entrypoint() -> None:
    makefile_text = read_text("Makefile")

    assert (
        ".PHONY: help python-version-check lint catalog-lint catalog-fast-check github-catalog-validation graphify-update graphify-check graphify-prepare"
        in makefile_text
    )
    assert "graphify-update:" in makefile_text
    assert "$(SCRIPTS_RUNNER) graphify_update --root ." in makefile_text
    assert "graphify-check:" in makefile_text
    assert "$(SCRIPTS_RUNNER) graphify_update --root . --check" in makefile_text
    assert "graphify-prepare:" in makefile_text
    assert (
        "$(SCRIPTS_RUNNER) graphify_update --root . --prepare-structural-use"
        in makefile_text
    )


def test_internal_graphify_requires_prepare_before_structural_use() -> None:
    skill_text = read_text(".github/skills/internal-graphify/SKILL.md")
    agent_text = read_text(".github/skills/internal-graphify/agents/openai.yaml")

    assert "Canonical structural-use preparation command: `make graphify-prepare`" in skill_text
    assert "Before every structural Graphify command, run `make graphify-prepare`" in skill_text
    assert "--resolve-node" in skill_text
    assert "Do not pass wrapper-resolved node ids to `graphify path`" in skill_text
    assert "make graphify-prepare" in agent_text
    assert "Treat `graphify path` as best-effort label search only" in agent_text


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


def test_graphify_wrapper_documents_the_graphify_shortcut() -> None:
    root_wrapper = read_text("github_catalog_validation.sh")
    scripts_wrapper = read_text(".github/scripts/github_catalog_validation.sh")
    runner_text = read_text(".github/scripts/run.sh")

    assert "bash ./github_catalog_validation.sh --graphify" in root_wrapper
    assert (
        "bash ./.github/scripts/github_catalog_validation.sh --graphify"
        in scripts_wrapper
    )
    assert "graphify_update" in runner_text
