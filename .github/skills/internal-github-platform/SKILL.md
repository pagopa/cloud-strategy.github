---
name: internal-github-platform
description: Use when designing, deciding, or proving GitHub repository or organization controls and operating models, including repository model, rulesets, branch protection, CODEOWNERS, environments, Apps and tokens, GitHub-side OIDC trust, runners, audit log, security-feature rollout, or Copilot policy. Route workflow YAML to /internal-github-actions, cloud-side trust policies to the cloud owner, and current Copilot feature facts to /internal-copilot-docs-research.
---

# Internal GitHub Platform

Own GitHub platform controls and operating-model decisions: what is enforced,
who or what gets access, which runners execute work, and how a rollout is
proven.

## When to use

- Choose between platform options: repository model, rulesets or branch
  protection, runner platform, token type, rollout shape.
- Design a control: ruleset, CODEOWNERS, environment protection, GitHub App
  or token scope, GitHub-side OIDC trust, runner group, Copilot policy.
- Prove a rollout or drift state with audit-log, API, or runner evidence.

## Boundaries

| Request | Owner |
|---|---|
| Workflow or `action.yml` authoring, failed-run diagnosis | `/internal-github-actions` |
| PR readiness, merge, or terminal state | `/internal-github-pr` |
| CodeQL, Dependabot, or secret-scanning configuration | the matching `/awesome-copilot-*` skill; this skill keeps only the rollout plan |
| Cloud-side trust policy for an OIDC role | the cloud owner (`/internal-aws`, `/internal-azure`, `/internal-gcp`); this skill states the required claim conditions |
| Terraform for GitHub provider resources | `/internal-terraform` |
| Current Copilot feature behavior | `/internal-copilot-docs-research` |

## Modes

Pick one mode per deliverable and produce its shape.

| Mode | Use for | Output shape |
|---|---|---|
| **decide** | A choice with more than one viable option | Decision, scope, assumptions, two or three realistic options, criteria, one recommendation, tradeoffs, reversibility, facts to verify |
| **control** | Designing or changing a guardrail or grant | Scope, mechanism, preventive effect, trust boundary and actor permissions, exception path, rollout validation |
| **prove** | Showing a change is safe to widen or still in place | Rollout unit, preflight, rollback trigger and owner, evidence marked confirmed or inferred, drift follow-up |

## Rules

- State the scope: enterprise, organization, repository set, repository, or
  environment.
- Prefer `GITHUB_TOKEN` or a GitHub App over a personal access token. Name
  the installation scope and each permission.
- Bind OIDC trust to the `sub` claim with the repository and an environment
  or ref, and match it with a cloud-side condition. Never trust a whole
  owner with a wildcard repository.
- Protect production deployment secrets with an environment that has required
  reviewers and a branch or tag policy. A wait timer never replaces reviewers.
- Do not attach persistent self-hosted runners to public repositories or to
  repositories that run fork PRs. Prefer hosted or ephemeral runners in a
  restricted runner group.
- In CODEOWNERS the last matching pattern wins: put broad patterns first and
  specific paths after them, and give `.github/` an explicit owner.
- Use only owner handles the user supplied or the repository already uses.
  Flag unresolved placeholders instead of emitting them.
- Give every non-universal control an exception path: owner, reason,
  duration, review date, and rollback.
- For `gh api` reads with `-f` or `-F` fields, pass `--method GET`; fields
  otherwise switch the request to `POST`.
- Verify plan-dependent or recently changed platform facts against current
  GitHub documentation and cite the URL with an access date.

## Reference map

- [Controls](references/controls.md): rulesets and branch protection,
  push rulesets, CODEOWNERS, environments.
- [Identity and tokens](references/identity-and-tokens.md): `GITHUB_TOKEN`,
  GitHub Apps, fine-grained PATs, OIDC `sub` claims.
- [Runners](references/runners.md): hosted, larger, self-hosted, ARC, runner
  groups, fork risk.
- [Evidence](references/evidence.md): audit log queries, rollout ladder,
  drift checks.
- [Security features](references/security-features.md): GHAS rollout and
  routing to feature skills.
- [Decision lenses](references/decision-lenses.md): lens combinations for
  decide mode.

## Completion criteria

- The mode is explicit and the output has that mode's shape.
- Scope, mechanism, trust boundary, and actor permissions are named.
- Exceptions have an owner, duration, and review date.
- Evidence separates confirmed from inferred signals.
- Freshness-sensitive facts carry a source and access date.
- Out-of-scope requests are handed to the owner in the boundaries table.
