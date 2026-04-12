---
description: Composite-action-specific standards that extend the GitHub Actions baseline with input validation and safe shell patterns.
applyTo: "**/actions/**/action.y*ml"
---

# Composite Action Instructions

## Scope
- This instruction augments `.github/instructions/internal-github-actions.instructions.md`.
- Keep only composite-specific rules here.

## Composite-specific rules
- Define explicit `inputs` and validate required values early.
- Pass `${{ inputs.* }}` through `env:` before shell usage.
- Keep `shell: bash` explicit and start shell blocks with `set -euo pipefail`.
- Move longer logic into dedicated scripts instead of large inline `run:` blocks.
- Preserve backward-compatible input and output contracts when modifying an existing composite action.
