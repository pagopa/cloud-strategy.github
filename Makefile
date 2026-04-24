PYTHON_VERSION_FILE := .python-version
PYTHON_VERSION := $(strip $(shell head -n 1 $(PYTHON_VERSION_FILE) 2>/dev/null))
PYTHON_MAJOR_MINOR := $(strip $(shell printf '%s' "$(PYTHON_VERSION)" | awk -F. 'NF >= 2 { print $$1 "." $$2 }'))
PYTHON ?= $(if $(PYTHON_MAJOR_MINOR),python$(PYTHON_MAJOR_MINOR),python3)
SHELL_SCRIPTS := $(wildcard .github/scripts/*.sh)
PYTHON_PATHS := .github/scripts/*.py .github/scripts/lib tests .github/skills
SCRIPTS_RUNNER := ./.github/scripts/run.sh
SCRIPTS_VENV := .github/scripts/.venv
MARKDOWNLINT_VERSION := 0.18.1
MARKDOWNLINT_PATTERNS := "**/*.md" "\#tmp/**"

.PHONY: help python-version-check lint catalog-lint github-catalog-validation test scripts-bootstrap catalog-check catalog-audit inventory-build token-risks skill-lint docs-lint all

help:
	@printf '%s\n' 'Targets: lint catalog-lint github-catalog-validation test scripts-bootstrap catalog-check catalog-audit inventory-build token-risks skill-lint docs-lint all'

python-version-check:
	@test -s "$(PYTHON_VERSION_FILE)" || { printf '%s\n' 'Missing or empty .python-version.' >&2; exit 1; }
	@$(PYTHON) -c 'import pathlib, sys; required = pathlib.Path("$(PYTHON_VERSION_FILE)").read_text().strip(); expected = ".".join(required.split(".")[:2]); actual = f"{sys.version_info.major}.{sys.version_info.minor}"; raise SystemExit(0 if actual == expected else f"Expected $(PYTHON) to resolve to Python {expected} from $(PYTHON_VERSION_FILE) ({required}), got {actual}.")'

scripts-bootstrap: python-version-check
	@$(SCRIPTS_RUNNER) build_inventory --help >/dev/null

lint: python-version-check docs-lint
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	@if command -v shellcheck >/dev/null 2>&1; then shellcheck -s bash $(SHELL_SCRIPTS); else printf '%s\n' 'shellcheck not installed; skipping.'; fi
	$(PYTHON) -m compileall $(PYTHON_PATHS)

catalog-lint: python-version-check
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	$(PYTHON) -m compileall $(PYTHON_PATHS)

github-catalog-validation: python-version-check
	@bash ./github_catalog_validation.sh

test: scripts-bootstrap
	@$(SCRIPTS_VENV)/bin/python -m pytest tests -q

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

docs-lint:
	@if command -v markdownlint-cli2 >/dev/null 2>&1; then \
		markdownlint-cli2 $(MARKDOWNLINT_PATTERNS); \
	elif command -v npx >/dev/null 2>&1; then \
		if [ -n "$${CI:-}" ]; then \
			npx --yes markdownlint-cli2@$(MARKDOWNLINT_VERSION) $(MARKDOWNLINT_PATTERNS); \
		elif npm exec --offline --yes markdownlint-cli2@$(MARKDOWNLINT_VERSION) -- --version >/dev/null 2>&1; then \
			npm exec --offline --yes markdownlint-cli2@$(MARKDOWNLINT_VERSION) -- $(MARKDOWNLINT_PATTERNS); \
		else \
			printf '%s\n' 'markdownlint-cli2 is not installed or cached; skipping markdown lint outside CI.'; \
		fi; \
	else \
		printf '%s\n' 'npx not installed; skipping markdown lint.'; \
	fi

all: lint test catalog-check
