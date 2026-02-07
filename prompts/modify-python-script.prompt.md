---
description: Modify an existing Python script and align it with standards
name: modify-python-script
agent: agent
argument-hint: target_file=<path> purpose=<short-purpose>
---

# Modify Python Script

## Context
Modify an existing Python script and align it with repository standards.

## Required inputs
- **Target file**: ${input:target_file}
- **Purpose**: ${input:purpose}

## Instructions

1. Use the skill in `.github/skills/script-python/SKILL.md`.
2. Inspect `${input:target_file}` and preserve existing behavior unless changes are requested.
3. Retrofit standards where feasible:
   - module docstring with purpose and usage examples
   - emoji logging and clear error messages
   - early return guard clauses
   - readability-first implementation
4. Add or update unit tests for testable behavior.
5. If external dependencies are used, ensure `requirements.txt` is pinned.

## Validation
- Run syntax checks.
- Run the relevant unit tests for the repository.
