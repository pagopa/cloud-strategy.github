---
description: Makefile conventions for deterministic targets, readable recipes, and explicit phony declarations.
applyTo: "**/Makefile,**/*.mk"
excludeAgent: "cloud-agent"
---

# Makefile Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify target names and dependencies reflect deterministic build order.
- Flag missing `.PHONY` declarations for non-file targets.
- Check recipe commands for shell safety and clear failure behavior.
- Report hidden environment coupling that breaks reproducible runs.
- Verify variable defaults and overrides are explicit and non-ambiguous.
- Check parallelism-sensitive targets for race-prone shared artifacts.
- Flag undocumented side effects in commonly used targets.
