# Composite Action Patterns

Use these shapes for `.github/actions/**/action.yml`. Every `run:` step
declares `shell: bash`, starts with `set -euo pipefail`, and reads inputs
from `env:`. `uses:` steps take no `shell:`.

## Contents

- [Minimal action](#minimal-action)
- [Multi-step action with an output](#multi-step-action-with-an-output)
- [State and output rules](#state-and-output-rules)

## Minimal action

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
          echo "target is required" >&2
          exit 1
        fi
```

## Multi-step action with an output

```yaml
name: Package Directory
description: Validate input, create an archive, and expose the archive path
inputs:
  source-directory:
    description: Directory to package
    required: true
outputs:
  archive-path:
    description: Archive path for later workflow steps
    value: ${{ steps.bundle.outputs.archive-path }}
runs:
  using: composite
  steps:
    - name: Validate source directory
      shell: bash
      env:
        SOURCE_DIRECTORY: ${{ inputs.source-directory }}
      run: |
        set -euo pipefail
        if [[ ! -d "$SOURCE_DIRECTORY" ]]; then
          echo "source-directory does not exist: $SOURCE_DIRECTORY" >&2
          exit 1
        fi
        echo "SOURCE_DIRECTORY=$SOURCE_DIRECTORY" >> "$GITHUB_ENV"
    - name: Define archive path
      id: bundle
      shell: bash
      run: |
        set -euo pipefail
        archive_path="$RUNNER_TEMP/source.tgz"
        echo "archive-path=$archive_path" >> "$GITHUB_OUTPUT"
        echo "ARCHIVE_PATH=$archive_path" >> "$GITHUB_ENV"
    - name: Create archive
      shell: bash
      run: |
        set -euo pipefail
        tar -czf "$ARCHIVE_PATH" -C "$SOURCE_DIRECTORY" .
```

## State and output rules

- Declare every caller-visible value under `outputs:` and map it from a step
  with a stable `id` that writes to `$GITHUB_OUTPUT`.
- Use `$GITHUB_ENV` only for step-to-step state inside the action.
- Do not forward values through temp files when `$GITHUB_OUTPUT` or
  `$GITHUB_ENV` expresses the contract.
- Extract long build or deploy logic into a repository script once the action
  becomes orchestration-heavy; see
  [script caller guidance](script-caller-guidance.md).
