---
name: internal-tf
description: Use when Terraform/OpenTofu HCL, .tf, .tfvars, or typed configuration language is the immediate concern.
---

# Terraform Language

## Reference files

- `references/common-mistakes.md`: Language and typed-interface mistakes to check when reviewing configuration.
- `references/structure-standard.md`: Default root file and environment layout for new configurations.
- `references/template-examples.md`: Minimal HCL examples for typed inputs, resources, and outputs.

## When to use

Use this skill when the immediate deliverable is Terraform/OpenTofu configuration language or HCL structure:

- Edit or review `.tf`, `.tfvars`, or `.tfvars.json` files.
- Fix HCL syntax, expressions, references, blocks, attributes, or collection types.
- Define or revise variables, outputs, locals, provider blocks, data blocks, resource blocks, or module block syntax.
- Choose typed input contracts, validation blocks, optional attributes, sensitive values, or nullable behavior.
- Organize Terraform files and environment values while preserving an established repository layout.
- Format or validate configuration without needing a state, plan, apply, or cloud operation.

## Scope

This is the language specialist for Terraform/OpenTofu. It owns the shape and readability of configuration, not the operational meaning of the infrastructure.

### Language and syntax

- HCL blocks, attributes, labels, expressions, references, functions, conditionals, loops, and collection values.
- Terraform/OpenTofu type constraints, object attributes, `optional()`, `nullable`, `sensitive`, and input validation syntax.
- Correct use of `count`, `for_each`, `dynamic`, `depends_on`, `lifecycle`, `precondition`, `postcondition`, `check`, `moved`, `import`, and `removed` block syntax when the question is about configuration shape.
- Terraform file naming, block ordering, two-space indentation, and `snake_case` identifiers.

### Configuration interfaces

- Variables must have an explicit `description` and `type` unless the target repository has a documented exception.
- Outputs must have a `description` and expose stable values rather than whole provider objects.
- Keep variable validation close to the variable it constrains.
- Preserve existing module input and output names when the task is a language-only edit. Route interface migration or module architecture to `antonbabenko-terraform-skill`.
- Keep environment-specific values in the established `.tfvars` layout and keep secrets out of committed configuration.

### Validation

Use the narrowest available checks for the changed configuration:

```bash
terraform fmt -check -recursive
terraform validate
```

Use `tofu fmt` and `tofu validate` when the repository standardizes on OpenTofu. If validation requires provider installation, backend access, state inspection, a plan, or an apply, hand the operational part to `antonbabenko-terraform-skill`.

## Routing boundaries

| Immediate request | Owner |
| --- | --- |
| HCL syntax, expressions, types, variables, outputs, `.tfvars`, or formatting | `/internal-tf` |
| Native `.tftest.hcl` or `.tftest.json`, `run`, `assert`, mock providers, or `terraform test`/`tofu test` | `/ibm-terraform-test` |
| Module architecture, state, drift, plan/apply, CI, scans, provider upgrades, recovery, or risk diagnosis | `/antonbabenko-terraform-skill` |

A `module` block syntax correction belongs here. Choosing module boundaries, migrating consumers, or protecting resource identity belongs to Anton.

## Handoff rules

- State the Terraform/OpenTofu runtime and version when a language feature has a version floor.
- Name the files and configuration constructs in scope.
- Do not invent provider schemas or cloud behavior from HCL syntax alone.
- Do not preload test, state, CI, security, or cloud-operation guidance for a language-only task.
- When the request crosses a boundary, return the language finding and identify the specialist that must own the remaining work.

## Output contract

Return:

1. The language or HCL assumption that controls the answer.
2. The exact configuration construct or interface being changed.
3. The smallest valid edit, preserving local layout and contracts.
4. The focused formatting or validation result.
5. A handoff to the router when the remaining issue is operational, test-related, or provider-specific.
