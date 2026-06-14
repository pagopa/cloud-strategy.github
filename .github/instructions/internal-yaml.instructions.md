---
description: YAML formatting and clarity conventions for stable, maintainable configuration files.
applyTo: "**/*.yml,**/*.yaml"
excludeAgent: "cloud-agent"
---

# YAML Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify YAML is syntactically valid with stable indentation and scalar usage.
- Flag duplicate keys, ambiguous merges, or anchor misuse.
- Check schema-sensitive fields for type and key-name correctness.
- Report values that change runtime behavior without explicit intent.
- Verify environment-specific overrides do not leak across scopes.
- Flag embedded secrets, credentials, or sensitive identifiers.
- Check comments and structure only when they affect maintainability or correctness.
