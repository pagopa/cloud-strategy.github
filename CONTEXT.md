# Copilot Skill Routing Context

This context defines the canonical boundaries for Terraform-related Copilot skills in the standards repository.

## Catalog Boundaries

**Terraform language specialist**:
The repository-owned language-only owner for Terraform/OpenTofu configuration language, HCL structure, `.tf`, `.tfvars`, and `.tfvars.json` work. It excludes state, provider operation, plan/apply, native test, CI, and cloud behavior.
_Avoid_: Terraform operations owner, test owner, provider or state owner

**Terraform wrapper/core**:
`internal-terraform` is the stable entrypoint and thin repository wrapper for operational, mixed, adoption, state, native test, CI, provider, recovery, and infrastructure-diagnosis work. It delegates positive language-only HCL and `.tfvars.json` work directly to `internal-tf`; mixed or ambiguous requests keep the wrapper as the single primary owner, with Anton core depth at `/antonbabenko-terraform-skill`.
_Avoid_: duplicated Anton guidance, direct IBM test routing

**Native Terraform test**:
A Terraform/OpenTofu test artifact or execution using `.tftest.hcl`, `.tftest.json`, `run`, `assert`, mock providers, or `terraform test`/`tofu test`.
It is an Anton-backed branch through `/internal-terraform`.
_Avoid_: generic Terraform validation, standalone test owner

**Imported skill**:
A sync-managed external skill whose upstream content remains authoritative unless an explicit local override is registered.
_Avoid_: local Terraform skill, copied skill
