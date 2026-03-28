---
name: internal-cicd-workflow
description: Use when the user mentions CI/CD, continuous integration, deployment pipelines, GitHub Actions workflow files, automated testing workflows, or wants to add steps like linting, testing, or deploying in a .github/workflows/ YAML file.
---

# CI/CD Workflow Skill

## When to use
- Create or modify GitHub Actions workflows.
- Add CI/CD jobs (build, test, deploy, lint).
- Add cloud authentication steps for Terraform or deployment.

## Mandatory rules
- Prefer OIDC for cloud authentication (no long-lived secrets).
- Pin every action to a full-length SHA.
- Keep `permissions` least-privilege — declare only what the job actually needs.
- Keep step names and operational output in English.
- Follow `.github/instructions/internal-github-actions.instructions.md`.

## Workflow patterns

### When to use which

| Situation | Pattern |
|---|---|
| Simple job sequence (build → test → deploy) | Single workflow with dependent jobs |
| Shared steps across 3+ workflows in the same repo | Reusable workflow (`workflow_call`) |
| Shared steps across multiple repositories | Composite action (see `internal-composite-action`) |
| Conditional deployment per environment | Environment protection rules + manual approval |

## Cloud auth snippets

Load from `references/auth-snippets.md` for full examples. Quick reference:

### AWS (OIDC)
```yaml
- uses: aws-actions/configure-aws-credentials@<FULL_SHA>
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: eu-south-1
```

### Azure (OIDC)
```yaml
- uses: azure/login@<FULL_SHA>
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

### GCP (OIDC)
```yaml
- uses: google-github-actions/auth@<FULL_SHA>
  with:
    workload_identity_provider: ${{ secrets.GCP_WIF_PROVIDER }}
    service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}
```

## Minimal workflow example
```yaml
name: CI
on: [pull_request]

permissions:
  contents: read
  id-token: write

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<FULL_SHA>
      - run: terraform fmt -check -recursive
```

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Using `permissions: write-all` or omitting permissions entirely | Grants the token maximum access — any compromised step can push code, delete branches, etc. | Declare only the permissions the job needs |
| Pinning actions by tag (`@v4`) instead of SHA | Tags are mutable — a compromised upstream can inject malicious code | Pin to full-length commit SHA |
| Using `secrets.GITHUB_TOKEN` for cross-repo operations | Token is scoped to the current repo only | Use a GitHub App or PAT with minimal scope |
| Long-lived cloud credentials in secrets instead of OIDC | Static credentials can leak and never expire | Configure OIDC federation for AWS/Azure/GCP |
| Missing `environment` protection on production deploys | Anyone who can push to the branch can deploy to prod | Add environment with required reviewers |
| Running `terraform apply` without a plan artifact | Plan drift between PR approval and merge | Save plan in PR job, load in deploy job |
| Duplicating steps across workflows instead of reusable workflow or composite | Maintenance burden grows with every copy | Extract to reusable workflow (same repo) or composite action (cross-repo) |

## Cross-references
- **internal-composite-action** (`.github/skills/internal-composite-action/SKILL.md`): for reusable composite actions shared across repos.
- **internal-terraform** (`.github/skills/internal-terraform/SKILL.md`): for the Terraform resources deployed by CI/CD.

## Checklist
- [ ] OIDC configured for cloud auth.
- [ ] All actions pinned by full SHA.
- [ ] `permissions` minimized per job.
- [ ] Environment protection enabled for production.
- [ ] Validation steps included (e.g., `terraform fmt -check`).

## Validation
- `actionlint` on workflow files (if available).
- Verify no `permissions: write-all` or missing permissions block.
- Verify all `uses:` lines reference full SHA, not tags.
