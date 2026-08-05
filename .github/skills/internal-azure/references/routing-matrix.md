# Azure Routing Scenario Matrix

## Direct specialist cases

| Immediate deliverable | Specialist | Selection signal |
|---|---|---|
| Management-group, subscription, landing-zone, residency, or topology design | `/internal-azure-organization-structure` | The output places Azure resources or platform boundaries. |
| RBAC, workload identity, PIM/PAM, Policy, tagging, guardrail, or exception design | `/internal-azure-governance` | The output defines authorization or preventive control behavior. |
| Preflight, monitoring, rollout evidence, backup/restore proof, or continuity validation | `/internal-azure-operations` | The output proves that a chosen platform change works. |
| Azure DevOps pipeline YAML, environment promotion, or project automation | `/internal-azure-devops` | The output changes pipeline or project delivery behavior. |

## Strategic decision cases

| Immediate deliverable | Specialist | Selection signal |
|---|---|---|
| Choosing between landing-zone or platform-topology alternatives | `/internal-azure-strategic` | The output compares viable options before implementation. |
| Framing a cross-domain Azure decision with material tradeoffs | `/internal-azure-strategic` | The output is a recommendation, not one owned implementation artifact. |
| Narrow Azure task with a known owner | Direct specialist | Decision framing is not needed; invoke the owner directly. |

## Trigger evaluation fixtures

| Fixture | Expected selection |
|---|---|
| Management-group layout | `/internal-azure-organization-structure` |
| RBAC operating model | `/internal-azure-governance` |
| Restore exercise evidence | `/internal-azure-operations` |
| Pipeline YAML review | `/internal-azure-devops` |
| Choosing between landing-zone alternatives | `/internal-azure-strategic` |
| Concrete Terraform edit | `/internal-terraform` |
| Terraform HCL or `.tfvars` language edit | `/internal-tf` |
| Native `.tftest.hcl` or `.tftest.json` test | `/internal-terraform` → `/antonbabenko-terraform-skill` |
| Terraform module, state, or drift decision | `/internal-terraform` → `/antonbabenko-terraform-skill` |
| Concrete Azure Policy definition | `/internal-cloud-policy` |
| Current SKU price | `/awesome-copilot-azure-pricing` |
| Generic application code hosted on Azure | No forced Azure specialist; use the application's owner. |

## Adjacent-owner cases

| Request | Primary route | Adjacent owner | Ordering rule |
|---|---|---|---|
| Concrete Terraform edit for Azure resources | `/internal-terraform` | `/internal-azure-organization-structure` or `/internal-azure-governance` | The Terraform router classifies the code edit; add Azure context only when the design decision is independently requested. |
| Concrete Azure Policy definition | `/internal-cloud-policy` | `/internal-azure-governance` | Cloud policy owns the policy artifact; governance supplies the control model only when separately requested. |
| Azure role selection for a named resource or action | `/awesome-copilot-azure-role-selector` | `/internal-azure-governance` | Role selection owns the role recommendation; governance adds the authorization model when separately requested. |
| Current Azure SKU price | `/awesome-copilot-azure-pricing` | `/internal-azure-strategic` | Pricing owns current cost data; add strategic framing only when options must be compared. |
| Azure resource health diagnosis | `/awesome-copilot-azure-resource-health-diagnose` | `/internal-azure-operations` | Resource health owns incident diagnosis; operations adds rollout or recovery proof when requested. |
| Azure DevOps CLI command or execution | `/awesome-copilot-azure-devops-cli` | `/internal-azure-devops` | CLI owns the command path; pipeline design is a separate deliverable. |
| Azure pricing estimate or commitment choice | `/awesome-copilot-azure-pricing` | `/internal-azure-strategic` | Pricing owns the estimate; strategic owns the recommendation when the choice is consequential. |

## Multi-deliverable ordering

| Deliverables | Primary | Secondary |
|---|---|---|
| Subscription placement followed by Policy design | `/internal-azure-organization-structure` | `/internal-azure-governance` |
| Governance design followed by rollout proof | `/internal-azure-governance` | `/internal-azure-operations` |
| Pipeline behavior followed by permission-boundary design | `/internal-azure-devops` | `/internal-azure-governance` |

Start with the deliverable that establishes the next dependent decision and add
the secondary specialist only when its output is independently requested.
