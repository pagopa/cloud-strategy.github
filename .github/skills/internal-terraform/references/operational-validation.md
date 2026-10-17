# Operational Validation Overlay

Use this reference only when `/internal-terraform` selects an operational,
mixed, testing, CI, provider, state, recovery, or infrastructure-diagnosis
branch. It supplies gates and corrections that `antonbabenko-terraform-skill`
lacks; that skill remains authoritative for unoverridden Terraform/OpenTofu
operational depth.

## Root Runner and CI Reachability

For every new or changed Terraform/OpenTofu root, record evidence that the
selected local runner executes the root and that the matching CI trigger can
reach the same runner. When either proof is unavailable, record the reachability
gap and do not treat production-ready completion as demonstrated.

## Native Test Authority

Native `.tftest.hcl`, `.tftest.json`, `terraform test`, or `tofu test` behavior is
authoritative for Terraform/OpenTofu semantics when the native runner can
observe it. Python or another external-language check must not replace native
resource, module, provider, plan, or assertion checks. A repository-specific
static contract is allowed only when no native equivalent exists and its
cross-boundary purpose is recorded.

Mock and override values accept partial objects; the runner fills omitted
attributes with random values. Set every attribute the configuration parses,
such as resource IDs, and omit the rest. An `override_data` whose target
instance is outside the run's scope is a silent no-op.

A negative run passes when any check on its `expect_failures` target fails.
Prove that each negative run trips its intended check: disable the other
checks on the same target once, or give each check its own checkable object.

## Provider and Import Guard Gates

Provider lockfile evidence and live adoption or apply guards are operational
concerns. Keep them in this conditional branch and do not preload them for a
language-only request. Do not infer provider or cloud behavior from HCL shape.

When Terraform provider hooks are consumed across platforms, re-lock every
platform used by the local runner and CI. A lockfile generated on only one
platform is not sufficient evidence for a cross-platform hook.

Before a live GitHub or Terraform adoption or apply, require executable,
fail-closed guards that keep live management disabled by default, reject
`apply` without an explicit live flag, and block plans that would create an
existing `github_repository` before import. The guard must also fail closed
when identity, ownership, authority, or recovery facts are missing or
ambiguous. Stop rather than guessing or silently mutating live resources.

## Plan Delta Interpretation

A non-empty plan is not evidence of a defect in the repository. The default
reading, that the configuration is wrong, is the one worth distrusting, because
the other case is common: the configuration is right and the live objects have
diverged from it. Only the first case is closed by a repository change. An
allowlist, plan checker, or migration script that already tolerates the
difference is a prior judgment that the divergence was expected, and a field
recording provenance, a timestamp, or a generated label tends to differ across
every managed object at once.

Editing correct configuration until the delta disappears converts an expected
divergence into a real defect. Where neither reading is supported, report the
delta as undecided rather than choosing the cheaper one. Route the
reconciliation mechanics to `/antonbabenko-terraform-skill` once the delta is
classified.

## Handoff

State the selected primary owner, the overlay gate being applied,
the evidence context, and the narrowest validation.
`antonbabenko-terraform-skill` remains the owner of general Terraform/OpenTofu
provider procedures and operational depth.
