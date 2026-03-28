PYTHON ?= python3
SHELL_SCRIPTS := $(wildcard .github/scripts/*.sh)

.PHONY: help lint validate test all

help:
	@printf '%s\n' 'Targets: lint validate test all'

lint:
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	@if [ -n "$(SHELL_SCRIPTS)" ]; then shellcheck -s bash $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to shellcheck.'; fi
	$(PYTHON) -m compileall .github/scripts tests

validate:
	@printf '%s\n' 'No repository-wide Copilot customization validator is configured.'

test:
	pytest -q

all: lint validate test
