PYTHON ?= python3
SHELL_SCRIPTS := $(wildcard .github/scripts/*.sh)
PYTHON_PATHS := .github/scripts .github/skills

.PHONY: help lint all

help:
	@printf '%s\n' 'Targets: lint all'

lint:
	@if [ -n "$(SHELL_SCRIPTS)" ]; then bash -n $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to lint.'; fi
	@if [ -n "$(SHELL_SCRIPTS)" ]; then shellcheck -s bash $(SHELL_SCRIPTS); else printf '%s\n' 'No Bash scripts to shellcheck.'; fi
	$(PYTHON) -m compileall $(PYTHON_PATHS)

all: lint
