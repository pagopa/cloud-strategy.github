# AWS Organization Structure Control Surface Map

Use this reference when turning a structural AWS question into the right control surface.

## Core boundary

- **Management account**: reserve for AWS Organizations control, billing and payer responsibilities, trusted access activation, and only those actions that AWS requires there.
- **Delegated administrator accounts**: prefer for day-to-day operation of integrated AWS services when supported.
- **Member accounts**: keep workload execution, service ownership, and most resource-level IAM decisions here.

## Default review checklist

1. Is this a structure choice, a governance control, or an operations concern?
2. Must the management account perform the action, or can it be delegated?
3. Is the change shaping layout, shaping permissions, or rolling out infrastructure?
4. What is the smallest safe rollout unit: one account, one OU, or one region set?
5. What must be validated before broad rollout?
6. What is the rollback path if access, billing, or platform automation breaks?

## Common structural mappings

| Need | Use first | Notes |
| --- | --- | --- |
| Shape preventive boundaries across many accounts | OU design plus `internal-aws-governance` | Keep the structure and the guardrail choice separate |
| Design a central operating account for an AWS service | Delegated admin placement | Use management account only when AWS requires it |
| Roll out a baseline stack across many accounts | StackSets topology | Keep global-resource blast radius explicit |
| Separate finance oversight from platform execution | payer and management responsibility split | Make the ownership model explicit |
| Place shared services or log collection | account-purpose model | Keep workload accounts separate from platform accounts |

## Important AWS-specific reminders

- SCPs do not affect users or roles in the management account.
- Delegated administrator accounts are still member accounts, so SCPs still apply to them.
- StackSets with service-managed permissions do not deploy stacks into the management account.
- Global IAM or S3 naming collisions matter more in multi-region StackSets than they do in single-account templates.
