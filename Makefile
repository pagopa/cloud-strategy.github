PYTHON_VERSION_FILE := .python-version
PYTHON_VERSION := $(strip $(shell head -n 1 $(PYTHON_VERSION_FILE) 2>/dev/null))
PYTHON_MAJOR_MINOR := $(strip $(shell printf '%s' "$(PYTHON_VERSION)" | awk -F. 'NF >= 2 { print $$1 "." $$2 }'))
PYTHON ?= $(if $(PYTHON_MAJOR_MINOR),python$(PYTHON_MAJOR_MINOR),python3)
SHELL_SCRIPTS := $(wildcard .github/scripts/*.sh)
PYTHON_PATHS := .github/scripts/*.py .github/scripts/lib tests .github/skills
SCRIPTS_RUNNER := ./.github/scripts/run.sh
SCRIPTS_VENV := .github/scripts/.venv
RUFF := $(if $(wildcard $(SCRIPTS_VENV)/bin/ruff),$(SCRIPTS_VENV)/bin/ruff,ruff)
CATALOG_FAST_TESTS := tests/test_inventory_and_consistency.py tests/test_validation_entrypoints_contract.py tests/test_retained_plan_artifact_contract.py tests/github/scripts/test_cli_entrypoints.py
CATALOG_FAST_INCLUDE_TOKEN_RISKS ?= 0
MARKDOWNLINT_VERSION := 0.18.1
MARKDOWNLINT_PATTERNS := "**/*.md" "\#tmp/**" "\#graphify-out/**" "\#.graphify_*" "\#.claude/commands/agent-os/**"

.PHONY: help python-version-check lint catalog-lint catalog-fast-check github-catalog-validation test scripts-bootstrap catalog-check catalog-audit inventory-build token-risks skill-lint docs-lint critical-validate internal-gateway-idea-fast-check all

help:
	@printf '%s\n' 'Targets: lint catalog-lint catalog-fast-check github-catalog-validation test scripts-bootstrap catalog-check catalog-audit inventory-build token-risks skill-lint docs-lint critical-validate all'

python-version-check:
	@test -s "$(PYTHON_VERSION_FILE)" || { printf '%s\n' 'Missing or empty .python-version.' >&2; exit 1; }
	@$(PYTHON) -c 'import pathlib, sys; required = pathlib.Path("$(PYTHON_VERSION_FILE)").read_text().strip(); expected = ".".join(required.split(".")[:2]); actual = f"{sys.version_info.major}.{sys.version_info.minor}"; raise SystemExit(0 if actual == expected else f"Expected $(PYTHON) to resolve to Python {expected} from $(PYTHON_VERSION_FILE) ({required}), got {actual}.")'

scripts-bootstrap: python-version-check
	@$(SCRIPTS_RUNNER) build_inventory --help >/dev/null

lint: python-version-check docs-lint
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	@if command -v shellcheck >/dev/null 2>&1; then shellcheck -s bash $(SHELL_SCRIPTS); else printf '%s\n' 'shellcheck not installed; skipping.'; fi
	$(PYTHON) -m compileall -q $(PYTHON_PATHS)
	$(RUFF) check .github/scripts tools tests

catalog-lint: python-version-check
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	$(PYTHON) -m compileall -q $(PYTHON_PATHS)
	$(RUFF) check .github/scripts tools tests

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

critical-validate: scripts-bootstrap
	@$(SCRIPTS_RUNNER) validate_critical_output --strict --file .github/skills/internal-gateway-critical-master/fixtures/critical_output_valid.md

internal-gateway-idea-fast-check: scripts-bootstrap
	@$(PYTHON) .github/skills/internal-gateway-idea/scripts/audit_workflow.py
	@$(SCRIPTS_RUNNER) validate_internal_skills --skill internal-gateway-idea --strict
	@$(SCRIPTS_VENV)/bin/python -m pytest -q tests/github/skills/internal-gateway-idea

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

PLAN_FOLDER ?=
PLAN_STAGE ?= handoff

PLAN_AUTHORING_CLI := .github/skills/internal-gateway-writing-plans/scripts/plan_authoring.py
PLAN_EXECUTING_CLI := .github/skills/internal-gateway-execute-plans/scripts/plan_execution.py

retained-plan-check: python-version-check
	@case "$(PLAN_STAGE)" in \
		handoff) \
			if [ -z "$(PLAN_FOLDER)" ]; then printf '%s\n' 'PLAN_FOLDER is required for handoff stage (e.g. make retained-plan-check PLAN_STAGE=handoff PLAN_FOLDER=tmp/superpowers/plans/my-plan)' >&2; exit 1; fi; \
			$(PYTHON) $(PLAN_AUTHORING_CLI) handoff-check "$(PLAN_FOLDER)" ;; \
		completion) \
			if [ -z "$(PLAN_FILE)" ] || [ -z "$(STATUS_FILE)" ]; then printf '%s\n' 'PLAN_FILE and STATUS_FILE are required for completion stage (e.g. make retained-plan-check PLAN_STAGE=completion PLAN_FILE=tmp/superpowers/plans/my-plan.md STATUS_FILE=tmp/superpowers/plans/my-plan.DONE.md)' >&2; exit 1; fi; \
			$(PYTHON) $(PLAN_EXECUTING_CLI) completion-check "$(PLAN_FILE)" "$(STATUS_FILE)" --repo-root . ;; \
		*) printf '%s\n' 'PLAN_STAGE must be handoff or completion.' >&2; exit 1 ;; \
	esac

all: lint test catalog-check
