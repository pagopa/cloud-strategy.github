# Terraform Language Mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Missing `description` on variables or outputs | Interfaces become harder to understand and review | Describe every public input and output |
| Missing an explicit variable `type` | Invalid or surprising values reach expressions | Declare the narrowest useful type |
| Using a broad `any` type without a contract | Callers cannot tell which values are accepted | Use an object, collection, or scalar type that matches the interface |
| Relying on implicit string-to-number or collection conversions | Behavior becomes version- and caller-sensitive | Make conversions explicit with the appropriate function |
| Using `default = ""` for a truly optional string | Empty string and absent value become indistinguishable | Use `null` and handle the absent case explicitly |
| Hardcoding IDs, ARNs, account values, or secrets in configuration | Configuration becomes environment-coupled or exposes credentials | Use variables, data sources, or the approved secret-management path |
| Omitting validation for a constrained input | Invalid values fail late or produce confusing provider errors | Add a variable `validation` block close to the input |
| Hiding a simple value behind an unnecessary `local` | The expression's source becomes harder to trace | Keep simple values at the point of use; reserve locals for meaningful derived values |
| Using non-`snake_case` block labels or identifiers | Names become inconsistent with the repository convention | Use descriptive singular `snake_case` names |

## Readability mistakes

These are file-level style rules from the official
[HashiCorp Terraform style guide](https://developer.hashicorp.com/terraform/language/style).
Splitting configuration across modules, workspaces, or environments is not a
language concern; route it to `/internal-terraform`.

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating a clean `terraform fmt` as a complete style check | `fmt` normalizes whitespace and alignment only, so naming, ordering, and comment problems survive it | Review naming, ordering, and comments explicitly after `fmt` passes |
| Using `//` or `/* */` comments | The canonical HCL comment idiom is `#`, so the file diverges from generated and upstream configuration | Use `#` for both single-line and multi-line comments |
| Reaching for `count` or `for_each` where separate blocks read more clearly | The meta-argument hides intent and makes plan output harder to map back to configuration | Use them when instances are genuinely repeated; otherwise write explicit blocks |
| Ordering resource arguments arbitrarily | Readers cannot locate meta-arguments or nested blocks predictably | Put `count` or `for_each` first, then non-block arguments, then nested blocks, and keep `lifecycle` and `depends_on` last |
| Ordering `variable` or `output` arguments arbitrarily | Interfaces read inconsistently across files | Order `variable` as `type`, `description`, `default`, `sensitive`, `nullable`, `validation`, and `output` as `description`, `value`, `sensitive`, `depends_on` |
| Declaring a data source far from the resources that consume it | The reader must jump around the file to reconstruct the dependency | Place the data source next to its consumers and order blocks so each one builds on the previous |
