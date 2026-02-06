---
applyTo: ".github/workflows/**"
---

# GitHub Actions Instructions

## Security
- Use OIDC authentication (no long-lived secrets)
- Pin action versions with SHA: `actions/checkout@v4` → `actions/checkout@<sha>`
- Use `permissions` block with minimal scope

## Structure
```yaml
name: Workflow Name

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4
```

## Naming
- Use emoji prefixes in step names
- 📥 Checkout, 🔐 Auth, 🏗️ Build, 🧪 Test, 🚀 Deploy

## Terraform Jobs
- Always run `terraform fmt -check`
- Use `-input=false` for plan/apply
- Store plan as artifact for apply job
