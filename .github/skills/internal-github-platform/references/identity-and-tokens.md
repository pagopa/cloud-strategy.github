# Identity and Tokens

Sources, accessed 2026-09-27:

- <https://docs.github.com/en/actions/reference/security/oidc>
- <https://docs.github.com/en/actions/reference/security/secure-use>

## Contents

- [Token choice](#token-choice)
- [OIDC subject claims](#oidc-subject-claims)
- [Trust-boundary examples](#trust-boundary-examples)

## Token choice

| Need | Prefer | Avoid |
|---|---|---|
| Automation inside the same repository | `GITHUB_TOKEN` with job-level permissions, read-only by default | Broad default workflow permissions |
| Automation across repositories | GitHub App with narrow permissions, installed only on target repositories | Classic PAT tied to a person |
| Human-scoped scripted access | Fine-grained PAT with expiry and repository selection, approved by org policy | Classic PAT without expiry |
| Cloud access from workflows | OIDC federation | Long-lived cloud secrets |

Any user with write access can read repository secrets through a workflow.
Scope credentials to the least privilege the job needs.

## OIDC subject claims

- The job needs `id-token: write`; that permission only allows fetching the
  token.
- Default `sub` formats:
  - environment job: `repo:ORG/REPO:environment:NAME`
  - branch: `repo:ORG/REPO:ref:refs/heads/BRANCH`
  - tag: `repo:ORG/REPO:ref:refs/tags/TAG`
  - `pull_request` without environment: `repo:ORG/REPO:pull_request`
- **Immutable subject claims:** repositories created after July 15, 2026, or
  renamed or transferred after that date, or opted in, use
  `repo:OWNER@OWNER-ID/REPO@REPO-ID:...`. Match the format the repository
  actually emits. Not available on GitHub Enterprise Server.
- Customize `sub` through the OIDC customization REST API with
  `include_claim_keys` (for example `repo`, `context`, `job_workflow_ref`).
  Create the matching cloud condition first, then change the template.
  Repositories must opt in to an organization template with
  `use_default: false`.
- Always set at least one cloud-side condition so untrusted repositories
  cannot obtain tokens. Custom claims are not supported in AWS, so AWS roles
  rely on `aud` and `sub`.
- Dependabot jobs use `event_name: dynamic`; restrict `event_name` when only
  workflows should be trusted.

## Trust-boundary examples

| Need | Primary control | Review note |
| --- | --- | --- |
| Repository automation needs write operations | GitHub App with narrow repository permissions | Keep installation scope and token permissions explicit |
| Workflow needs cloud access without secrets | OIDC with `sub` bound to repository and environment | The cloud owner writes the role policy |
| Reusable workflow needs elevated deployment rights | Environment approval plus job-scoped permissions | Consider `job_workflow_ref` in `sub` to require the approved workflow |
