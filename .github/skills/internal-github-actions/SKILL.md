---
name: internal-github-actions
description: Use when authoring or revising GitHub Actions workflows, reusable workflows, or deciding when shared step logic should move into a composite action.
---

# GitHub Actions Skill

## When to use
- Create or modify GitHub Actions workflows under `.github/workflows/`.
- Create or modify reusable workflows exposed through `workflow_call`.
- Decide whether repeated step logic should stay inline, move to a reusable workflow, or move to a composite action.
- Add CI/CD jobs such as build, test, lint, release, or deployment.

Use `internal-devops-core-principles` when the question is delivery strategy, release model, or operating-model health rather than workflow authoring.

## Mandatory rules
- Follow `.github/instructions/internal-github-actions.instructions.md`.
- Prefer OIDC for cloud authentication.
- Pin every third-party action to a full-length SHA with adjacent release comment.
- Keep `permissions` least-privilege.
- Keep step names and logs in English.

## Choose the right reuse pattern

| Situation | Pattern |
|---|---|
| Simple pipeline in one repository | Standard workflow |
| Repeated job orchestration inside one repository | Reusable workflow (`workflow_call`) |
| Shared step logic across repositories or many workflows | Composite action |
| Composite action authoring or contract changes | Load `internal-github-action-composite` |

## Auth and workflow examples

- Load `references/auth-snippets.md` for AWS, Azure, and GCP OIDC snippets.
- Load `references/workflow-example.md` for the minimal workflow skeleton.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Using `permissions: write-all` or omitting permissions entirely | Grants the token maximum access and widens the blast radius of a compromised step | Declare only the permissions the job needs |
| Pinning actions by tag (`@v4`) instead of SHA | Tags are mutable and can be retargeted upstream | Pin to a full-length commit SHA with a release comment |
| Using `secrets.GITHUB_TOKEN` for cross-repo operations | The token is scoped to the current repository only | Use a GitHub App or PAT with minimal scope |
| Long-lived cloud credentials in secrets instead of OIDC | Static credentials can leak and do not expire automatically | Configure OIDC federation for AWS, Azure, or GCP |
| Missing `environment` protection on production deploys | Anyone who can push to the branch can deploy to production | Add an environment with required reviewers |
| Running `terraform apply` without a plan artifact | Plan drift can occur between review and deployment | Save the plan in the PR job and load it in the deploy job |
| Duplicating steps across workflows instead of reusable workflow or composite action | Maintenance burden grows with every copy | Extract to a reusable workflow in one repo or a composite action across repos |

## Cross-references

- **internal-github-action-composite** (`.github/skills/internal-github-action-composite/SKILL.md`): for composite-action authoring and compatibility-sensitive contract changes.
- **internal-terraform** (`.github/skills/internal-terraform/SKILL.md`): for the Terraform resources deployed by CI/CD.

## Checklist

- [ ] OIDC configured for cloud auth.
- [ ] All third-party actions pinned by full SHA with release comments.
- [ ] `permissions` minimized per job.
- [ ] Environment protection enabled for production.
- [ ] Validation steps included where the workflow changes infrastructure or releases.

## Validation

- `actionlint` on workflow files, if available.
- Verify there is no `permissions: write-all` and no missing permissions block where least privilege matters.
- Verify all `uses:` lines reference full SHAs instead of tags.
