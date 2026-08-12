---
name: internal-terraform
description: Use when Terraform/OpenTofu work is operational, mixed, adoption, state, testing, CI, provider, recovery, or infrastructure diagnosis.
---

# Terraform/OpenTofu Wrapper

This stable wrapper routes Terraform/OpenTofu requests and collects only the
bounded context needed to select the appropriate owner.

## When to use

Use this wrapper for operational or mixed Terraform/OpenTofu requests that
require repository-local routing or handoff. Delegate positive language-only
HCL or typed-configuration fixes directly to `/internal-tf`.

## Intent classification and routing

Classify intent before collecting general context. Syntax ownership does not
decide operational, state, or adoption semantics.

- Positive language-only signal: HCL expressions, types, variables, outputs,
  formatting, typed configuration, `.tf`, `.tfvars`, `.tfvars.json`, or
  import-block syntax and shape only, with no state, provider operation,
  plan/apply, native test, CI, or cloud behavior. Set `Primary = /internal-tf`
  and do not preload this wrapper's operational references.
- Existing-infrastructure adoption, operational import, bulk import, state
  reconstruction, IaC migration, native tests, module architecture, provider
  operations, plans, CI-integrated roots, drift, upgrades, recovery, and risk
  diagnosis remain `Primary = /antonbabenko-terraform-skill` through this
  wrapper.
- HCL plus an operational or adoption concern keeps Anton primary through this
  wrapper. `/internal-tf` may contribute only a separable language finding;
  operational ownership is not split away from the wrapper.
- Missing or conflicting identity, ownership, mutation, or recovery facts keep
  the wrapper primary. Mark the fact unknown, fail closed, and require the
  applicable safety gates. Do not infer identity or permission.

### Context collection

For adoption, collect only facts that affect the selected route: runtime and
version, changed root or path, desired/live/state evidence, canonical identity
and ambiguity, ownership disposition, mutation authority, environment
criticality, immediate risk, evidence mode, and recovery status. Mark unknown
facts explicitly and stop on ambiguity rather than guessing.

For other non-language branches, retain only the runtime/version, changed-root
path, relevant files and providers, execution path, environment criticality,
and immediate risk needed for the selected owner.

## Conditional local references

- Adoption or existing-resource reconstruction: load
  `references/existing-infrastructure-adoption.md`.
- Operational validation, native tests, CI reachability, provider lockfile
  evidence, state or drift, recovery, or infrastructure diagnosis: load
  `references/operational-validation.md`.
- Language-only work loads no wrapper-owned operational reference. Both local
  references are resolved relative to this skill bundle.

This skill provides guidance and routing instructions only. It cannot enforce
runtime identity, ownership, mutation, or recovery gates; the selected owner
and native runtime remain authoritative for those behaviors.

### Handoff

Before invoking the selected target, state Primary, Reason (deliverable and
boundary), Context, and Validation (the narrowest check expected).

### Guardrails

- User instructions and root repository policy have higher precedence.
- Preserve `internal-terraform` as the stable entrypoint.
- Anton is authoritative and read-only for unoverridden Terraform depth.
- Coordinate an Azure owner only for an independent Azure design or governance decision.
- Route non-Terraform requests to the actual artifact owner.
- Retain local guidance only when uniquely repository-specific.

This wrapper is a routing surface. `/internal-tf` owns language and HCL; Anton
owns Terraform domain depth unless a repository-specific rule is uniquely
justified.
