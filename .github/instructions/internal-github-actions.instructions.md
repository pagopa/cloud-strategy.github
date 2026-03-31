---
description: Security and reliability standards for GitHub Actions workflows with SHA pinning and least privilege.
applyTo: "**/workflows/**"
---

# GitHub Actions Instructions

## Security baseline
- Prefer OIDC over long-lived secrets.
- Pin actions to full-length commit SHAs.
- For each pinned SHA, add an adjacent comment with release/tag and upstream release URL.
- Pin `docker://` references and workflow container images by digest instead of floating tags.
- When an image is pinned by digest, keep the human-readable tag/version in an adjacent comment or nearby reference.
- Keep `permissions` minimal.
- Start with `contents: read` and add write scopes only when the job requires them.
- Avoid `pull_request_target` for untrusted code.
- Pass secrets only through `secrets.*` or protected environments; never hardcode them in `env`.
- Integrate dependency review, SAST, or secret scanning when the workflow is a delivery or release path.

## Workflow baseline
- Start with a descriptive workflow `name` and explicit `on` triggers.
- Set explicit `timeout-minutes`.
- Set `concurrency` when jobs can conflict on shared targets.
- Prefer reusable workflows (`workflow_call`) for repeated pipelines.
- Prefer smaller jobs with explicit `needs` over one monolithic job when phases are logically separate.
- Use `if` conditions deliberately for branch, event, or environment-specific execution.
- Use clear English step names.
- For Terraform jobs: include `fmt -check`, use `-input=false`, and avoid concurrent apply on the same target.
- Keep environment secrets in protected environments when possible.
- Keep cache and artifact usage explicit, deterministic, and scoped to real reuse.
- Use matrix strategy only when it improves confidence/cost tradeoff.
- Use `fail-fast: false` only when full matrix visibility matters more than fast failure.

## Performance and reproducibility
- Use `actions/cache` only for dependencies or outputs with stable keys such as `hashFiles(...)`.
- Prefer `actions/setup-*` built-in caching when it is simpler and equivalent.
- Use `actions/upload-artifact` and `actions/download-artifact` for inter-job handoff instead of rebuilding the same output.
- Default `actions/checkout` to shallow history (`fetch-depth: 1`) unless the job explicitly needs full history.

## Job and step design
- Keep step boundaries meaningful: setup, build, test, package, deploy.
- Use job `outputs` to pass small structured values and artifacts to pass files.
- Prefer workflow or job-level defaults for shell and working directory when repeated.
- Use self-hosted runners only for justified hardware, network, or cost reasons, and note the security/maintenance tradeoff.

## Minimal example
```yaml
name: ci

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

timeout-minutes: 20

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      artifact_name: app-build
    steps:
      - name: Checkout
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2 https://github.com/actions/checkout/releases/tag/v6.0.2
        with:
          fetch-depth: 1

      - name: Restore cache
        uses: actions/cache@0057852bfaa89a56745cba8c7296529d2fc39830 # v4.2.3 https://github.com/actions/cache/releases/tag/v4.2.3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}

      - name: Build
        run: npm ci && npm run build

      - name: Upload artifact
        uses: actions/upload-artifact@65462800fd760344b1a7b4382951275a0abb4808 # v4.6.0 https://github.com/actions/upload-artifact/releases/tag/v4.6.0
        with:
          name: app-build
          path: dist/

  deploy:
    if: github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest
    environment: production
    permissions:
      contents: read
      id-token: write
steps:
  - name: Download artifact
    uses: actions/download-artifact@fa0a91b85d4f404e444e00e005971372dc801d16 # v4.1.8 https://github.com/actions/download-artifact/releases/tag/v4.1.8
    with:
      name: app-build
```
