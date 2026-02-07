---
applyTo: ".github/workflows/**"
---

# GitHub Actions Instructions

## Security
- Use OIDC whenever possible (avoid long-lived secrets).
- Pin actions to full-length commit SHAs, not only `@v*` tags.
- Define `permissions` with least privilege.
- Avoid `pull_request_target` for untrusted code execution.

## Minimal structure example
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
  ci:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - name: Checkout
        uses: actions/checkout@<FULL_LENGTH_COMMIT_SHA>
```

## Step naming
- Emoji prefixes are allowed.
- Keep step text in English.

## Terraform jobs
- Always run `terraform fmt -check`.
- Use `-input=false` for `terraform plan` and `terraform apply`.
- Store plan output as an artifact before apply.
- Use `concurrency` to avoid concurrent applies on the same target.
