# Controls

Sources, accessed 2026-09-27:

- <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets>
- <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners>
- <https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments>

Re-verify plan availability before recommending a control.

## Contents

- [Rulesets and branch protection](#rulesets-and-branch-protection)
- [Push rulesets](#push-rulesets)
- [CODEOWNERS](#codeowners)
- [Environments](#environments)
- [Control selection](#control-selection)

## Rulesets and branch protection

- Rulesets and branch protection rules both apply to a branch. All applicable
  rules are aggregated and the most restrictive version wins; a ruleset has
  no priority.
- Rulesets add: several rulesets on one branch, an enforcement status you can
  change without deleting the ruleset, visibility to anyone with read access,
  and bypass lists for roles, teams, or GitHub Apps.
- Organization rulesets that target many repositories are an Enterprise-plan
  feature. Limits: 75 rulesets per repository and 75 organization-wide.
- Prefer rulesets for new controls and for org-wide targeting. Convert
  existing branch protection with GitHub's conversion flow and roll out in
  waves.

## Push rulesets

- Push rulesets block pushes to a private or internal repository and its
  whole fork network by file path, path length, extension, or file size.
- Only people with bypass in the root repository can bypass a push rule in a
  fork.

## CODEOWNERS

- GitHub looks for `CODEOWNERS` in `.github/`, the root, then `docs/`, and
  uses the first one found. The file on the PR's base branch is used.
- **The last matching pattern takes precedence.** Put `*` and broad patterns
  first and specific paths after them. A trailing catch-all shadows every
  rule above it.
- Owners must have explicit write access; a team must be visible. An unknown
  or under-privileged owner is silently not assigned, and invalid lines are
  skipped.
- Give the CODEOWNERS file itself an owner, for example
  `/.github/ @org/platform`, and enable "Require review from Code Owners" in a
  ruleset or branch protection. One owner's approval satisfies the rule.

## Environments

- Required reviewers: up to six users or teams, one approval is enough, and
  "prevent self-review" stops the deployer from approving. Environment
  secrets are released only after approval.
- Deployment branches and tags restrict which refs can deploy.
- A wait timer only delays; it never replaces reviewers.
- On Free, Pro, and Team plans, required reviewers, wait timers, and
  admin-bypass settings for private repositories are not available; they work
  only on public repositories. Check the plan before relying on them.
- On self-hosted runners, environment jobs are not isolated; treat
  environment secrets like repository secrets there.

## Control selection

| Need | Control | Why |
| --- | --- | --- |
| Enforce branch and merge standards broadly | Org or repository ruleset | Preventive and visible; supports bypass lists |
| Stop risky file types or sizes | Push ruleset | Blocks at push time across the fork network |
| Route review to owners | CODEOWNERS plus code-owner review rule | Ownership becomes enforceable |
| Separate release control from daily work | Environment with reviewers and branch policy | Secrets released only after approval |
| Limit what automation can do | GitHub App or scoped `GITHUB_TOKEN` | Reviewable trust boundary |
