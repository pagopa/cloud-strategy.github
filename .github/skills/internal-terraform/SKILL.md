---
name: internal-terraform
description: Use when a Terraform/OpenTofu request needs the stable wrapper for non-language work or direct language delegation.
---

# Terraform/OpenTofu Wrapper

## Referenced files

- `references/review-anti-patterns.md`: Load only when a review needs the repository's local anti-pattern vocabulary.
- `references/decision-guide.md`: Load when feature-versus-module placement is the immediate decision before routing module work.

This stable entrypoint is a thin repository wrapper. The referenced skills are
targets, not a preload bundle:

- `/internal-tf`: Terraform/OpenTofu language, HCL, `.tf`, `.tfvars`, and typed configuration.
- `/antonbabenko-terraform-skill`: The core for native tests and every non-language Terraform branch.

## When to use

Use this skill for every Terraform/OpenTofu request that is not pure language
work, or when a mixed request needs repository-local routing before work begins.

The only core bypass is a pure HCL or typed-configuration deliverable: delegate
directly to `/internal-tf` and do not preload Anton. All other branches load the
Anton core through this wrapper, including:

- Native `.tftest.hcl` or `.tftest.json`, `run`, `assert`, mock providers, and `terraform test`/`tofu test`.
- Modules, state, drift, plan/apply, provider operation, cloud topology, CI/CD, scans, security, upgrades, recovery, and operational risk.
- Mixed requests where language work is coupled to an operational, test, provider, or lifecycle decision.

## Wrapper contract

1. Keep `/internal-terraform` as the stable entrypoint.
2. Collect only bounded context needed by the selected branch: runtime and version, files and providers, execution path, environment criticality, and risk; mark missing facts explicitly.
3. Invoke `/internal-tf` directly for pure language work. Otherwise invoke `/antonbabenko-terraform-skill` as the core.
4. Load `references/review-anti-patterns.md` or `references/decision-guide.md` only when its local overlay is independently useful.
5. Coordinate an Azure owner only when an Azure design or governance decision is independently requested.

## Repository test reachability

For every new or changed Terraform root, record the Terraform/OpenTofu root
directory and version, the boundary selected by the Anton core, the local
authoritative command, and the CI discovery mechanism. Prefer automatic
changed-root discovery; use a validated repository-owned root manifest as the
fallback.

The Anton core owns test-boundary and framework selection. This wrapper only
requires proof that the selected runner executes locally and is reachable from
the matching CI trigger before production-ready completion. Otherwise record
the reachability gap explicitly; a test file's presence is not passing
evidence.

## Authority and overrides

User instructions and root repository policy remain higher precedence. Wrapper
rules may constrain the current run. Anton is authoritative for unoverridden
Terraform depth; imported core files are read-only. The wrapper must not copy
Anton response contracts, testing guidance, operational tables, or domain depth.

## Handoff protocol

Before invoking a target, state:

- `Primary`: `/internal-tf` for pure language; otherwise `/antonbabenko-terraform-skill`.
- `Secondary`: only an independently requested adjacent owner, otherwise `none`.
- `Reason`: the immediate deliverable and its boundary signal.
- `Context`: known runtime, files, providers, execution path, and risk; mark missing facts.
- `Validation`: the narrowest check expected from the selected owner.

The selected target owns the final domain response. Do not ask for state,
credentials, or cloud context for a language-only request when those details
cannot affect the answer.

## Guardrails

- Preserve `/internal-terraform` as the stable entrypoint for existing callers.
- Keep `/antonbabenko-terraform-skill` upstream-authoritative and read-only.
- Invoke only the direct language bypass or the Anton-backed branch; do not preload both.
- If no Terraform/OpenTofu context is present, route to the owner of the actual artifact instead of forcing a Terraform specialist.
- Never recommend a production apply without the reviewed plan and approval controls required by the operational specialist.
