# GitHub Governance Guardrail Map

Use this reference when a governance decision needs a clearer split between
control surfaces, trust boundaries, and exception patterns.

## Control selection

| Need | Control | Why |
| --- | --- | --- |
| Enforce branch and merge standards broadly | Rulesets or branch protection | Preventive repository guardrail |
| Limit what automations may do | GitHub Apps or Actions permissions | Reviewable automation trust boundary |
| Remove long-lived cloud secrets from workflows | OIDC posture | Federated workload access |
| Separate release control from daily development | Environments plus approvals | Deployment guardrail |
| Govern AI feature use | Copilot governance | Policy, entitlement, and visibility control |

## Scope and exception questions

1. Is the mechanism preventing action, granting action, or constraining
   automation?
2. Is the scope enterprise, organization, repository set, repository, or
   environment?
3. What exception path is required, and who owns its review?
4. What evidence must exist before rollout and after the first safe unit?

## Trust-boundary examples

| Need | Primary control | Review note |
| --- | --- | --- |
| Repository automation needs repository write operations | GitHub App with narrow repository permissions | Keep installation scope and token privileges explicit. |
| Workflow needs cloud access without long-lived credentials | OIDC trust plus environment or branch guardrails | Review the GitHub trust boundary and cloud-side role scope. |
| Reusable workflow needs elevated deployment rights | Environment approval plus scoped workflow permissions | Avoid giving every workflow the same broad token surface. |

## Exception patterns and audit expectations

| Exception type | Pattern | Audit expectation |
| --- | --- | --- |
| Ruleset exception for a subset of repositories | Scoped exception with owner, reason, and review date | Record why it exists, where it applies, and when it is rechecked. |
| Temporary environment bypass or elevated automation access | Time-bounded exception with approver and rollback note | Record approval, duration, and activity. |
| Copilot governance carve-out for a pilot group | Narrow organization or repository set with policy note and review point | Record scope, entitlement reason, and follow-up decision date. |
