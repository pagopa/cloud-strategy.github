---
description: Create or modify a GitHub Actions workflow
name: cs-github-action
agent: agent
argument-hint: action=<create|modify> workflow_name=<name> purpose=<purpose> [triggers=push,pull_request]
---

# GitHub Actions Workflow Task

## Context
Create or modify a CI/CD workflow while enforcing security, least privilege, and consistency with existing workflows.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Workflow name**: ${input:workflow_name}
- **Purpose**: ${input:purpose}
- **Triggers**: ${input:triggers:push,pull_request}

## Instructions

1. Use the skill in `.github/skills/cicd-workflow/SKILL.md`.
2. Review existing workflows in `.github/workflows/`.
3. Implement:
   - OIDC authentication
   - minimal `permissions`
   - action pinning with full-length SHAs
   - protected environment for production deploys
4. Keep step names in English.

## Cloud auth snippets

### AWS
```yaml
- uses: aws-actions/configure-aws-credentials@<FULL_LENGTH_COMMIT_SHA>
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
```

### Azure
```yaml
- uses: azure/login@<FULL_LENGTH_COMMIT_SHA>
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
```

### GCP
```yaml
- uses: google-github-actions/auth@<FULL_LENGTH_COMMIT_SHA>
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
```

## Validation
- Validate YAML syntax.
- Validate security policy (`permissions`, SHA pinning, no long-lived secrets).
- Run `act` when available.
