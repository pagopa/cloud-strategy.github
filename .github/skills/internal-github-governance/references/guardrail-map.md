# GitHub Governance Guardrail Map

Use this reference when the user needs a clearer split between GitHub governance surfaces.

## Quick split

| Need | Use first | Why |
| --- | --- | --- |
| Enforce branch and merge standards broadly | rulesets or branch protection | Preventive repository guardrail |
| Limit what automations may do | GitHub Apps or Actions permissions | Automation trust boundary |
| Remove long-lived cloud secrets from workflows | OIDC posture | Federated workload access |
| Separate release control from daily development | environments plus approvals | Deployment guardrail |
| Govern AI feature use | Copilot governance | Policy, entitlement, and visibility control |

## Review questions

1. Is this question about where a control lives or what an actor may do?
2. Is the mechanism preventing action, granting action, or constraining automation?
3. Is the scope enterprise, organization, repository set, or environment?
4. What exception path is required, if any?
5. What should be validated before rollout?

## Reminder

- Strategic absorbs light enterprise, org, and repo-shape decisions.
- Governance chooses permissions and guardrails.
- Operations verifies that the chosen governance behaves as intended after rollout.
