# GitHub Actions review target

The static review must follow the chain from the pull-request event through
the workflow and local composite action to the publishing script.

Material observations are identified by these IDs:

- `WORKFLOW_PERMISSIONS`: job permissions must be least-privilege and must
  explain any identity-token or deployment authority.
- `WORKFLOW_REUSE`: workflow and action reuse must identify their local or
  pinned boundary and preserve the caller contract.
- `WORKFLOW_CONTEXT`: event inputs, expressions, and environment values must
  be valid for the selected trigger and safe at the trust boundary.
- `COMPOSITE_INPUT_OUTPUT`: action inputs and outputs must be declared and
  forwarded through `GITHUB_OUTPUT` where needed.
- `COMPOSITE_SHELL`: shell behavior must be explicit, strict, and safe for
  untrusted values.
- `COMPOSITE_COMPATIBILITY`: action runtime and versioning choices must be
  compatible with the supported runner contract.
- `VERIFICATION_PATH`: smoke and failure-path checks must cover the linked
  workflow, composite action, and script behavior.
