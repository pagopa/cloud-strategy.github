# Terraform Skill Routing Boundaries

The repository keeps `internal-terraform` as the stable Terraform/OpenTofu
entrypoint and thin wrapper. Pure HCL and typed-configuration work delegates
directly to `internal-tf` without loading the core. Native Terraform tests and
all other non-language work use `/internal-terraform` to invoke the imported
`/antonbabenko-terraform-skill` core.

This layering preserves the public entrypoint, prevents unrelated preloading,
keeps the local wrapper limited to routing and bounded context, and removes the
standalone native-test owner. The Anton bundle remains upstream-authoritative
and unchanged.
