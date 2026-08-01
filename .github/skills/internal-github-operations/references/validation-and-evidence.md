# GitHub Operations Validation And Evidence

Use this reference for preflight, rollout, post-rollout, runner, permission,
audit, and drift evidence.

## Preflight

- confirm scope and rollout unit
- confirm rollback trigger and owner
- confirm runner, workflow, and audit signals for the affected surface
- confirm permission and environment assumptions before widening rollout
- confirm reporting or export surfaces needed for follow-up evidence

## Rollout and post-rollout

- validate the first safe unit before widening scope
- record what was actually observed versus what was only expected
- collect the audit trail for what changed
- prove intended workflows still run with expected permissions
- prove runner capacity and health match operating assumptions
- confirm audit and reporting surfaces describe the intended state

## Runner health evidence

| Surface | Signals to check | What they confirm |
| --- | --- | --- |
| Hosted or self-hosted runner rollout | Queue time, runner availability, job success, startup or registration failures | Runner capacity and health match operating assumptions |
| Environment or protected deployment path | Approval flow, environment access, deployment outcome | Release controls allow intended delivery |
| Repository or organization workflow change | Run outcome, token scope behavior, audit events | The change did not silently widen or break automation |

## Workflow-permission validation

| Need | Acceptable proof | Not enough on its own |
| --- | --- | --- |
| Workflow has intended permissions | Expected action succeeds and denied actions remain denied | One green run without token-scope checks |
| Environment controls still work | Approval, secret access, and deployment path behave as designed | Deployment success without trigger proof |
| Automation trust remains constrained | Audit records and scoped actor behavior match design | Absence of visible failures |

## Audit and drift follow-up

| Rollout stage | Evidence before widening |
| --- | --- |
| First repository or environment | Audit trail, expected permission behavior, rollback owner |
| First runner group or automation boundary | Queue health, registration health, failure handling |
| Broad organization rollout | Prior-wave observations, drift review, investigated regressions |
