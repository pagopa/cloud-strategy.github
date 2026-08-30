# CI Assets

Use this reference only to inspect or route the expected documentation CI assets. Do not author, edit, or duplicate GitHub Actions YAML from this skill.

## Expected Assets

Expected asset paths are host-configured through `expected_assets` in the optional knowledge config. `audit` reports whether each configured path is present. Presence or absence is evidence only; this skill never creates or repairs those files. Missing optional config yields an empty CI-asset report.

## Input And Exit-Code Contract

The composite action accepts `manifest` and `repo-root`. `manifest` is a repository-relative knowledge-map path and defaults to `docs/knowledge-map.yaml`. `repo-root` is the target repository root and defaults to `.`.

The action runner uses this exit-code contract: exit code `0` when the manifest exists, parses, and every declared component path exists; exit code `1` when the manifest is missing, unreadable, or a declared path is absent. The workflow may continue after a non-zero knowledge-structure check so a later summary can consume the same log path.

## Delegation

- Route workflow and composite-action authoring, inputs, outputs, and YAML structure to `/internal-github-actions`.
- Route the self-contained Python runner behind the action to `/internal-python-script`.
- Keep this skill report-only for CI assets. Do not write `.github/actions/**`, `.github/workflows/**`, or the action runner from a knowledge authoring branch.
