# GCP Routing Scenario Matrix

## Fallback-positive cases

| Scenario | Why no primary owner |
|---|---|
| Underspecified cross-org control problem mixing structure, governance, and operations with no clear primary deliverable | The request names multiple GCP domains but does not identify which deliverable takes priority. |
| GCP platform question asking which lane should own the work without naming structure, governance, or operations | The user has not selected a domain; the fallback must clarify the lane before any specialist can engage. |
| Broad Google Cloud adoption review where the user wants a general health assessment across all domains | No single specialist owns a cross-domain health review; the fallback selects the minimum set. |

## Direct-specialist negative cases

| Scenario | Direct owner | Reason |
|---|---|---|
| Org, folder, project, or Shared VPC layout | `internal-gcp-organization-structure` | The deliverable is a structural placement decision. |
| IAM, workload identity, service account, or Org Policy design | `internal-gcp-governance` | The deliverable is a guardrail or identity boundary. |
| Monitoring, backup, DR validation, inventory, or reporting | `internal-gcp-operations` | The deliverable is operational evidence or continuity proof. |

## Multi-domain primary-owner cases

| Scenario | Primary owner | Secondary | Reason |
|---|---|---|---|
| Project or Shared VPC design with later IAM work | `internal-gcp-organization-structure` | `internal-gcp-governance` | The first deliverable is placement; IAM and Org Policy follow once the structure is settled. |
| Org Policy or IAM rollout evidence | `internal-gcp-governance` | `internal-gcp-operations` | The first deliverable is governance design; operations validates the rollout. |
| Structural change needing continuity proof | `internal-gcp-organization-structure` | `internal-gcp-operations` | The first deliverable is layout; operations confirms the recovery posture after placement. |

## Review rule

Prefer a direct specialist whenever a reasonable reviewer can name one primary owner from the request itself. Activate the fallback only when the request does not identify a primary owner and clarification is required before a specialist can engage. The fallback is not a prerequisite for ordinary GCP work and must never activate all GCP skills by default.
