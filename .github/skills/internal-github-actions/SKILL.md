---
name: internal-github-actions
description: Use when creating, editing, or debugging GitHub Actions workflows, reusable workflows, or composite actions under `.github/workflows/` or `.github/actions/**/action.y*ml`, including the root cause of a failed workflow run. Route diff review to /internal-review-code, failing PR-check triage to /openai-gh-fix-ci, CodeQL setup to /awesome-copilot-codeql, and runner fleets, rulesets, or org policy to /internal-github-platform.
---

# Internal GitHub Actions

Own GitHub Actions behavior under `.github/workflows/` and
`.github/actions/**/action.yml` or `action.yaml`: workflow authoring,
`workflow_call`, reuse-pattern selection, composite-action contracts, and the
root cause of a failed workflow run.

## When to use

- Create or modify standard or reusable workflows, including CI/CD jobs for
  build, test, lint, release, or deployment.
- Decide whether repeated logic stays inline, moves to a script, becomes a
  reusable workflow, or becomes a composite action.
- Create, change, document, or test a composite `action.yml`.
- Diagnose a failed run on a branch, schedule, or manual dispatch.
- Contribute GitHub Actions observations when `internal-review-code` invokes
  this skill with a contributor envelope.

## Boundaries

| Request | Owner |
|---|---|
| Technical review of a workflow diff | `/internal-review-code`; this skill only contributes the record in [review contributor](references/review-contributor.md) |
| End-to-end triage of failing checks on an open PR | `/openai-gh-fix-ci`; this skill applies when the cause is in workflow or action YAML |
| CodeQL, Dependabot, or secret-scanning configuration | the matching `/awesome-copilot-*` skill |
| Runner fleet health, rulesets, org Actions policy, GitHub-side OIDC trust design | `/internal-github-platform` |
| Cloud-side trust policy for an OIDC role | the cloud owner (`/internal-aws`, `/internal-azure`, `/internal-gcp`) |

## Workflow authoring rules

- Prefer OIDC for cloud authentication. Grant `id-token: write` only on the
  job that uses it.
- Pin every third-party action to a full 40-character SHA with an adjacent
  release comment.
- Declare explicit least-privilege `permissions` at workflow or job scope.
  Never use `write-all`.
- Validate `workflow_dispatch` and `workflow_call` inputs before shell or
  deploy steps consume them. Pass expression values through `env:` instead of
  interpolating them in `run:`.
- Keep step names and logs in English.
- Read the official workflow syntax and context-availability documentation
  when expression scope or key-specific rules affect the change.
- When an action option needs a wider `GITHUB_TOKEN` scope, grant exactly
  that scope on the job or disable the option.
- Before enabling release auto-merge, re-verify branch, author, state, and
  cross-repository conditions with GitHub API or CLI data.
- Manual `release-please` tests on non-production branches must pass
  `skip-github-release: true`.

## Composite-action authoring rules

- Validate required inputs first and fail clearly.
- Pass inputs through `env:`; never interpolate `${{ inputs.* }}` in `run:`.
- Declare `shell: bash` on every `run:` step and start each block with
  `set -euo pipefail`. `uses:` steps take no `shell:`.
- Map caller-visible values under `outputs:` from `$GITHUB_OUTPUT`; use
  `$GITHUB_ENV` only for state inside the action.
- Extract long shell logic into a repository script early.
- Preserve existing inputs and outputs, or treat a contract change as a
  versioning event.

## Reuse-pattern selection

| Situation | Pattern |
| --- | --- |
| One or two adjacent steps in one workflow | Keep inline |
| Mostly shell or language commands called the same way | Repository script |
| Repeated jobs that need their own runners, permissions, or concurrency | Reusable workflow (`workflow_call`) |
| Step logic inside one job that exposes outputs, or reuse across repositories | Composite action |

Choose by the unit of reuse: jobs go to a reusable workflow, steps go to a
composite action. Keep an abstraction local when it saves fewer than a couple
of real call sites. When the choice changes trust boundaries or secret flow,
prefer the more explicit contract. State the reason for the choice.

## Failed runs

Start from the first failed step with log evidence
(`gh run view <id> --log-failed`) before proposing a fix. A workflow fix inside
a PR does not change a `pull_request_target` run for that PR, because the run
uses the default-branch definition. Follow
[failed run debugging](references/run-debugging.md).

## Reference map

- [Workflow patterns](references/workflow-patterns.md): validated manual
  deploy, reusable workflow, matrix, scheduled job.
- [Composite action patterns](references/composite-action.md): minimal and
  multi-step `action.yml` with outputs.
- [Composite release](references/composite-release.md): smoke and failure-path
  tests, versioning, README template.
- [Failed run debugging](references/run-debugging.md): log-first procedure,
  cause table, `pull_request_target` and token-scope traps.
- [Auth snippets](references/auth-snippets.md): AWS, Azure, and GCP OIDC
  steps.
- [Caching and artifacts](references/caching-and-artifacts.md): deterministic
  cache keys and reviewed artifact transfers.
- [Script caller guidance](references/script-caller-guidance.md): calling a
  script and forwarding its output, formats, failures, or artifacts.
- [Security hardening checklist](references/security-hardening-checklist.md):
  deployment, secrets, self-hosted runners, or untrusted events.
- [Review contributor](references/review-contributor.md): the observer-only
  record returned to `internal-review-code`.

## Validation

- Run `actionlint` on changed workflow files when available, and `zizmor`
  when the repository provides it.
- Check non-global expression contexts against the context-availability table.
- Confirm no `write-all`, an explicit `permissions` block, and a full SHA on
  every third-party `uses:` line.
- Confirm composite `run:` steps use `env:` forwarding, Bash, and strict mode,
  and that outputs are mapped from `$GITHUB_OUTPUT` and documented.
- Confirm every referenced local guide resolves.

## Completion criteria

- Workflow, `workflow_call`, and `action.yml` contracts are valid.
- The reuse choice is explicit and matches the unit of reuse.
- OIDC, least privilege, full-SHA pins, input validation, and release safety
  are addressed when relevant.
- A failed-run diagnosis cites the first failed step and its log line.
- Out-of-scope requests are handed to the owner in the boundaries table.
