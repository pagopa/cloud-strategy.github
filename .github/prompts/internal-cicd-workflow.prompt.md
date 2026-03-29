---
description: Create or modify reusable GitHub Actions workflows for CI/CD and governance automation
name: internal-cicd-workflow
agent: agent
argument-hint: action=<create|modify> workflow_name=<name> purpose=<purpose> trigger=<push|pull_request|schedule|workflow_dispatch>
---

# CI/CD Workflow

## Context
Use this prompt to create or modify GitHub Actions workflows that remain portable across repositories.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Workflow name**: ${input:workflow_name}
- **Purpose**: ${input:purpose}
- **Trigger**: ${input:trigger:push,pull_request,schedule,workflow_dispatch}

## Instructions
1. Use `.github/skills/internal-cicd-workflow/SKILL.md` and `.github/instructions/internal-github-actions.instructions.md`.
2. Pin external actions to full commit SHA.
3. Add adjacent release/tag references for each pinned action.
4. Keep workflow steps generic and avoid repository-specific business logic.
5. Use least privilege for `permissions`.

## Minimal example
- Input: `action=create workflow_name=validate-customizations purpose="Run static checks on prompt/skill files" trigger=pull_request`
- Expected output:
  - New workflow with scoped triggers, pinned actions, and minimal permissions.
  - Validation steps aligned with repository scripts.

## Validation
- Run YAML validation and check syntax errors via editor/linter.
- Run `python3 .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
- Confirm action pinning and comments comply with repository rules.
