---
name: internal-composite-action
description: Use when creating or modifying a reusable GitHub composite action under `.github/actions/`, especially for shared step logic that should not become a full reusable workflow.
---

# Composite Action Skill

## When to use
- Create a new reusable composite action under `.github/actions/`.
- Modify an existing composite action and preserve compatibility.
- Standardize input validation and shell execution patterns.

## Composite action vs reusable workflow

| Factor | Composite action | Reusable workflow |
|---|---|---|
| Granularity | Step-level (runs inside a job) | Job-level (runs as separate job) |
| Secrets access | Inherited from caller job | Must be passed explicitly |
| Outputs | Step outputs only | Workflow outputs |
| Best for | Shared validation, setup, formatting | Full CI/CD pipelines, multi-job orchestration |

**Rule of thumb**: if the reusable unit is a few steps → composite action. If it is an entire job with its own runner → reusable workflow.

## Mandatory rules
- Keep the action focused on one responsibility.
- Define explicit `name`, `description`, and typed `inputs`.
- Validate required inputs early and fail fast.
- Use English logs and deterministic output.
- Prefer shell scripts for complex logic instead of large inline blocks.
- Pass expression inputs via `env` — never interpolate `${{ }}` directly in `run:`.
- Quote shell variables. Avoid `eval` and untrusted command execution.
- Keep secrets out of defaults and logs.

## Minimal template
```yaml
name: Validate Input
description: Validate required inputs before action logic
inputs:
  target:
    description: Target environment
    required: true
runs:
  using: composite
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
        echo "✅ input validated"
```

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Interpolating `${{ inputs.x }}` directly in `run:` | Script injection via crafted input values | Pass through `env:` and use `"$VAR"` in shell |
| Missing `set -euo pipefail` in `run:` blocks | Silent failures, partial execution | Always set strict mode as first line |
| Large inline `run:` blocks (>30 lines) | Hard to read, test, and lint | Extract to a shell script under the action directory |
| No input validation before logic | Cryptic downstream errors | Validate and fail fast at the top of the first step |
| Forgetting `shell: bash` on composite steps | Defaults to `sh` on some runners — different behavior | Always explicit `shell: bash` |
| Breaking existing input contract | Callers silently break without warning | Add new inputs with defaults; deprecate old ones gradually |

## Cross-references
- **internal-cicd-workflow** (`.github/skills/internal-cicd-workflow/SKILL.md`): for workflows that call composite actions.
- **internal-script-bash** (`.github/skills/internal-script-bash/SKILL.md`): for extracted shell scripts inside the action.

## Validation
- Inputs documented and validated.
- Shell code is safe (`set -euo pipefail`, quoted vars).
- No secret leakage in logs/defaults.
- Backward compatibility preserved when modifying existing action.
