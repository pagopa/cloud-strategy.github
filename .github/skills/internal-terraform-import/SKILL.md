---
name: internal-terraform-import
description: Use only when /internal-terraform has handed off an approved Terraform/OpenTofu import assessment or execution with explicit scope and safety evidence.
---

# Terraform Import Execution Owner

This skill is secondary-only. `/internal-terraform` remains the decision owner
and must issue the handoff before this skill is used.

## When to use

Use only for an approved import assessment or execution after the wrapper has
provided the required handoff. Do not use this skill as a general Terraform
entrypoint.

## Handoff gate

Require an explicit wrapper handoff with these fields: `Primary`, `Execution
owner`, `Reason`, `Context`, `Safety evidence`, and `Validation`. The execution
owner must be `/internal-terraform-import`, and the handoff must identify the
consumer root, selected mode, scopes, identity, ownership, state, runner,
mutation, convergence, and recovery evidence.

If the handoff is absent, malformed, or incomplete, return to
`/internal-terraform` without running lookup, state inspection, import, plan,
or apply. The runner enforces the same boundary through its handoff document;
this skill does not infer identity, ownership, permissions, provider aliases,
regions, backend scope, or recovery readiness.

## Ownership

Own portable import assessment and execution after the wrapper handoff. Use the
consumer-supplied runner and resource adapters, preserve remote Terraform state
as resume evidence, default to non-mutating assessment, and require every
live safety gate before import or apply.

Load `references/import-orchestration.md` for bulk or multi-state imports.
Load `references/aws-identity-center-import.md` only for the AWS Identity
Center adapter path.

Route general Terraform semantics to `antonbabenko-terraform-skill`,
language-only HCL to `/internal-tf`, and independent cloud design or governance
to the relevant cloud owner. This skill does not own adoption policy,
general operational validation, or cloud governance.
