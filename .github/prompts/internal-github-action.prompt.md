---
description: Create or modify a GitHub Actions workflow
name: internal-github-action
agent: agent
argument-hint: action=<create|modify> workflow_name=<name> purpose=<purpose> [triggers=push,pull_request]
---

# GitHub Actions Workflow Task

## Required inputs
- **Action**: ${input:action:create,modify}
- **Workflow name**: ${input:workflow_name}
- **Purpose**: ${input:purpose}
- **Triggers**: ${input:triggers:push,pull_request}

## Instructions
1. Use `.github/skills/internal-cicd-workflow/SKILL.md`.
2. Reuse existing workflow conventions in `.github/workflows/`.
3. Follow `.github/instructions/internal-github-actions.instructions.md` for OIDC, minimal `permissions`, SHA pinning, and image digest pinning.
4. Keep step names in English.
5. If `action=modify`, preserve existing behavior unless explicitly changed.

## Minimal example
- Input: `action=create workflow_name=terraform-ci purpose="Validate terraform on PR" triggers=pull_request`
- Expected output:
  - A workflow file under `.github/workflows/` aligned with repo naming.
  - SHA-pinned actions with release/tag comments and least-privilege `permissions`.
  - Validation steps for the target stack (for example, `terraform fmt -check`).

## Validation
- Validate YAML syntax.
- Validate security policy (OIDC, least privilege, SHA pinning, release/tag comments for SHAs).
- Run local workflow simulation tools when available.
