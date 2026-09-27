---
description: CODEOWNERS standards for template placeholders and review-enforcement readiness.
applyTo: "**/CODEOWNERS"
excludeAgent: "cloud-agent"
---

# CODEOWNERS Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify entries use valid owner handles and no unresolved template placeholders remain.
- Check rule ordering: GitHub applies the last matching pattern, so broad
  catch-all patterns come first and specific paths after them. Flag a
  catch-all that follows and shadows specific rules.
- Flag duplicate or conflicting patterns that weaken ownership enforcement.
- Confirm critical governance paths have explicit owners.
- Verify wildcard usage does not unintentionally widen or drop review coverage.
- Report syntax issues that cause GitHub CODEOWNERS parsing failures.
- Check that ownership targets are repository-valid users or teams.
