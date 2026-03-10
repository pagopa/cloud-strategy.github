PYTHON ?= python3
VALIDATOR := .github/scripts/validate-copilot-customizations.sh
SHELL_SCRIPTS := $(wildcard .github/scripts/*.sh)

.PHONY: help lint validate test all

help:
	@printf '%s\n' 'Targets: lint validate test all'

lint:
	bash -n $(SHELL_SCRIPTS)
	shellcheck -s bash $(SHELL_SCRIPTS)
	$(PYTHON) -m compileall .github/scripts tests

validate:
	bash $(VALIDATOR) --scope root --mode strict

test:
	pytest -q

all: lint validate test
