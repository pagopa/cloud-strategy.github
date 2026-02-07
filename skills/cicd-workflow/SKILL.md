---
name: cicd-workflow
description: Create or modify secure GitHub Actions workflows for CI/CD pipelines.
---

# CI/CD Workflow Skill

## When to use
- Creating new GitHub Actions workflows.
- Adding jobs to existing workflows.
- Setting up Terraform CI/CD pipelines.
- Configuring OIDC authentication.

## Mandatory rules
- Use OIDC whenever possible.
- Pin actions to full-length commit SHAs.
- Keep `permissions` minimal.
- Keep step names and operational output in English.

## Terraform workflow template

```yaml
name: Terraform

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  id-token: write
  contents: read
  pull-requests: write

env:
  TF_VERSION: "1.7.0"
  WORKING_DIR: "src/main"

jobs:
  plan:
    name: Plan
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - name: Checkout
        uses: actions/checkout@<FULL_LENGTH_COMMIT_SHA>

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@<FULL_LENGTH_COMMIT_SHA>
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: eu-south-1

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@<FULL_LENGTH_COMMIT_SHA>
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Format check
        run: terraform fmt -check -recursive
        working-directory: ${{ env.WORKING_DIR }}

      - name: Init
        run: terraform init -input=false
        working-directory: ${{ env.WORKING_DIR }}

      - name: Plan
        run: terraform plan -input=false -out=tfplan
        working-directory: ${{ env.WORKING_DIR }}

  apply:
    name: Apply
    needs: plan
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production
    concurrency:
      group: terraform-${{ github.ref }}
      cancel-in-progress: false
    steps:
      - name: Checkout
        uses: actions/checkout@<FULL_LENGTH_COMMIT_SHA>
      # ... apply steps
```

## OIDC snippets

### AWS
```yaml
- uses: aws-actions/configure-aws-credentials@<FULL_LENGTH_COMMIT_SHA>
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: eu-south-1
```

### Azure
```yaml
- uses: azure/login@<FULL_LENGTH_COMMIT_SHA>
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

### GCP
```yaml
- uses: google-github-actions/auth@<FULL_LENGTH_COMMIT_SHA>
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account: ${{ secrets.SA_EMAIL }}
```

## Checklist
- [ ] OIDC is configured.
- [ ] Actions are pinned by SHA.
- [ ] `permissions` are minimal.
- [ ] Production protection/environment is configured.
- [ ] `terraform fmt -check` is included.
