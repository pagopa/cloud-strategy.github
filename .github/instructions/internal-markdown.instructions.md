---
description: Markdown standards for concise, maintainable documentation and explicit command/path formatting.
applyTo: "**/*.md"
excludeAgent: "cloud-agent"
---

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

# Markdown Review Checks

- Verify content is concise, technically accurate, and free of contradictory guidance.
- Flag stale paths, commands, or references that do not match repository reality.
- Check heading structure for clear scanability and stable document navigation.
- Report duplicated policy text that should remain in a single canonical owner.
- Verify examples are minimal, valid, and aligned with current contracts.
- Flag language that implies behavior not enforced by code, tests, or validators.
- Check links and anchors for resolution and maintenance risk.
