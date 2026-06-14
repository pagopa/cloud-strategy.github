---
description: JSON formatting and consistency standards for registry and configuration data files.
applyTo: "**/authorizations/**/*.json,**/organization/**/*.json,**/src/**/*.json,**/data/**/*.json"
excludeAgent: "cloud-agent"
---

# JSON Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify JSON is valid and structurally consistent with adjacent files in the same family.
- Flag key renames or type changes that break existing consumers.
- Check required fields are present and optional fields are used consistently.
- Report duplicate keys, ambiguous defaults, or contradictory values.
- Verify identifiers, enums, and policy values match repository conventions.
- Flag ordering or formatting drift only when it harms diff readability or tooling.
- Check for embedded secrets or sensitive values that must not be committed.
