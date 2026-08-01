# Azure Governance Guardrail Map

Use this reference for Azure control patterns, identity examples, and exception
evidence.

## Control patterns

| Scenario | Primary control | Evidence focus |
|---|---|---|
| Limit permitted locations, SKUs, or network posture | Azure Policy or initiative | Preventive or detective effect, scope, compliance, and remediation. |
| Grant people or groups access to resources | RBAC role assignments | Authorization scope, least privilege, and intended operations. |
| Limit standing privilege for sensitive operations | PIM or PAM | Approval, duration, elevation activity, and review. |
| Remove long-lived credentials from workloads | Managed identity or federation | Trust configuration, scoped RBAC, and runtime evidence. |
| Standardize metadata expectations | Naming and tagging controls | Coverage, exemptions, and revalidation. |

## Workload identity and federation examples

| Need | Pattern | Review evidence |
|---|---|---|
| Azure workload access to Azure resources | Managed identity plus scoped RBAC | Identity type, resource scope, and successful intended operation. |
| External CI deployment into Azure | Federation plus narrow RBAC scope | Token trust and resource authorization as separate controls. |
| Human production elevation | PIM-backed role path | Approval, duration, activity record, and revocation. |

## Exception evidence

| Exception type | Required record |
|---|---|
| Policy exception for subscriptions | Business reason, owner, scoped exemption, compensating controls, expiry or review date. |
| Temporary elevated operator access | Approver, duration, activity evidence, and closure confirmation. |
| Workload cannot yet use managed identity | Affected workload, owner, rotation path, fallback expiry, and migration deadline. |

## Rollout evidence

Before widening a high-blast-radius change, collect scope confirmation,
compliance or access results, intended-operation evidence, exception records, and
the rollback trigger.
