---
description: Azure-specific Terraform standards for RBAC, Management Groups, Policy, and resource conventions.
applyTo: "**/eng-azure-*/**/*.tf,**/*azure*.tf,**/*azurerm*.tf"
---

# Terraform Azure Instructions

## Provider conventions
- Pin `azurerm` provider version in `required_providers`.
- Configure the `features {}` block explicitly — do not leave it empty without intent.
- Use `subscription_id` from variables or data sources, never hardcoded.
- Set `skip_provider_registration = true` only when Registration is managed externally.

## RBAC patterns
- Prefer built-in roles over custom roles whenever possible.
- Scope role assignments to the narrowest scope needed (resource > resource group > subscription > management group).
- Never assign `Owner` at subscription or management group level without documented justification.
- Use conditions (ABAC) on role assignments for fine-grained access control when supported.
- Use `azurerm_role_definition` with explicit `permissions` block for custom roles — keep `actions` and `not_actions` explicit.
- Prefer managed identities over service principals with secrets.
- For service principals, keep application permissions minimal and avoid `Directory.ReadWrite.All`.

## Management Groups and Policy
- Keep Management Group hierarchy explicit in Terraform — do not assume inherited state.
- Assign Azure Policy at the narrowest effective scope.
- Use `azurerm_management_group_policy_assignment` with explicit `parameters` and `non_compliance_message`.
- Document policy effects (`Deny`, `Audit`, `DeployIfNotExists`) and their operational impact.
- Keep policy rule JSON in separate files for readability and review.

## Anti-patterns (Azure-specific)

### Critical
- Hardcoded subscription IDs, tenant IDs, or client secrets.
- `Owner` role at subscription level without justification.
- Custom role with `*` actions.

### Major
- `Contributor` at subscription level when narrower scope suffices.
- Role assignment without scope restriction (defaults to subscription).
- Missing `condition` on sensitive role assignments where ABAC is available.
- Missing `azurerm_management_lock` on production data resources.
- Public IP without Network Security Group association.
- Storage account with `allow_blob_public_access = true` without justification.
- Missing diagnostic settings on production resources.

### Minor
- Missing `ManagedBy = "terraform"` tag.
- Resource group naming not following convention (e.g., `rg-<project>-<env>-<region>`).
- Redundant role assignments that could be consolidated.

## Naming conventions
- Follow Azure naming conventions: `rg-`, `st`, `kv-`, `pip-`, etc.
- Resource names: `snake_case` in Terraform, cloud naming convention in Azure resource names.
- Required tags: `Project`, `Environment`, `ManagedBy` (at minimum).

## Validation
- `terraform fmt -recursive`
- `terraform validate`
- Review `terraform plan` for unintended RBAC or Policy changes.
- Check that no Management Group Policy would block the planned changes.
