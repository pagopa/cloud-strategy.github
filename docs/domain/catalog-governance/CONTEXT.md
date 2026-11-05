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
The `internal-terraform` entrypoint and its operational or mixed-work decision boundary.
_Avoid_: Standalone native-test owner or import execution owner

**Terraform import execution owner**:
The secondary `internal-terraform-import` bundle that runs an approved import
handoff and owns portable import orchestration, identity adapters, and live
safety gates.
_Avoid_: Terraform decision owner or general cloud governance owner

**Native Terraform test**:
A Terraform or OpenTofu test artifact or execution using native test syntax or commands.
_Avoid_: Generic Terraform validation

**Imported skill**:
A sync-managed external skill whose upstream content remains authoritative unless a local override is registered.
_Avoid_: Local Terraform skill, copied skill

## Knowledge vocabulary

**Area**:
A durable responsibility with a stated Purpose and an ownership boundary.
_Avoid_: Project folder, knowledge domain

**Topic**:
A boundary within an Area where language and Rules have one meaning. Its closest DDD concept is a Bounded Context, usually but not necessarily aligned with one Subdomain.
_Avoid_: Component, project area

**Operational Home**:
The declared owner location for an Area's working evidence and deliverables, separate from accepted durable knowledge.
_Avoid_: Knowledge store, documentation bucket

**Shared Terms**:
Identical meanings used across Topics. They form a Shared Kernel only when joint ownership is explicitly declared.
_Avoid_: Ambiguous terms, shared Topic
