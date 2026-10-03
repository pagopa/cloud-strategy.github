# Evidence

Sources, accessed 2026-09-27:

- <https://docs.github.com/en/enterprise-cloud@latest/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization>
- <https://cli.github.com/manual/gh_api>

## Contents

- [Audit log](#audit-log)
- [Rollout ladder](#rollout-ladder)
- [Drift checks](#drift-checks)
- [Permission proof](#permission-proof)

## Audit log

- The organization audit log covers the last 180 days; only owners can read
  it. The audit log API requires GitHub Enterprise Cloud and the
  `read:audit_log` scope. Git events are kept for seven days.
- Query with search qualifiers such as `action:`, `actor:`, `repo:`, and
  `created:`. Free-text search is not supported.
- `gh api` sends `POST` as soon as `-f` or `-F` fields are present. Force
  `GET` for reads:

  ```bash
  gh api --method GET /orgs/ORG/audit-log \
    -f phrase='action:repository_ruleset.update created:>=2026-09-20' \
    -f per_page=100 --paginate
  ```

- Security alert endpoints behave the same way: an implicit `POST` can return
  a misleading `404`.

## Rollout ladder

| Stage | Evidence before widening |
|---|---|
| First repository or environment | Audit trail, expected allow and deny behavior, rollback owner |
| First runner group or automation boundary | Queue and registration health, failure handling |
| Broad organization rollout | Prior-wave observations, drift review, investigated regressions |

For every stage, state the rollout unit, the rollback trigger, and who
decides. Record what was observed separately from what was expected.

## Drift checks

- Compare live settings with the declared baseline through the API, for
  example `gh api repos/ORG/REPO/rulesets` or the organization rulesets
  endpoint.
- Report each difference with the repository, the setting, the expected
  value, and the observed value.

## Permission proof

| Need | Acceptable proof | Not enough on its own |
|---|---|---|
| Workflow has intended permissions | Expected action succeeds and denied actions stay denied | One green run |
| Environment controls work | Approval, secret access, and deploy path behave as designed | A successful deploy |
| Automation trust stays constrained | Audit entries and actor behavior match the design | Absence of visible failures |
