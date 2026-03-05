---
description: Create or modify reusable Python scripts with deterministic behavior and tests
name: script-python
agent: agent
argument-hint: action=<create|modify> script_name=<name> purpose=<purpose> [target_path=<path>] [test_scope=<none|unit>]
---

# Create Python Script

## Context
Use this prompt to create or modify Python scripts for governance automation in a reusable, repository-agnostic way.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Target path**: ${input:target_path:.github/scripts}
- **Test scope**: ${input:test_scope:unit,none}

## Instructions
1. Use `.github/skills/script-python/SKILL.md` as implementation baseline.
2. Keep public interfaces explicit (CLI args, input/output schema, exit codes).
3. Keep logs and comments in English.
4. Add/update tests for deterministic logic when `test_scope=unit`.
5. Avoid domain-specific assumptions (consumer repo paths, cloud account IDs, organization names).

## Minimal example
- Input: `action=create script_name=prompt_inventory purpose="List prompts and skill references" target_path=.github/scripts test_scope=unit`
- Expected output:
  - Script with clear argument parsing and deterministic output.
  - Focused unit tests for parsing and formatting logic.

## Validation
- Run `python -m compileall <changed_python_paths>`.
- Run `pytest` for the changed script/tests when present.
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
