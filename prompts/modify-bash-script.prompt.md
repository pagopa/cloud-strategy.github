---
description: Modify an existing Bash script and align it with standards
name: modify-bash-script
agent: agent
argument-hint: target_file=<path> purpose=<short-purpose>
---

# Modify Bash Script

## Context
Modify an existing Bash script and align it with repository standards.

## Required inputs
- **Target file**: ${input:target_file}
- **Purpose**: ${input:purpose}

## Instructions

1. Use the skill in `.github/skills/script-bash/SKILL.md`.
2. Inspect `${input:target_file}` and keep existing functional behavior unless changes are requested.
3. Retrofit standards where feasible:
   - Bash shebang and strict mode (`set -euo pipefail`)
   - top comment block with purpose and usage examples
   - emoji logs for runtime states
   - early return guard clauses
   - readability-first structure
4. Do not add unit tests for Bash unless explicitly requested.

## Validation
- Run `bash -n ${input:target_file}`.
- Run `shellcheck -s bash ${input:target_file}` when available.
