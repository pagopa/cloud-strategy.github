---
description: JSON review checks for strict grammar, duplicate keys, numeric interoperability, and consumer contract changes.
applyTo: "**/*.json"
excludeAgent: "cloud-agent"
---

# JSON Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag duplicate object keys. Most parsers keep one value silently.
- Flag a UTF-8 byte order mark, non-UTF-8 content, and unpaired surrogate
  escapes.
- Flag comments, trailing commas, `NaN`, and `Infinity` in strict JSON. JSONC
  files such as `.vscode/*.json`, `tsconfig*.json`, and `devcontainer.json`
  allow comments and trailing commas.
- Flag integers outside the range from -(2^53 - 1) to 2^53 - 1 when a
  JavaScript consumer reads them. Suggest a string for large identifiers.
- Do not report key order. JSON object order has no meaning unless a consumer
  in the repository defines one.
- Flag changed keys, types, required properties, identifiers, or enum values
  that break a schema or consumer visible in the repository.
- Flag secrets and contradictory defaults.
- Leave `.tfvars.json` semantics to the Terraform instruction.
