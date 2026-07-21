# Azure Routing Scenario Matrix

## Fallback-positive cases

| Scenario | Why no primary owner |
|---|---|
| Underspecified cross-subscription control problem mixing structure, governance, and operations with no clear primary deliverable | The request names multiple Azure domains but does not identify which deliverable takes priority. |
| Azure platform question asking which lane should own the work without naming structure, governance, operations, or pipelines | The user has not selected a domain; the fallback must clarify the lane before any specialist can engage. |
| Broad Azure adoption review where the user wants a general health assessment across all domains | No single specialist owns a cross-domain health review; the fallback selects the minimum set. |

## Direct-specialist negative cases

| Scenario | Direct owner | Reason |
|---|---|---|
| Management-group or subscription layout | `internal-azure-organization-structure` | The deliverable is a structural placement decision. |
| RBAC, Policy, or PIM design | `internal-azure-governance` | The deliverable is a guardrail or identity boundary. |
| Backup/restore or DR validation | `internal-azure-operations` | The deliverable is operational evidence or continuity proof. |
| Pipeline YAML or project automation | `internal-azure-devops` | The deliverable is pipeline behavior or project flow. |

## Multi-domain primary-owner cases

| Scenario | Primary owner | Secondary | Reason |
|---|---|---|---|
| Subscription design with later Policy work | `internal-azure-organization-structure` | `internal-azure-governance` | The first deliverable is placement; Policy follows once the structure is settled. |
| Policy rollout evidence | `internal-azure-governance` | `internal-azure-operations` | The first deliverable is governance design; operations validates the rollout. |
| Pipeline permissions detail | `internal-azure-devops` or `internal-azure-governance` | depends on deliverable | Choose `internal-azure-devops` when the deliverable is pipeline behavior; choose `internal-azure-governance` when the deliverable is the permission boundary. |

## Review rule

Prefer a direct specialist whenever a reasonable reviewer can name one primary owner from the request itself. Activate the fallback only when the request does not identify a primary owner and clarification is required before a specialist can engage.
