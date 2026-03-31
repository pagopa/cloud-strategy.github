---
description: Standards for secure, deterministic GitHub composite actions with explicit input validation.
applyTo: "**/actions/**/action.y*ml,**/workflows/**/action.y*ml"
---

# Composite Action Instructions

## Objective
Define consistent standards for reusable composite actions under `.github/actions/`.

## Mandatory rules
- Keep each composite action focused on one clear responsibility.
- Use explicit `name`, `description`, and typed `inputs`.
- Validate required inputs early and fail fast with clear errors.
- Use English logs and keep output deterministic.
- Avoid embedding secrets in scripts or defaults.
- Prefer shell scripts in `.github/scripts/` for complex logic.

## Security baseline
- Quote all interpolated shell variables.
- Avoid `eval` and untrusted command execution.
- Minimize permissions in calling workflows.
- Document expected trust model in the action description.
- Pin any `docker://` or container image reference by digest and keep the human-readable tag/version nearby.

## Shell guidance
- Keep shell snippets inside composite actions aligned with `.github/instructions/internal-bash.instructions.md`.
- When shell logic grows beyond a short validation or orchestration step, move it into a dedicated Bash script under `.github/scripts/`.

## Minimal example
```yaml
name: "Validate Input"
description: "Validate required inputs before running workflow logic"
inputs:
  target:
    description: "Target environment"
    required: true
runs:
  using: "composite"
  steps:
    - shell: bash
      env:
        TARGET: ${{ inputs.target }}
      run: |
        set -euo pipefail
        if [[ -z "$TARGET" ]]; then
          echo "❌ target is required" >&2
          exit 1
        fi
        echo "✅ target input validated"
```
