# GCP Governance Guardrail Map

Use this reference when the user needs a clearer split between GCP governance surfaces.

## Quick split

| Need | Use first | Why |
| --- | --- | --- |
| Limit what principals may do across many folders or projects | Org Policy plus scope design | Preventive guardrail |
| Grant execution access to people, groups, or workloads | IAM binding model | Authorization and scope control |
| Remove long-lived workload credentials | workload identity federation | Identity-based runtime access |
| Constrain service account sprawl | service account boundary design | Governance and blast-radius control |
| Standardize security posture | org or folder guardrails plus exceptions | Governance consistency |

## Review questions

1. Is this question about where a control lives or what a principal may do?
2. Is the mechanism preventing action, granting action, or constraining workload identity?
3. Is the scope org, folder set, or project set?
4. What exception path is required, if any?
5. What should be validated before rollout?

## Reminder

- Structure chooses placement.
- Governance chooses permissions and guardrails.
- Operations verifies that the chosen governance behaves as intended after rollout.
