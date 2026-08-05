# Copilot Skill Routing Context

This context defines the canonical boundaries for Terraform-related Copilot skills in the standards repository.

## Catalog Boundaries

**Terraform language specialist**:
The repository-owned owner for Terraform/OpenTofu configuration language, HCL structure, `.tf`, `.tfvars`, and `.tfvars.json` work. It does not own native test scenarios, state operations, CI delivery, or infrastructure diagnosis.
_Avoid_: Terraform operations owner, test owner

**Terraform wrapper/core**:
`internal-terraform` is the stable entrypoint and thin repository wrapper. It delegates pure HCL and typed configuration directly to `internal-tf`; every native test and other non-language Terraform branch uses the Anton core at `/antonbabenko-terraform-skill`.
_Avoid_: duplicated Anton guidance, direct IBM test routing

**Native Terraform test**:
A Terraform/OpenTofu test artifact or execution using `.tftest.hcl`, `.tftest.json`, `run`, `assert`, mock providers, or `terraform test`/`tofu test`.
It is an Anton-backed branch through `/internal-terraform`.
_Avoid_: generic Terraform validation, standalone test owner

**Imported skill**:
A sync-managed external skill whose upstream content remains authoritative unless an explicit local override is registered.
_Avoid_: local Terraform skill, copied skill
