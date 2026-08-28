# Security Baseline for Copilot Customization

## Objective

Provide a portable baseline that teams can apply before enabling repository-wide Copilot customization.

## Minimum controls

- Pin all third-party GitHub Actions by full commit SHA.
- Keep `permissions` minimal in workflows (default to read-only unless write is required).
- Prefer OIDC short-lived credentials over long-lived static secrets.
- Require branch protection and pull request reviews for `.github/**` changes.
- Validate `.github/**` content in CI with repository-defined automation when a dedicated validator exists.
- Run `shellcheck` on Bash scripts under `.github/scripts/`.

## IAM and least privilege

- Apply least privilege across all clouds: scope roles, policies, and bindings to the narrowest effective target.
- AWS: no `"Action": "*"` or `"Resource": "*"` without documented justification. Use permission boundaries on human
  roles. Align with SCPs.
- Azure: no Owner at subscription level without justification. Scope role assignments narrowly. Prefer managed
  identities over service principal secrets.
- GCP: no primitive roles (`roles/editor`, `roles/owner`). No `allUsers`/`allAuthenticatedUsers` bindings. Prefer
  Workload Identity over SA keys.
- Flag privilege escalation chains (e.g., `iam:PassRole` + `lambda:CreateFunction` on AWS).
- Review blast radius: identify the worst-case impact if this identity is compromised.

## Supply chain and CI/CD security

- Pin every GitHub Action to a full-length commit SHA with adjacent release/tag comment.
- Pin `docker://` references by digest instead of floating tags.
- Require OIDC for cloud authentication in workflows. Do not use long-lived secrets.
- Use minimal `permissions` on every workflow and job.
- Never use `pull_request_target` with untrusted code execution.
- Protect production environments with required reviewers and deployment rules.
- Set explicit `timeout-minutes` and `concurrency` on jobs.

## Guidance and artifact safety

- Avoid guidance that requests hidden or sensitive data.
- Prohibit plaintext tokens, keys, and passwords in examples.
- Use explicit guardrails for destructive operations.
- Require deterministic, reviewable output in generated artifacts.

## Agent safety

- Prefer read-only agents for planning/review.
- Restrict write-capable agents to clearly scoped tasks.
- Require explicit references to policy files for security-sensitive changes.

## Change governance

- Document breaking changes to skills, agents, prompts, validators, or root policy in `.github/CHANGELOG.md`.
- Use a deprecation window before removing skills or agents in active use unless a documented exception applies.
- Keep a rollback path for workflow and policy changes.

## Enforcement status

| Control | Status | Tool |
| --- | --- | --- |
| Third-party action SHA pinning | Manual review | `internal-github-actions` + PR review |
| Minimal workflow permissions | Manual review | `internal-github-actions` + PR review |
| Docker image digest pinning | Manual review | `internal-docker` + PR review |
| Validate `.github/**` in CI | Automated | `.github/workflows/_github-catalog-validation.yml` |
| `shellcheck` on `.github/scripts/` | Automated | pre-commit + CI |
| Secret placeholder avoidance in examples/generated artifacts | Partial | pre-commit hooks + review |
| OIDC over long-lived secrets | Manual review | `internal-github-actions` |
| IAM least privilege (AWS/Azure/GCP) | Manual review | `internal-review-code` + `antonbabenko-terraform-skill` |
| Supply chain hardening | Manual review | `internal-github-actions` + `internal-review-code` |
| Branch protection for `.github/**` | Manual review | repository settings requiring `_github-catalog-validation` |
| Read-only reviewer agents | Manual review | agent review |
| CHANGELOG-based change governance | Manual review | PR review |

## Optional hardening

- Add CODEOWNERS coverage for `.github/**`.
- Add secret scanning and dependency update automation.
- Add repository rulesets for workflow and environment protection.
