# AWS Control Plane Map

Use this reference when turning a strategic AWS question into the right control surface.

## Core boundary

- **Management account**: reserve for AWS Organizations control, billing and payer responsibilities, trusted access activation, and only those actions that AWS requires there.
- **Delegated administrator accounts**: prefer for day-to-day operation of integrated AWS services when supported.
- **Member accounts**: keep workload execution, service ownership, and most resource-level IAM decisions here.

## Default review checklist

1. Is this an organization guardrail or an account execution rule?
2. Must the management account perform the action, or can it be delegated?
3. Is the mechanism limiting permissions, granting permissions, or rolling out infrastructure?
4. What is the smallest safe rollout unit: one account, one OU, one region set?
5. How do we validate the effect before broad rollout?
6. What is the rollback path if access, billing, or platform automation breaks?

## Common strategic mappings

| Need | Use first | Notes |
|---|---|---|
| Restrict service or region usage across member accounts | SCP | Test outside the org root first |
| Restrict external principals from reaching supported resources | RCP | Use only where the service supports it |
| Design cross-account human and machine access | IAM roles and trust policies | Prefer federation and role assumption over long-lived users |
| Roll out guardrail infrastructure to many accounts | StackSets | Prefer service-managed permissions when Organizations integration fits |
| Operate a service centrally across the org | Trusted access plus delegated admin | Keep management-account use minimal after activation |

## Important AWS-specific reminders

- SCPs do not affect users or roles in the management account.
- Delegated administrator accounts are still member accounts, so SCPs still apply to them.
- StackSets with service-managed permissions do not deploy stacks into the management account.
- Global IAM or S3 naming collisions matter more in multi-region StackSets than they do in single-account templates.
