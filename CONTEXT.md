# Copilot Skill Routing Context

This context defines the canonical boundaries for Terraform-related Copilot skills in the standards repository.

## Catalog Boundaries

**Terraform language specialist**:
The repository-owned owner for Terraform/OpenTofu configuration language, HCL structure, `.tf`, `.tfvars`, and `.tfvars.json` work. It does not own native test scenarios, state operations, CI delivery, or infrastructure diagnosis.
_Avoid_: Terraform operations owner, test owner

**Terraform router**:
The stable entrypoint that classifies a Terraform/OpenTofu request and selects the narrowest specialist without preloading unrelated skills.
_Avoid_: Terraform language specialist

**Native Terraform test**:
A Terraform/OpenTofu test artifact or execution using `.tftest.hcl`, `.tftest.json`, `run`, `assert`, mock providers, or `terraform test`/`tofu test`.
_Avoid_: generic Terraform validation, infrastructure test

**Imported skill**:
A sync-managed external skill whose upstream content remains authoritative unless an explicit local override is registered.
_Avoid_: local Terraform skill, copied skill
