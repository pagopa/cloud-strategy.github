# Portable Import Orchestration

Use this reference after `/internal-terraform` hands off a bulk or multi-state
adoption import. The selected consumer repository remains responsible for its
root, wrapper contract, identity, scope catalogue, and mutation authority.

## Input and adapters

The only input format is JSONL. Each non-empty line must be one JSON object
with this stable record shape:

```json
{"scope":"string","address":"terraform address","resource_kind":"adapter key","lookup":{},"disposition":"import_candidate"}
```

Live protocol v2 records must declare exactly one disposition. The generic core
recognizes `already_managed`, `import_candidate`, `absent_create`,
`moved_candidate`, `collision`, `ambiguous_live_identity`,
`state_identity_mismatch`, `disputed_ownership`, `undeclared_remote`,
`unsupported_capability`, and `excluded_by_scope`. Only `import_candidate` and
`moved_candidate` may enter adoption. `absent_create` is deferred to a later
convergence decision.

The orchestrator normalizes records, rejects malformed or ambiguous input, and
passes them to two consumer-supplied adapters:

- The runner adapter proves state inspection, import, plan, and (when live
  execution is explicitly enabled) saved-plan and exact-apply capability.
- The resource adapter resolves one canonical live identity and one literal
  import ID for the declared resource kind.

The handoff document must also carry the wrapper projection `primary_owner`,
`execution_owner`, `reason`, `context`, `safety_evidence`, and `validation`.
The importer validates that projection, including root, mode, and scope
agreement, before loading adapters or inspecting state.

Protocol v2 authority fields are structured records. `mutation_authority` must
include an approved status, actor, decision ID, consumer root, allowed scopes,
and selected mode. A `converge` execution mode additionally requires a
separate `convergence_authority` record with the same bindings. Live import
records also bind `live_authorization` and `identity_confirmation` to the
decision, root, state scope, scopes, and import mode.
This bundle validates a separate `convergence_authority` when a handoff names
`converge`, but the current entrypoint rejects convergence execution; route
that operation back through the convergence owner.

When the selected consumer root has `./terraform.sh`, it is the required
default runner. An absent, unexecutable, or capability-incomplete wrapper is a
fail-closed stop. The orchestrator never invokes `terraform import` directly as
a fallback and never infers a profile, account, region, backend, alias, or
scope. For live execution, the selected runner path must also exactly match
the path authorized in the handoff; `--runner` cannot replace that authorization.

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
The HCL runner adapter must also verify each expanded configuration destination
before generation, and records must be re-resolved for canonical identity
immediately before exact apply.
Remove the generated file only after all expected identities match and the
post-import plan has no unexpected creates. Retain it unchanged after any
generation, import, verification, or plan failure so an operator can diagnose
or resume safely.

## Plan safety

The core classifies machine-readable `import`, `moved`, `no-op`, `create`,
`update`, `delete`, `replace`, and unknown actions. Live execution stops for
every action outside the adoption-safe set `{import, moved, no-op}`. A moved
action also requires a canonical-identity, state-lineage, collision, and
no-remote-mutation proof.

Live execution calls `runner_plan_saved` once, binds the resulting artifact to
the run ID, root, state scope, lineage, serial, configuration digest,
dependency-lock digest, and artifact digest, then passes the same path to
`runner_apply_saved`. It does not regenerate a plan for apply. In HCL mode,
the runner receives the scoped adoption-records path as the fifth argument to
both functions so an adapter can plan and apply verified state moves without
putting provider-specific move logic in the generic core.

## Records and recovery

Authorization, runtime evidence, and completion are separate JSON records under
the consumer root's `.terraform-import-adoption/` directory. They share the
handoff `run_id`; authorization and evidence are immutable once written. A
successful HCL run retains its authorization, evidence, recovery, receipt,
saved plan, and plan envelope for resume and diagnosis. The run ID is a safe
filename token. Runtime evidence includes desired, live, and state inventory
digests, state lineage and serial, reconciliation dispositions, collision and
ambiguity results, tool versions, timestamps, plan classification, and live
verification results. If a live lifecycle fails, the runner must persist the
run recovery record; inability to write that record is itself a terminal error.
