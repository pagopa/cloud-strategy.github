---
description: Create cloud governance policy (AWS SCP, Azure Policy, GCP Org Policy)
name: new-cloud-policy
agent: agent
---

# Cloud Governance Policy

## Context
Create a new governance policy for AWS, Azure, or GCP.

## Required Inputs
- **Cloud provider**: ${input:cloud:aws,azure,gcp}
- **Policy name**: ${input:policy_name}
- **Purpose**: ${input:purpose}
- **Effect**: ${input:effect:deny,audit,modify}

## Instructions

### AWS (SCP)
- Location: `src/scp/`
- Format: JSON policy document
- Attach to OUs via Terraform

### Azure (Policy)
- Location: `src/02_policy_*/`
- Format: `azurerm_policy_definition` resource
- Follow folder naming: `02_policy_{service}/`

### GCP (Org Policy)
- Location: `src/02_policy_custom/`
- Format: `google_org_policy_policy` resource
- Apply to folders/projects

## Template (Azure)

```hcl
resource "azurerm_policy_definition" "{policy_name}" {
  name         = "pagopa-{policy_name}"
  policy_type  = "Custom"
  mode         = "All"
  display_name = "PagoPA - {display_name}"
  description  = "{purpose}"

  metadata = jsonencode({
    category = "{category}"
    version  = "1.0.0"
  })

  policy_rule = jsonencode({
    if = {
      # conditions
    }
    then = {
      effect = "{effect}"
    }
  })
}
```

## Validation
- Validate policy syntax
- Test in non-production first
- Document in README
