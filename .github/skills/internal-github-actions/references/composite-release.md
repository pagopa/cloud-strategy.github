# Composite Action Testing, Versioning, and Documentation

Use this reference before publishing or changing the contract of a composite
action.

## Contents

- [Testing](#testing)
- [Versioning](#versioning)
- [README template](#readme-template)

## Testing

1. **Smoke workflow:** call the local action and assert one success-path
   output.

   ```yaml
   jobs:
     smoke:
       runs-on: ubuntu-latest
       steps:
         - name: Check out repository
           # actions/checkout@v6.0.2
           # https://github.com/actions/checkout/releases/tag/v6.0.2
           uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
         - name: Run local action
           id: action
           uses: ./.github/actions/package-directory
           with:
             source-directory: tests/fixtures/package-directory
         - name: Assert archive output
           shell: bash
           env:
             ARCHIVE_PATH: ${{ steps.action.outputs.archive-path }}
           run: |
             set -euo pipefail
             test -n "$ARCHIVE_PATH"
             test -f "$ARCHIVE_PATH"
   ```

2. **Failure path:** run at least one invalid input and assert the action
   fails early with a clear error.
3. **Contract:** keep the README inputs and outputs in sync with `action.yml`,
   and rerun the smoke check after adding or renaming any input or output.

## Versioning

- The full commit SHA is the immutable pin in caller workflows. Release tags
  are human-readable labels; move a major tag only within a compatibility
  line.
- Cut a new major when inputs, outputs, required tools, permissions, or
  visible behavior break callers. Keep deprecated inputs or outputs long
  enough for callers to migrate.
- Before release, confirm: existing `with:` blocks still work, output names
  and meanings are unchanged, failure messages and side effects are
  comparable, and no new runner permissions or tools are required. Any "no"
  is a versioning event.
- In published examples, pair the human tag with the pinned SHA in a comment.

## README template

````md
# <action-name>

One sentence on what the action does and what it does not do.

## Inputs

| Name | Required | Description |
| --- | --- | --- |
| `source-directory` | Yes | Directory to package. |

## Outputs

| Name | Description |
| --- | --- |
| `archive-path` | Archive path produced by the action. |

## Side effects

- Writes an archive under `$RUNNER_TEMP`.
- Requires `tar` on the runner.

## Example

```yaml
steps:
  - uses: ./.github/actions/<action-name>
    with:
      source-directory: dist
```

## Compatibility notes

- Input and output names stay stable within a major release.
- Breaking changes and migration steps are in the release notes.
````
