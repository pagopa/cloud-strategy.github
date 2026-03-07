---
description: Add or update a reusable reporting script for repository maintenance and governance
name: TechAIAddReportScript
agent: agent
argument-hint: action=<create|modify> script_name=<name> purpose=<purpose> output_format=<json|yaml|md|txt> [target_path=<path>]
---

# Add Reporting Script

## Context
Use this prompt to add or update a reporting script that supports governance and maintenance workflows in a reusable way.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Script name**: ${input:script_name}
- **Purpose**: ${input:purpose}
- **Output format**: ${input:output_format:json,yaml,md,txt}
- **Target path**: ${input:target_path:.github/scripts}

## Instructions
1. Use `.github/skills/tech-ai-script-python/SKILL.md` as the implementation baseline.
2. Keep input/output contracts explicit and deterministic.
3. Keep logs and messages in English.
4. Avoid references to any specific consumer repository, tenant, subscription, or billing scope.
5. If behavior changes, update related prompt/instruction references accordingly.

## Minimal example
- Input: `action=create script_name=inventory_report purpose="Summarize customization assets" output_format=json target_path=.github/scripts`
- Expected output:
  - New script with clear CLI parameters, deterministic output, and error handling.
  - Optional tests for the parsing/formatting logic when practical.

## Validation
- Run relevant script checks (`python -m compileall`, `pytest` if tests exist).
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
- Verify script output does not leak secrets or environment-specific identifiers.
