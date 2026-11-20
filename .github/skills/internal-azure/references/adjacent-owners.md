# Azure Adjacent Owners

Use this reference when an Azure request produces an artifact owned by another
skill, or when several deliverables must be ordered.

## Artifact owners

| Request | Owner | Azure role |
| --- | --- | --- |
| Concrete Azure Policy definition or exemption artifact | `internal-cloud-policy` | Control model only when separately requested. |
| Terraform code for Azure resources | `internal-terraform` | Design decision only when separately requested. |
| Current SKU price, estimate, or commitment data | `awesome-copilot-azure-pricing` | Decision mode when options must be compared. |
| Role for a named resource or action | `awesome-copilot-azure-role-selector` | Authorization model when separately requested. |
| Resource health incident diagnosis | `awesome-copilot-azure-resource-health-diagnose` | Rollout or recovery proof when requested. |
| Azure DevOps pipeline YAML or project automation | `internal-azure-devops` | Service-connection RBAC design when separately requested. |
| Azure DevOps CLI command | `awesome-copilot-azure-devops-cli` | none |
| GitHub Actions workflow deploying to Azure | `internal-github-actions` | Azure-side federation and RBAC design when separately requested. |
| Application code hosted on Azure | the application owner | none |

## Dependency ordering

Start with the deliverable that settles the next dependent decision.

| Deliverables | First | Then |
| --- | --- | --- |
| Subscription placement followed by Policy design | structure | governance |
| Governance design followed by rollout proof | governance | operations |
| Pipeline behavior followed by permission design | `internal-azure-devops` | governance |
