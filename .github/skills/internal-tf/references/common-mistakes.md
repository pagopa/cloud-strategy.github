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
