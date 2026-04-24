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
