# Minimal Composite Action Template

Use this reference when you need a safe starter template for a reusable
composite action under `.github/actions/`.

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

This template implements the
[composite-action authoring rules](../SKILL.md#composite-action-authoring-rules)
as the smallest safe starting point.
