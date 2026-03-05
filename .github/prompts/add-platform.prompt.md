---
description: Add or update a reusable platform/profile definition for repository standards
name: add-platform
agent: agent
argument-hint: action=<add|update> platform_id=<name> primary_stack=<python|java|nodejs|terraform|mixed> goal=<goal> [target_profile=<profile_name>]
---

# Add Platform Profile

## Context
Use this prompt to introduce or update a reusable platform/profile entry without coupling changes to a specific consumer repository.

## Required inputs
- **Action**: ${input:action:add,update}
- **Platform ID**: ${input:platform_id}
- **Primary stack**: ${input:primary_stack:python,java,nodejs,terraform,mixed}
- **Goal**: ${input:goal}
- **Target profile**: ${input:target_profile:minimal}

## Instructions
1. Start from `.github/repo-profiles.yml` and update the profile catalog in a backward-compatible way.
2. Keep naming, descriptions, and routing generic (no consumer-repo paths).
3. Cross-check profile recommendations against existing instruction/prompt/skill files.
4. Use `.github/skills/code-review/SKILL.md` to self-review consistency and anti-patterns before finalizing.

## Minimal example
- Input: `action=add platform_id=analytics-python primary_stack=python goal="Support data-processing repositories" target_profile=backend-python`
- Expected output:
  - A new or updated profile entry with generic description and reusable recommendations.
  - No hardcoded tenant/org/repository references.

## Validation
- Run `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
- Verify all referenced files in the profile exist.
- Verify wording is reusable across unrelated repositories.
