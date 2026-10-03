# Maintainer entrypoints. Run `make` to list targets.

SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:
MAKEFLAGS += --no-builtin-rules --no-print-directory

TOOLS_RUNNER := ./.github/tools/run.sh
TOOLS_PYTHON := .github/tools/.venv/bin/python
VALIDATE_CODE := ./validate-code.sh
TOOLS_READY := .github/tools/.venv/.make-ready
VALIDATE_CODE_ARGS ?=
CATALOG_FAST_TESTS := tests/github/tools/inventory/test-inventory.py tests/github/tools/common/test-repository.py tests/github/scripts/test-graphify-hooks.py tests/github/tools/test-runner.py tests/test_repository_test_layout_contract.py
CATALOG_FAST_INCLUDE_TOKEN_RISKS ?= 0
MARKDOWNLINT_VERSION := 0.22.1
MARKDOWNLINT_GLOBS := "**/*.md"

.PHONY: help all lint catalog-lint docs-lint test validate-code clean \
	catalog-fast-check catalog-check catalog-audit github-catalog-validation \
	inventory-build token-risks skill-lint skill-change-scope

help: ## List targets
	@awk 'BEGIN { FS = ":.*## " } /^##@ / { printf "\n%s\n", substr($$0, 5) } /^[a-z-]+:.*## / { printf "  %-26s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# The tools venv is rebuilt only when its pinned inputs change.
$(TOOLS_READY): .github/tools/requirements.txt .python-version
	@$(TOOLS_RUNNER) build-inventory --help >/dev/null
	@touch $@

##@ Code

all: lint test catalog-check ## Run lint, tests, and catalog checks

lint: docs-lint catalog-lint ## Run Markdown lint and static code checks

catalog-lint: $(TOOLS_READY) ## Run static code checks (Bash, Python, Ruff, actionlint, entrypoints)
	@$(VALIDATE_CODE) static --compact

docs-lint: ## Run Markdown lint (skipped without npx)
	@if command -v npx >/dev/null 2>&1; then \
		npx --yes --prefer-offline markdownlint-cli2@$(MARKDOWNLINT_VERSION) $(MARKDOWNLINT_GLOBS); \
	else \
		echo "npx not found; skipping Markdown lint."; \
	fi

test: $(TOOLS_READY) ## Run all Python tests in parallel shards
	@$(VALIDATE_CODE) python --compact

validate-code: $(TOOLS_READY) ## Run validate-code.sh; pass options in VALIDATE_CODE_ARGS
	@$(VALIDATE_CODE) $(VALIDATE_CODE_ARGS)

clean: ## Remove local validation caches
	@rm -rf tmp/validate-code .pytest_cache .ruff_cache

##@ Catalog

catalog-fast-check: $(TOOLS_READY) ## Run the quick catalog loop (CATALOG_FAST_INCLUDE_TOKEN_RISKS=1 adds token risks)
	@$(TOOLS_RUNNER) build-inventory --root . --check
	@$(TOOLS_RUNNER) validate-catalog --root .
	@$(TOOLS_RUNNER) validate-internal-skills --root . --strict
	@$(TOOLS_PYTHON) -m pytest -q $(CATALOG_FAST_TESTS)
	@if [[ "$(CATALOG_FAST_INCLUDE_TOKEN_RISKS)" == 1 ]]; then $(TOOLS_RUNNER) detect-token-risks --root .; fi

catalog-check: $(TOOLS_READY) ## Validate the catalog, including token risks
	@$(TOOLS_RUNNER) validate-catalog --root . --include-token-risks

catalog-audit: $(TOOLS_READY) ## Run the deep catalog audit
	@$(TOOLS_RUNNER) validate-catalog --root . --deep

github-catalog-validation: $(TOOLS_READY) ## Run the full catalog gate with a compact summary option
	@$(TOOLS_RUNNER) validate-github-catalog --root .

inventory-build: $(TOOLS_READY) ## Rebuild .github/INVENTORY.md
	@$(TOOLS_RUNNER) build-inventory --root .

token-risks: $(TOOLS_READY) ## Scan for token-budget risks
	@$(TOOLS_RUNNER) detect-token-risks --root .

skill-lint: $(TOOLS_READY) ## Validate internal skills (strict)
	@$(TOOLS_RUNNER) validate-internal-skills --root . --strict

skill-change-scope: $(TOOLS_READY) ## Check that protected skills are unchanged
	@$(TOOLS_RUNNER) validate-skill-change-scope --root .
