---
description: Create or modify GitHub Actions workflow
name: new-github-action
agent: agent
---

# GitHub Actions Workflow

## Context
Create or modify a GitHub Actions workflow for CI/CD.

## Required Inputs
- **Workflow name**: ${input:workflow_name}
- **Purpose**: ${input:purpose}
- **Triggers**: ${input:triggers:push,pull_request}

## Instructions

1. Use the skill in `.github/skills/cicd-workflow/SKILL.md`
2. Check existing workflows in `.github/workflows/`
3. Create the workflow with:
   - OIDC authentication (no long-lived secrets)
   - Minimal permissions
   - Emoji prefixes in step names
   - Environment protection for production deploys

## Cloud-Specific Auth

### AWS
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
```

### Azure
```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
```

### GCP
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
```

## Validation
- Validate YAML syntax
- Check workflow with `act` if available
