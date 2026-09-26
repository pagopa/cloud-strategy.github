PYTHON_VERSION_FILE := .python-version
PYTHON_VERSION := $(strip $(shell head -n 1 $(PYTHON_VERSION_FILE) 2>/dev/null))
PYTHON_MAJOR_MINOR := $(strip $(shell printf '%s' "$(PYTHON_VERSION)" | awk -F. 'NF >= 2 { print $$1 "." $$2 }'))
PYTHON ?= $(if $(PYTHON_MAJOR_MINOR),python$(PYTHON_MAJOR_MINOR),python3)
SHELL_SCRIPTS := $(wildcard .github/scripts/*.sh) .github/tools/run.sh
SKILL_TEST_PATHS := $(wildcard .github/skills/*/tests)
PYTHON_PATHS := .github/scripts/*.py .github/tools/common .github/tools/inventory .github/tools/catalog .github/tools/skills .github/tools/tokens tests $(SKILL_TEST_PATHS)
TOOLS_RUNNER := ./.github/tools/run.sh
TOOLS_VENV := .github/tools/.venv
RUFF := $(if $(wildcard $(TOOLS_VENV)/bin/ruff),$(TOOLS_VENV)/bin/ruff,ruff)
CATALOG_FAST_TESTS := tests/github/tools/inventory/test-inventory.py tests/github/tools/common/test-repository.py tests/github/scripts/test-graphify-hooks.py tests/github/tools/test-runner.py tests/test_repository_test_layout_contract.py
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
	@$(TOOLS_RUNNER) build-inventory --help >/dev/null

lint: python-version-check docs-lint
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	@if command -v shellcheck >/dev/null 2>&1; then shellcheck -s bash $(SHELL_SCRIPTS); else printf '%s\n' 'shellcheck not installed; skipping.'; fi
	$(PYTHON) -m compileall -q $(PYTHON_PATHS)
	$(RUFF) check .github/scripts .github/tools tools tests $(SKILL_TEST_PATHS)

catalog-lint: python-version-check
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	$(PYTHON) -m compileall -q $(PYTHON_PATHS)
	$(RUFF) check .github/scripts .github/tools tools tests $(SKILL_TEST_PATHS)

catalog-fast-check: scripts-bootstrap
	@$(TOOLS_RUNNER) build-inventory --root . --check
	@$(TOOLS_RUNNER) validate-catalog --root .
	@$(TOOLS_RUNNER) validate-internal-skills --root . --strict
	@$(TOOLS_VENV)/bin/python -m pytest -q $(CATALOG_FAST_TESTS)
	@if [ "$(CATALOG_FAST_INCLUDE_TOKEN_RISKS)" = "1" ]; then \
		$(TOOLS_RUNNER) detect-token-risks --root .; \
	else \
		printf '%s\n' 'Skipping token-risks; set CATALOG_FAST_INCLUDE_TOKEN_RISKS=1 for always-on or shared-contract changes.'; \
	fi

github-catalog-validation: python-version-check
	@$(TOOLS_RUNNER) validate-github-catalog --root .

test: scripts-bootstrap
	@$(TOOLS_VENV)/bin/python -m pytest -q

catalog-check: scripts-bootstrap
	@$(TOOLS_RUNNER) validate-catalog --root . --include-token-risks

catalog-audit: scripts-bootstrap
	@$(TOOLS_RUNNER) validate-catalog --root . --deep

inventory-build: scripts-bootstrap
	@$(TOOLS_RUNNER) build-inventory --root .

token-risks: scripts-bootstrap
	@$(TOOLS_RUNNER) detect-token-risks --root .

skill-lint: scripts-bootstrap
	@$(TOOLS_RUNNER) validate-internal-skills --root . --strict

skill-change-scope: scripts-bootstrap
	@$(TOOLS_RUNNER) validate-skill-change-scope --root .

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
