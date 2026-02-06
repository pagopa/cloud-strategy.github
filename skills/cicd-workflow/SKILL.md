---
name: cicd-workflow
description: Create or modify GitHub Actions workflows for CI/CD pipelines. Use for automation, testing, and deployment.
---

# CI/CD Workflow Skill

## When to Use
- Creating new GitHub Actions workflows
- Adding jobs to existing workflows
- Setting up Terraform CI/CD
- Configuring OIDC authentication

## Terraform Workflow Template

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
    name: 📋 Plan
    runs-on: ubuntu-latest
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4

      - name: 🔐 Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: eu-south-1

      - name: 🏗️ Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: 📐 Format Check
        run: terraform fmt -check -recursive
        working-directory: ${{ env.WORKING_DIR }}

      - name: 🔧 Init
        run: terraform init -input=false
        working-directory: ${{ env.WORKING_DIR }}

      - name: 📋 Plan
        run: terraform plan -input=false -out=tfplan
        working-directory: ${{ env.WORKING_DIR }}

  apply:
    name: 🚀 Apply
    needs: plan
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4
      # ... apply steps
```

## OIDC Authentication

### AWS
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: eu-south-1
```

### Azure
```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

### GCP
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account: ${{ secrets.SA_EMAIL }}
```

## Checklist
- [ ] OIDC authentication (no long-lived secrets)
- [ ] Minimal permissions in `permissions` block
- [ ] Emoji prefixes in step names
- [ ] Environment protection for production
- [ ] terraform fmt check included
