---
description: Create a cloud governance policy (AWS SCP, Azure Policy, GCP Org Policy)
name: new-cloud-policy
agent: agent
argument-hint: cloud=<aws|azure|gcp> policy_name=<name> purpose=<purpose>
---

# Create Cloud Governance Policy

## Context
Create a new governance policy for AWS, Azure, or GCP while following repository naming and structure patterns.

## Required inputs
- **Cloud provider**: ${input:cloud:aws,azure,gcp}
- **Policy name**: ${input:policy_name}
- **Purpose**: ${input:purpose}
- **Effect**: ${input:effect}

## Instructions

### AWS (SCP)
- Recommended path: `src/scp/`.
- Format: JSON SCP document.
- Model `Action`/`NotAction`, `Resource`, and `Condition` explicitly.
- Keep technical text and descriptions in English.

### Azure (Policy)
- Recommended path: `src/02_policy_*/`.
- Format: `azurerm_policy_definition` resource.
- Common effects: `deny`, `audit`, `modify`, `append`, `disabled`.

### GCP (Org Policy)
- Recommended path: `src/02_policy_custom/`.
- Format: `google_org_policy_policy` resource.
- Define target scope clearly (organization/folder/project).

## Base template (Azure)

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
- Validate policy syntax before commit.
- Test in a non-production environment.
- Update technical documentation in English.
