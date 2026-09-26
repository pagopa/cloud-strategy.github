---
name: internal-tf
description: Use when Terraform/OpenTofu language-only HCL is the immediate concern. Route module architecture, state, plan or apply, provider operation, native `.tftest.hcl` tests, CI, scans, upgrades, and risk diagnosis to /internal-terraform.
---

# Terraform/OpenTofu Language

## When to use

Use this skill when the immediate deliverable is language-only Terraform/OpenTofu
HCL:

- Edit or review `.tf`, `.tfvars`, or `.tfvars.json` files.
- Fix HCL syntax, expressions, references, blocks, attributes, or collection types.
- Define or revise variables, outputs, locals, provider blocks, data blocks, resource blocks, or module block syntax.
- Choose typed input contracts, validation blocks, optional attributes, sensitive values, or nullable behavior.
- Choose names, file layout, or formatting for language-level configuration.
- Format or validate configuration without backend access, state, a plan, an apply, or a cloud operation.

This skill owns HCL shape, typed configuration, and readability, not the
operational meaning of the infrastructure.

## Scope

### Language and syntax

- HCL blocks, attributes, labels, expressions, references, functions, conditionals, loops, and collection values.
- Terraform/OpenTofu type constraints, object attributes, `optional()`, `nullable`, `sensitive`, and input validation syntax.
- Correct use of `count`, `for_each`, `dynamic`, `depends_on`, `lifecycle`, `precondition`, `postcondition`, `check`, `moved`, `import`, and `removed` block syntax when the question is about configuration shape.
- Terraform file naming, block ordering, two-space indentation, and `snake_case` identifiers.

### Configuration interfaces

- Variables must have an explicit `description` and `type` unless the target repository has a documented exception.
- Outputs must have a `description` and expose stable values rather than whole provider objects.
- Keep variable validation close to the variable it constrains.
- Preserve existing module input and output names when the task is language-only. Route interface migration or module architecture to `/internal-terraform`.
- Keep environment-specific values in the established `.tfvars` layout and keep secrets out of committed configuration.
- Disclose the Terraform/OpenTofu version floor when using a language feature that requires one.

## Conditional references

- [`references/common-mistakes.md`](references/common-mistakes.md): load when reviewing HCL, typed-interface, or file-level readability mistakes.
- [`references/structure-standard.md`](references/structure-standard.md): load when choosing the default root file or environment layout.
- [`references/template-examples.md`](references/template-examples.md): load when a minimal typed HCL example is useful.

## Validation

The local validation boundary is:

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

Use the `tofu` equivalents when the repository standardizes on OpenTofu.
`init -backend=false` installs providers without configuring a backend, so it
reads no state and needs no cloud credentials. Hand the operational part to
`/internal-terraform` when validation needs backend access, state inspection,
a plan, an apply, credentials, native test execution, CI behavior, or a cloud
operation.

## Routing boundaries

| Immediate request | Owner |
| --- | --- |
| HCL syntax, expressions, types, variables, outputs, `.tfvars`, `.tfvars.json`, or formatting | `internal-tf` |
| Native `.tftest.hcl` or `.tftest.json`, `run`, `assert`, mock providers, or `terraform test`/`tofu test` | `/internal-terraform` |
| Module architecture, state, drift, plan/apply, provider operation, cloud topology, CI, scans, upgrades, recovery, or risk diagnosis | `/internal-terraform` |

A `module` block syntax correction belongs here. Choosing module boundaries,
migrating consumers, or protecting resource identity belongs to
`/internal-terraform`.

## Handoff

- State the Terraform/OpenTofu runtime and version when a language feature has a version floor.
- Name the files and configuration constructs in scope.
- Derive provider schemas and cloud behavior from provider documentation or validation output, not from HCL syntax alone.
- Load only language guidance for a language-only task; state, provider-operation, plan/apply, native-test, CI, and cloud-operation guidance belongs to `/internal-terraform`.
- When the request crosses a boundary, return the language finding and route the remaining work to `/internal-terraform`.

## Output contract

Return:

1. The language or HCL assumption that controls the answer.
2. The exact configuration construct or interface being changed.
3. The smallest valid edit, preserving local layout and contracts.
4. The focused formatting or validation result.
5. A handoff to `/internal-terraform` when the remaining issue is operational, test-related, or provider-specific.

**Complete when:** the edit is the smallest valid change, the validation
boundary above was run or its gap is stated, and every out-of-boundary concern
is handed to `/internal-terraform`.
