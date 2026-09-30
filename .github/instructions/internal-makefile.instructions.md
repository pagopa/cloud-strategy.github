---
description: Makefile review checks for phony targets, recipe syntax, variable expansion, ordering, and failure handling.
applyTo: "**/Makefile,**/*.mk"
excludeAgent: "cloud-agent"
---

# Makefile Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag targets that never create a file of the same name but are missing from
  `.PHONY`.
- Flag recipe lines that do not start with a tab or the configured
  `.RECIPEPREFIX`.
- Flag `$` and `$$` mistakes: in a recipe, `$VAR` expands the Make variable
  `V`, and `$$VAR` passes a shell variable.
- Flag missing prerequisites that break ordering under `make -j`, and output
  files written by more than one target.
- Flag recursive calls that use plain `make` instead of `$(MAKE)`.
- Flag ignored failures, such as a `-` prefix or `|| true`, where the failure
  matters.
- Flag variables read from the environment without a default or a documented
  override.
- Do not assume `make -n` has no side effects. `$(shell ...)` and
  `+`-prefixed lines still run.
