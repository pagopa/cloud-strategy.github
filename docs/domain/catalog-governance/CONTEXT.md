# Catalog Governance

This context defines the repository's terms for governing reusable Copilot assets and the contracts that keep their source catalog coherent.

## Asset vocabulary

**Catalog asset**:
A reusable instruction, skill, agent, prompt, script, or template managed by this repository.
_Avoid_: Runtime copy, consumer asset

**Source-managed**:
An asset whose canonical content and ownership remain in this repository.
_Avoid_: Synchronized copy

**Consumer-local**:
An asset owned by a target repository and preserved when source-managed content is synchronized.
_Avoid_: Local source

**Bridge**:
A compact entrypoint that identifies the scope and routing boundary of a Copilot surface.
_Avoid_: General policy dump

**Inventory**:
The generated exact path list for the live GitHub Copilot catalog.
_Avoid_: Policy file, catalog intention

## Routing vocabulary

**Terraform language specialist**:
The repository-owned owner for Terraform and OpenTofu language-only HCL work.
_Avoid_: Terraform operations owner

**Terraform wrapper/core**:
The `internal-terraform` entrypoint and its operational or mixed-work routing boundary.
_Avoid_: Standalone native-test owner

**Native Terraform test**:
A Terraform or OpenTofu test artifact or execution using native test syntax or commands.
_Avoid_: Generic Terraform validation

**Imported skill**:
A sync-managed external skill whose upstream content remains authoritative unless a local override is registered.
_Avoid_: Local Terraform skill, copied skill
