# Workflow Patterns

Use these shapes as starting points. Adapt names, paths, and pins to the
target repository, and re-verify every pinned SHA against its release.

## Contents

- [Validated manual deploy](#validated-manual-deploy)
- [Reusable workflow](#reusable-workflow)
- [Matrix validation](#matrix-validation)
- [Scheduled housekeeping](#scheduled-housekeeping)

## Validated manual deploy

Use for a manual entrypoint with input validation and a protected environment.

```yaml
name: deploy-service

on:
  workflow_dispatch:
    inputs:
      target:
        description: Deployment target
        required: true
        type: choice
        options:
          - staging
          - production

permissions:
  contents: read

concurrency:
  group: deploy-${{ github.ref }}-${{ inputs.target }}
  cancel-in-progress: false

jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    outputs:
      target: ${{ steps.target.outputs.value }}
    steps:
      - name: Check out repository
        # actions/checkout@v6.0.2
        # https://github.com/actions/checkout/releases/tag/v6.0.2
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
      - name: Validate dispatch input
        id: target
        env:
          TARGET: ${{ inputs.target }}
        run: |
          set -euo pipefail
          case "$TARGET" in
            staging|production) ;;
            *)
              echo "Unsupported target: $TARGET" >&2
              exit 1
              ;;
          esac
          echo "value=$TARGET" >> "$GITHUB_OUTPUT"
      - name: Run pre-deploy checks
        run: make test

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: read
      deployments: write
    environment:
      name: ${{ needs.validate.outputs.target }}
    steps:
      - name: Check out repository
        # actions/checkout@v6.0.2
        # https://github.com/actions/checkout/releases/tag/v6.0.2
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
      - name: Deploy
        env:
          TARGET: ${{ needs.validate.outputs.target }}
        run: |
          set -euo pipefail
          ./scripts/deploy.sh "$TARGET"
```

- Keep deployment permissions and secrets on the deploy job only.
- Use environment protection rules for approval instead of shell logic.
- Add artifacts with explicit `retention-days` only for a reviewed transfer.

## Reusable workflow

Use when several workflows share one or more jobs through `workflow_call`.

```yaml
name: reusable-validate

on:
  workflow_call:
    inputs:
      working-directory:
        description: Directory to validate
        required: false
        type: string
        default: .
    outputs:
      normalized-working-directory:
        description: Sanitized directory forwarded to caller jobs
        value: ${{ jobs.validate.outputs.working-directory }}

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    outputs:
      working-directory: ${{ steps.normalize.outputs.working-directory }}
    steps:
      - name: Check out repository
        # actions/checkout@v6.0.2
        # https://github.com/actions/checkout/releases/tag/v6.0.2
        uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
      - name: Normalize caller input
        id: normalize
        env:
          WORKING_DIRECTORY: ${{ inputs.working-directory }}
        run: |
          set -euo pipefail
          if [[ ! -d "$WORKING_DIRECTORY" ]]; then
            echo "working-directory does not exist: $WORKING_DIRECTORY" >&2
            exit 1
          fi
          echo "working-directory=$WORKING_DIRECTORY" >> "$GITHUB_OUTPUT"
      - name: Run validation
        working-directory: ${{ steps.normalize.outputs.working-directory }}
        run: make test
```

Caller:

```yaml
jobs:
  validate:
    uses: ./.github/workflows/reusable-validate.yml
    with:
      working-directory: services/api
```

- Keep caller inputs small and typed.
- Expose only outputs that downstream jobs use.

## Matrix validation

```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, macos-latest]
    python: ['3.12', '3.13']
```

- Keep steps identical across entries and vary only inputs.
- Add `max-parallel` when runners or external quotas are limited.

## Scheduled housekeeping

```yaml
on:
  schedule:
    - cron: '17 3 * * 1'
```

- Make scheduled jobs idempotent and safe to rerun.
- Set `timeout-minutes` and narrow `permissions`.
- Revalidate state before any destructive mutation and log what changed.
