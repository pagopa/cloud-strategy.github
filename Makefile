PYTHON ?= python3
SHELL_SCRIPTS := $(wildcard .github/scripts/*.sh)
PYTHON_PATHS := .github/scripts/*.py .github/scripts/lib tests .github/skills
SCRIPTS_RUNNER := ./.github/scripts/run.sh
SCRIPTS_VENV := .github/scripts/.venv

.PHONY: help lint test scripts-bootstrap catalog-check catalog-audit inventory-build token-risks all

help:
	@printf '%s\n' 'Targets: lint test scripts-bootstrap catalog-check catalog-audit inventory-build token-risks all'

scripts-bootstrap:
	@$(SCRIPTS_RUNNER) build_inventory --help >/dev/null

lint:
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	@if command -v shellcheck >/dev/null 2>&1; then shellcheck -s bash $(SHELL_SCRIPTS); else printf '%s\n' 'shellcheck not installed; skipping.'; fi
	$(PYTHON) -m compileall $(PYTHON_PATHS)

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

all: lint test catalog-check
