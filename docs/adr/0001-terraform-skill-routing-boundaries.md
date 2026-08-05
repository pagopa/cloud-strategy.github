# Terraform Skill Routing Boundaries

The repository keeps `internal-terraform` as the stable Terraform/OpenTofu entrypoint and router, while `internal-tf` owns configuration-language and HCL work. Native Terraform tests route exclusively to the sync-managed `ibm-terraform-test` skill; state, CI, security, provider, module, and operational diagnosis work routes to `antonbabenko-terraform-skill`. This preserves the public entrypoint, prevents unrelated skill preloading, and keeps the imported test skill within its actual scope.
