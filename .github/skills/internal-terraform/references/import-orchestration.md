# Portable Import Orchestration

Use this reference for bulk or multi-state adoption imports. The selected
consumer repository remains responsible for its root, wrapper contract,
identity, scope catalogue, and mutation authority.

## Input and adapters

The only input format is JSONL. Each non-empty line must be one JSON object
with this stable record shape:

```json
{"scope":"string","address":"terraform address","resource_kind":"adapter key","lookup":{}}
```

The orchestrator normalizes records, rejects malformed or ambiguous input, and
passes them to two consumer-supplied adapters:

- The runner adapter proves state inspection, import, plan, and (when live
  HCL execution is explicitly enabled) apply capability.
- The resource adapter resolves one canonical live identity and one literal
  import ID for the declared resource kind.

When the selected consumer root has `./terraform.sh`, it is the required
default runner. An absent, unexecutable, or capability-incomplete wrapper is a
fail-closed stop. The orchestrator never invokes `terraform import` directly as
a fallback and never infers a profile, account, region, backend, alias, or
scope.

## Modes and resume

Select exactly one mode per run: `script` for imperative imports or `hcl` for
generated import blocks. An address cannot be processed by both modes in one
run. Process HCL one explicit scope at a time. Compare the adapter's canonical
identity with runner state before importing: equal identity is
`skipped_already_managed`, missing state is a candidate, and a mismatch is a
fail-closed error. Remote Terraform state is the resume source of truth; no
resume sidecar or alternate manifest format is introduced.

The default path is non-mutating. Dry-run reports candidates without import.
Continue-on-error is opt-in and still exits non-zero when any record remains
failed. Do not use `eval`, `-lock=false`, automatic `state rm`, or destructive
remediation.

## Generated HCL lifecycle

HCL mode writes one scoped `imports.generated.tf` only from adapter-known
destination shapes, provider aliases, and verified literal IDs. It must not
interpolate a raw manifest address into a `to` expression. Group only
homogeneous resource kinds into known `for_each` import blocks, and ensure the
destination resource addresses already exist in the verified configuration.

Generation alone performs no apply. An explicit live path must use the runner
adapter for plan, apply, state identity verification, and a post-import plan.
Remove the generated file only after all expected identities match and the
post-import plan has no unexpected creates. Retain it unchanged after any
generation, import, verification, or plan failure so an operator can diagnose
or resume safely.
