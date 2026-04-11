# Azure Governance Guardrail Map

Use this reference when the user needs a clearer split between Azure governance surfaces.

## Quick split

| Need | Use first | Why |
| --- | --- | --- |
| Limit what principals may do across many subscriptions | Azure Policy plus scope design | Preventive or detective guardrail |
| Grant execution access to people or groups | RBAC role assignment model | Authorization and scope control |
| Constrain privileged access | PIM or PAM posture | Time-bound elevation and review |
| Remove long-lived credentials from workloads | managed identity or federation pattern | Identity-based runtime access |
| Standardize metadata expectations | naming and tagging guardrails | Governance consistency |

## Review questions

1. Is this question about where a control lives or what a principal may do?
2. Is the mechanism preventing action, granting action, or constraining privileged access?
3. Is the scope management group, subscription set, or single subscription?
4. What exception path is required, if any?
5. What should be validated before rollout?

## Reminder

- Structure chooses placement.
- Governance chooses permissions and guardrails.
- Operations verifies that the chosen governance behaves as intended after rollout.
