PYTHON_VERSION_FILE := .python-version
PYTHON_VERSION := $(strip $(shell head -n 1 $(PYTHON_VERSION_FILE) 2>/dev/null))
PYTHON_MAJOR_MINOR := $(strip $(shell printf '%s' "$(PYTHON_VERSION)" | awk -F. 'NF >= 2 { print $$1 "." $$2 }'))
PYTHON ?= $(if $(PYTHON_MAJOR_MINOR),python$(PYTHON_MAJOR_MINOR),python3)
SHELL_SCRIPTS := $(wildcard .github/scripts/*.sh)
SKILL_TEST_PATHS := $(wildcard .github/skills/*/tests)
PYTHON_PATHS := .github/scripts/*.py .github/scripts/lib tests $(SKILL_TEST_PATHS)
SCRIPTS_RUNNER := ./.github/scripts/run.sh
SCRIPTS_VENV := .github/scripts/.venv
RUFF := $(if $(wildcard $(SCRIPTS_VENV)/bin/ruff),$(SCRIPTS_VENV)/bin/ruff,ruff)
CATALOG_FAST_TESTS := tests/github/scripts/lib/test_inventory.py tests/github/scripts/lib/test_repo_paths.py tests/github/scripts/test_install_graphify_hooks.py tests/github/scripts/test_run_sh_dispatch.py tests/test_repository_test_layout_contract.py
CATALOG_FAST_INCLUDE_TOKEN_RISKS ?= 0
MARKDOWNLINT_VERSION := 0.22.1
MARKDOWNLINT_PATTERNS := "**/*.md" "\#tmp/**" "\#graphify-out/**" "\#.graphify_*"

.PHONY: help python-version-check lint catalog-lint catalog-fast-check github-catalog-validation test scripts-bootstrap catalog-check catalog-audit inventory-build token-risks skill-lint skill-change-scope docs-lint all

help:
	@printf '%s\n' 'Targets: lint catalog-lint catalog-fast-check github-catalog-validation test scripts-bootstrap catalog-check catalog-audit inventory-build token-risks skill-lint skill-change-scope docs-lint all'

python-version-check:
	@test -s "$(PYTHON_VERSION_FILE)" || { printf '%s\n' 'Missing or empty .python-version.' >&2; exit 1; }
	@$(PYTHON) -c 'import pathlib, sys; required = pathlib.Path("$(PYTHON_VERSION_FILE)").read_text().strip(); expected = ".".join(required.split(".")[:2]); actual = f"{sys.version_info.major}.{sys.version_info.minor}"; raise SystemExit(0 if actual == expected else f"Expected $(PYTHON) to resolve to Python {expected} from $(PYTHON_VERSION_FILE) ({required}), got {actual}.")'

scripts-bootstrap: python-version-check
	@$(SCRIPTS_RUNNER) build_inventory --help >/dev/null

lint: python-version-check docs-lint
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	@if command -v shellcheck >/dev/null 2>&1; then shellcheck -s bash $(SHELL_SCRIPTS); else printf '%s\n' 'shellcheck not installed; skipping.'; fi
	$(PYTHON) -m compileall -q $(PYTHON_PATHS)
	$(RUFF) check .github/scripts tools tests $(SKILL_TEST_PATHS)

catalog-lint: python-version-check
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	$(PYTHON) -m compileall -q $(PYTHON_PATHS)
	$(RUFF) check .github/scripts tools tests $(SKILL_TEST_PATHS)

catalog-fast-check: scripts-bootstrap
	@$(SCRIPTS_RUNNER) build_inventory --root . --check
	@$(SCRIPTS_RUNNER) check_catalog_consistency --root .
	@$(SCRIPTS_RUNNER) validate_internal_skills --root . --strict
	@$(SCRIPTS_VENV)/bin/python -m pytest -q $(CATALOG_FAST_TESTS)
	@if [ "$(CATALOG_FAST_INCLUDE_TOKEN_RISKS)" = "1" ]; then \
		$(SCRIPTS_RUNNER) detect_token_risks --root .; \
	else \
		printf '%s\n' 'Skipping token-risks; set CATALOG_FAST_INCLUDE_TOKEN_RISKS=1 for always-on or shared-contract changes.'; \
	fi

github-catalog-validation: python-version-check
	@$(SCRIPTS_RUNNER) github_catalog_validation --root .

test: scripts-bootstrap
	@$(SCRIPTS_VENV)/bin/python -m pytest -q

catalog-check: scripts-bootstrap
	@$(SCRIPTS_RUNNER) check_catalog_consistency --root . --include-token-risks

catalog-audit: scripts-bootstrap
	@$(SCRIPTS_RUNNER) audit_copilot_catalog --root .

inventory-build: scripts-bootstrap
	@$(SCRIPTS_RUNNER) build_inventory --root .

token-risks: scripts-bootstrap
	@$(SCRIPTS_RUNNER) detect_token_risks --root .

skill-lint: scripts-bootstrap
	@$(SCRIPTS_RUNNER) validate_internal_skills --root . --strict

skill-change-scope: scripts-bootstrap
	@$(SCRIPTS_RUNNER) validate_skill_change_scope --root .

docs-lint:
	@if command -v npx >/dev/null 2>&1; then \
		if [ -n "$${CI:-}" ]; then \
			npx --yes markdownlint-cli2@$(MARKDOWNLINT_VERSION) $(MARKDOWNLINT_PATTERNS); \
		elif npm exec --offline --yes markdownlint-cli2@$(MARKDOWNLINT_VERSION) -- --version >/dev/null 2>&1; then \
			npm exec --offline --yes markdownlint-cli2@$(MARKDOWNLINT_VERSION) -- $(MARKDOWNLINT_PATTERNS); \
		elif command -v markdownlint-cli2 >/dev/null 2>&1 \
			&& markdownlint-cli2 --version 2>/dev/null | grep -Fq "markdownlint-cli2 v$(MARKDOWNLINT_VERSION)"; then \
			markdownlint-cli2 $(MARKDOWNLINT_PATTERNS); \
		else \
			printf '%s\n' 'markdownlint-cli2 is not installed or cached; skipping markdown lint outside CI.'; \
		fi; \
	elif command -v markdownlint-cli2 >/dev/null 2>&1 \
		&& markdownlint-cli2 --version 2>/dev/null | grep -Fq "markdownlint-cli2 v$(MARKDOWNLINT_VERSION)"; then \
		markdownlint-cli2 $(MARKDOWNLINT_PATTERNS); \
	else \
		printf '%s\n' 'npx not installed; skipping markdown lint.'; \
	fi

all: lint test catalog-check
