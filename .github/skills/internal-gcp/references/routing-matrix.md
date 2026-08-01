# GCP Routing Scenario Matrix

## Direct routing scenarios

| Scenario | Invoke |
|---|---|
| Shared VPC host and service-project placement | `/internal-gcp-organization-structure` |
| Org Policy rollout with IAM exceptions | `/internal-gcp-governance` |
| Restore evidence and recovery validation | `/internal-gcp-operations` |
| Compare two GCP platform options and recommend one | `/internal-gcp-strategic` |

## Multi-domain sequencing

- Structure before governance when project or Shared VPC placement must settle before IAM or Org Policy design.
- Governance before operational proof when a control rollout must be defined before its evidence is validated.
- Structure before operational proof when a structural change must settle before continuity evidence is collected.

## Primary-deliverable rule

Route by the primary deliverable rather than domain count. Select strategic decision support only when the requested deliverable is a decision comparison or recommendation.
