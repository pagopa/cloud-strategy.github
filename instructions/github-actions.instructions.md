---
applyTo: ".github/workflows/**"
---

# GitHub Actions Instructions

## Security baseline
- Prefer OIDC over long-lived secrets.
- Pin actions to full-length commit SHAs.
- Keep `permissions` minimal.
- Avoid `pull_request_target` for untrusted code.

## Workflow baseline
- Set explicit `timeout-minutes`.
- Use clear English step names.
- For Terraform jobs: include `fmt -check`, use `-input=false`, and avoid concurrent apply on the same target.

## Minimal example
```yaml
permissions:
  id-token: write
  contents: read
```
