---
name: internal-github-actions
description: Use when /internal-github routes GitHub Actions workflow authoring or debugging under `.github/workflows/`, including `workflow_call` and reuse-pattern selection.
user-invocable: false
---

# GitHub Actions Skill

Own GitHub Actions workflow behavior under `.github/workflows/`, including
workflow authoring, debugging, `workflow_call`, and reuse-pattern selection.

## When to use

- Create or modify standard or reusable workflows.
- Add CI/CD jobs for build, test, lint, release, or deployment.
- Decide whether repeated logic stays inline, moves to a script, becomes a
  reusable workflow, or becomes a composite action.

## Workflow authoring rules

- Prefer OIDC for cloud authentication.
- Pin every third-party action to a full-length SHA with an adjacent release
  comment.
- Keep `permissions` least-privilege and declare them where they matter.
- Keep step names and logs in English.
- Read official workflow syntax and context-availability documentation when
  expression scope or key-specific rules affect the change.
- Validate `workflow_dispatch` inputs before shell or deploy steps consume
  them.
- Before enabling release auto-merge, re-verify branch, author, state, and
  cross-repository conditions using GitHub API or CLI data.
- Manual `release-please` tests on non-production branches must pass
  `skip-github-release: true`.

## Reuse-pattern selection

| Situation | Pattern |
| --- | --- |
| Simple pipeline in one repository | Standard workflow |
| Repeated job orchestration inside one repository | Reusable workflow (`workflow_call`) |
| Shared step logic across repositories or many workflows | Composite action |
| Mostly shell or language-specific commands | Repository script called from the workflow |

Choose by the unit of reuse: jobs and their runners, permissions, or
concurrency belong in a reusable workflow; steps and caller-visible outputs
belong in a composite action; thin orchestration around language-specific
commands belongs in a script.

## Conditional review contributor

When this skill is conditionally loaded by `/internal-review-code`, contribute
observations only for workflow surfaces. Inspect the static chain from the
event through workflow or `workflow_call`, job permissions and environments,
composite actions, repository scripts, artifacts or caches, and external
system boundaries when the target links them.

Return only the wrapper protocol fields: `domain`,
`changed_contract_surfaces`, `observations`, `probes`,
`applicable_validations`, `compatibility_risks`, and `evidence_gaps`. Focus
observations and probes on OIDC and least privilege, full-SHA action pins,
input and context validity, reuse contracts, permissions and environment
boundaries, artifact and cache transfers, and the relevant chain links.

This contributor does not issue a verdict, severity, approval, merge decision,
remediation plan, or operations conclusion. Addy remains the sole substantive
review engine and `internal-review-code` remains the single public-verdict
owner. Static evidence cannot prove runner health or successful runtime
loading; record that limitation and route live evidence to Operations.

## Reference map

- Load [auth snippets](references/auth-snippets.md) for AWS, Azure, and GCP
  OIDC examples.
- Load [workflow example](references/workflow-example.md) for a compact manual
  deploy archetype.
- Load [reusable workflow template](references/reusable-workflow-template.md)
  for typed inputs and job-level reuse.
- Load [workflow patterns catalog](references/workflow-patterns-catalog.md)
  for matrix, scheduled, environment-gated, and reusable shapes.
- Load [caching and artifacts](references/caching-and-artifacts.md) for
  deterministic cache keys and reviewed artifact transfers.
- Load [reuse decision tree](references/reuse-decision-tree.md) when multiple
  reuse patterns remain plausible.
- Load [security hardening checklist](references/security-hardening-checklist.md)
  for deployment, secrets, self-hosted runners, or untrusted events.

## Completion criteria

- Workflow behavior and `workflow_call` contracts are valid.
- The reuse-pattern selection is explicit and matches the unit of reuse.
- OIDC, least privilege, full-SHA pins, input validation, and release safety
  are addressed when relevant.
- Context availability and focused validation are checked.

## Validation

- Run `actionlint` on changed workflow files when available.
- Compare non-global expression contexts with the official context-availability
  table.
- Verify the first failed step in CI-log debugging.
- Verify no `permissions: write-all` and no missing permissions block where
  least privilege matters.
- Verify every third-party `uses:` line references a full SHA.
- Verify every referenced local guide resolves before completion.
