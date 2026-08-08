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

### Routing

- Pure HCL and typed configuration: Primary = `/internal-tf` (no Anton preload).
- All other Terraform/OpenTofu work (including native tests, modules, provider
  operations, plans, and CI-integrated roots): Primary =
  `/antonbabenko-terraform-skill` via this wrapper.

### Context collection

Collect runtime/version, changed-root path, relevant files and providers,
execution path, environment criticality, and immediate risk only when they
affect the selected branch; mark missing facts explicitly.

### Test reachability

For any new or changed Terraform root, production-ready completion requires
evidence that the selected runner executes locally and is reachable from the
matching CI trigger; when that proof cannot be demonstrated, record the
reachability gap explicitly.

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
