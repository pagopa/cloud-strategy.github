# Terraform Skill Routing Boundaries

The repository keeps `internal-terraform` as the stable Terraform/OpenTofu
entrypoint and decision wrapper. Positive language-only HCL, `.tf`, `.tfvars`,
and `.tfvars.json` work delegates directly to `internal-tf` without loading
operational context. Native Terraform tests, state, provider operation,
plan/apply, CI, recovery, module architecture, adoption, and all other
non-language work use `/internal-terraform` to invoke the imported
`/antonbabenko-terraform-skill` core. An approved import assessment or
execution may hand off to the secondary `/internal-terraform-import` owner,
which owns the portable import runner and provider identity adapters. Mixed or
ambiguous requests keep `internal-terraform` as the single primary owner; a
separable language finding may be delegated to `internal-tf`.

This layering preserves the public entrypoint, prevents unrelated preloading,
keeps adoption and operational references conditional and bundle-relative, and
separates import execution from adoption policy. The benchmark reports a
static context proxy and does not prove runtime loading, cache behavior, or
billed token savings. The Anton bundle remains upstream-authoritative and
unchanged.
