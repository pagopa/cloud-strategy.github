# Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Using `count` where `for_each` with logical keys fits | Index-based addressing causes drift when items are added/removed in the middle | Use `for_each` with a map or `toset()` of logical keys |
| Missing `description` on variables and outputs | Undocumented interfaces block collaboration and code review | Always add `description` — it costs nothing |
| Hardcoded ARNs, subscription IDs, or account IDs | Breaks portability between environments and accounts | Use variables or data sources |
| Provider version not pinned in `required_providers` | Non-deterministic plans across machines and CI | Pin with `~>` or exact version constraint |
| `ignore_changes` without documented rationale | Hides drift and confuses future maintainers | Add a comment explaining why the lifecycle rule exists |
| Creating a module for a one-off resource group | Over-engineering adds indirection without reuse benefit | Keep it inline; extract when 2+ callers emerge |
| Breaking module interface (removing/renaming variables) | Breaks all consumers silently | Deprecate old vars, add new ones, migrate consumers, then remove |
| Missing `versions.tf` in modules | No reproducibility guarantee | Always include `required_version` and `required_providers` |
| Missing `prevent_destroy` on critical production resources | Accidental deletion during `terraform apply` | Add lifecycle for databases, DNS zones, encryption keys |
| `default = ""` instead of `default = null` for optional strings | Empty string passes validation but means "no value" ambiguously | Use `null` for truly optional inputs |
