PYTHON ?= python3
SHELL_SCRIPTS := $(shell find .github -type f -name '*.sh' -print)
PYTHON_PATHS := .github/scripts .github/skills tests

.PHONY: help lint validate test all

help:
	@printf '%s\n' 'Targets: lint validate test all'

lint:
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	@if [ -n "$(SHELL_SCRIPTS)" ]; then shellcheck -s bash $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to shellcheck.'; fi
	$(PYTHON) -m compileall $(PYTHON_PATHS)

validate:
	./.github/scripts/validate-copilot-customizations.sh --scope root --mode strict

test:
	pytest -q

all: lint validate test
