---
name: internal-terraform
description: Use when a Terraform/OpenTofu request needs the stable wrapper for non-language work or direct language delegation.
---

# Terraform/OpenTofu Wrapper

This stable wrapper routes Terraform/OpenTofu requests and collects only the
bounded context necessary to select the appropriate owner.

## When to use

Use this wrapper for non-language or mixed Terraform/OpenTofu requests that
require repository-local routing or handoff. Delegate pure HCL or
typed-configuration fixes directly to `/internal-tf`.

## Intent classification and routing

Classify intent before collecting general context. Syntax ownership does not
decide operational adoption semantics.

- HCL expressions, types, variables, outputs, formatting, typed configuration,
  or import-block syntax and shape only, with no operational state or live
  action: `Primary = /internal-tf`; do not preload Anton or the adoption
  reference.
- Existing-infrastructure adoption, operational import, bulk import, state
  reconstruction, or IaC migration: `Primary = /antonbabenko-terraform-skill`
  through this wrapper; load
  `.github/skills/internal-terraform/references/existing-infrastructure-adoption.md`
  only for this adoption branch.
- Other non-language Terraform/OpenTofu work, including native tests, modules,
  provider operations, plans, CI-integrated roots, state, drift, upgrades,
  recovery, or risk diagnosis: `Primary = /antonbabenko-terraform-skill` via
  this wrapper; do not load the adoption reference unless the request also
  expresses adoption intent.
- HCL plus existing-infrastructure adoption: Anton remains primary through
  this wrapper, and `/internal-tf` is limited to the separable language
  portion. Do not split operational ownership away from the wrapper; load the
  adoption reference.
- Missing or conflicting identity, ownership, or mutation facts in an adoption
  request: keep Anton primary, mark the fact unknown, load the adoption
  reference, fail closed, and require its safety gates. Do not infer identity
  or permission.

### Context collection

For an adoption branch, collect only facts that affect the selected route:
runtime and version, changed root or path, desired/live/state evidence,
canonical identity and ambiguity, ownership disposition, mutation authority,
environment criticality and immediate risk, declarative or imperative evidence
mode, and recovery status. Mark unknown facts explicitly and stop on ambiguity
rather than guessing. For other branches, retain only the runtime/version,
changed-root path, relevant files and providers, execution path, environment
criticality, and immediate risk needed for the selected owner.

### Test reachability

For any new or changed Terraform root, production-ready completion requires
evidence that the selected runner executes locally and is reachable from the
matching CI trigger; when that proof cannot be demonstrated, record the
reachability gap explicitly.

Native Terraform/OpenTofu tests are authoritative for Terraform semantics when
the native runner can observe the behavior. Python must not use regex or string
matching as a substitute for native resource, module, provider, plan, or assert
checks. A repository-specific static contract is a narrow exception only when
no native equivalent exists and its cross-boundary purpose is documented.

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
