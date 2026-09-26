---
name: internal-terraform
description: Use first for any Terraform/OpenTofu request unless it is clearly language-only HCL; covers operational, mixed, adoption, state, native test, CI, provider, recovery, and infrastructure-diagnosis work.
---

# Terraform/OpenTofu Wrapper

This stable wrapper routes Terraform/OpenTofu requests and collects only the
bounded context needed to select the owner. It provides routing guidance; the
selected owner and the native runtime enforce identity, ownership, mutation,
and recovery gates.

## When to use

- Operational, mixed, adoption, state, native test, CI, provider, recovery, or
  infrastructure-diagnosis requests.
- Any Terraform/OpenTofu request whose owner is not clearly language-only.
- Route positive language-only HCL or typed-configuration fixes directly to
  `/internal-tf`.

## Intent classification and routing

Classify intent before collecting general context. Syntax ownership does not
decide operational, state, or adoption semantics.

- Positive language-only signal: HCL expressions, types, variables, outputs,
  formatting, typed configuration, `.tf`, `.tfvars`, `.tfvars.json`, or
  import-block syntax and shape only, with no state, provider operation,
  plan/apply, native test, CI, or cloud behavior. Route to `/internal-tf` and
  load no wrapper reference.
- Existing-infrastructure adoption, operational import assessment, state
  reconstruction, IaC migration, native tests, module architecture, provider
  operations, plans, CI-integrated roots, drift, upgrades, recovery, and risk
  diagnosis: this wrapper stays primary and delegates Terraform depth to
  `/antonbabenko-terraform-skill`. An approved bulk or provider-specific import
  may then hand off execution to `/internal-terraform-import`.
- HCL plus an operational or adoption concern keeps this wrapper primary.
  `/internal-tf` may contribute only a separable language finding; operational
  ownership stays with the wrapper.
- Missing or conflicting identity, ownership, mutation, or recovery facts keep
  the wrapper primary. Mark the fact unknown, fail closed, and require the
  applicable safety gates. Infer neither identity nor permission.

## Context collection

For adoption, collect only facts that affect the selected route: runtime and
version, changed root or path, desired/live/state evidence, canonical identity
and ambiguity, ownership disposition, mutation authority, environment
criticality, immediate risk, evidence mode, recovery status, runner path and
capability, import mode, manifest evidence, and per-scope state boundary. Mark
unknown facts explicitly and stop on ambiguity rather than guessing.

For other non-language branches, retain only the runtime/version, changed-root
path, relevant files and providers, execution path, environment criticality,
and immediate risk needed for the selected owner.

## Conditional references

- Adoption or existing-resource reconstruction: load
  [`references/existing-infrastructure-adoption.md`](references/existing-infrastructure-adoption.md).
- Operational validation, native tests, CI reachability, provider lockfile
  evidence, state or drift, recovery, or infrastructure diagnosis: load
  [`references/operational-validation.md`](references/operational-validation.md).
- Language-only work loads no wrapper reference.

## Handoff

Before invoking the selected owner, state:

- `Primary`: the owner of the deliverable.
- `Reason`: the deliverable and the boundary that selected the owner.
- `Context`: the facts collected above, with unknown facts marked.
- `Validation`: the narrowest check expected.

For an approved import, the handoff also uses the import protocol values:
`Primary = /internal-terraform` and
`Execution owner = /internal-terraform-import`. It provides the consumer root,
mode, scopes, identity, reconciliation, ownership, runner path and verified
capability evidence, mutation, convergence, and recovery evidence. Missing or
ambiguous evidence keeps this wrapper primary and blocks live execution.

**Complete when:** exactly one primary owner is named, every handoff field is
present or marked unknown, and any live path is blocked until its evidence is
complete.

## Guardrails

- User instructions and root repository policy have higher precedence.
- Preserve `internal-terraform` as the stable entrypoint.
- `antonbabenko-terraform-skill` is authoritative and read-only for
  unoverridden Terraform depth.
- Coordinate with `/internal-azure` only for an independent Azure design or
  governance decision.
- Route non-Terraform requests to the actual artifact owner.
- Retain local guidance only when it is uniquely repository-specific.
