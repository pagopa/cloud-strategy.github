---
name: internal-tf
description: Use when Terraform/OpenTofu language-only HCL is the immediate concern. Route module architecture, state, plan or apply, provider operation, native `.tftest.hcl` tests, CI, scans, upgrades, and risk diagnosis to /internal-terraform.
---

# Terraform/OpenTofu Language

## Reference files

- `references/common-mistakes.md`: Load when reviewing HCL or typed-interface mistakes.
- `references/structure-standard.md`: Load when choosing the default root file or environment layout.
- `references/template-examples.md`: Load when a minimal typed HCL example is useful.

## When to use

Use this skill when the immediate deliverable is language-only Terraform/OpenTofu
HCL:

- Edit or review `.tf`, `.tfvars`, or `.tfvars.json` files.
- Fix HCL syntax, expressions, references, blocks, attributes, or collection types.
- Define or revise variables, outputs, locals, provider blocks, data blocks, resource blocks, or module block syntax.
- Choose typed input contracts, validation blocks, optional attributes, sensitive values, or nullable behavior.
- Choose names, file layout, or formatting for language-level configuration.
- Format or validate configuration without needing state, provider installation, a plan, an apply, or a cloud operation.

## Scope

This is the lightweight language-only owner for Terraform/OpenTofu. It owns
HCL shape, typed configuration, and readability, not the operational meaning
of the infrastructure.

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

## Validation

The maximum local validation boundary is:

```bash
terraform fmt -check -recursive
terraform validate
```

Use `tofu fmt` and `tofu validate` when the repository standardizes on OpenTofu. If validation requires provider installation, backend access, state inspection, a plan, an apply, credentials, native test execution, CI behavior, or cloud operation, hand the operational part to `/internal-terraform`.

## Routing boundaries

| Immediate request | Owner |
| --- | --- |
| HCL syntax, expressions, types, variables, outputs, `.tfvars`, `.tfvars.json`, or formatting | `/internal-tf` |
| Native `.tftest.hcl` or `.tftest.json`, `run`, `assert`, mock providers, or `terraform test`/`tofu test` | `/internal-terraform` |
| Module architecture, state, drift, plan/apply, provider operation, cloud topology, CI, scans, upgrades, recovery, or risk diagnosis | `/internal-terraform` |

A `module` block syntax correction belongs here. Choosing module boundaries,
migrating consumers, or protecting resource identity belongs to Anton through
`/internal-terraform`.

## Handoff rules

- State the Terraform/OpenTofu runtime and version when a language feature has a version floor.
- Name the files and configuration constructs in scope.
- Do not invent provider schemas or cloud behavior from HCL syntax alone.
- Do not preload state, provider-operation, plan/apply, native-test, CI, or cloud-operation guidance for a language-only task.
- When the request crosses a boundary, return the language finding and identify `/internal-terraform` as the owner of the remaining work.

## Output contract

Return:

1. The language or HCL assumption that controls the answer.
2. The exact configuration construct or interface being changed.
3. The smallest valid edit, preserving local layout and contracts.
4. The focused formatting or validation result.
5. A handoff to `/internal-terraform` when the remaining issue is operational, test-related, or provider-specific.
