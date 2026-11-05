---
name: internal-terraform-import
description: Use only when /internal-terraform has handed off an approved Terraform/OpenTofu import assessment or execution with explicit scope and safety evidence.
---

# Terraform Import Execution Owner

This skill is secondary-only. `/internal-terraform` remains the decision owner
and must issue the handoff before this skill is used. The bundle owns the
provider-neutral adoption protocol after that handoff; provider and resource
logic remains in consumer-supplied adapters.

## When to use

Use only for an approved import assessment or execution after the wrapper has
provided the required handoff. Route every other Terraform request to
`/internal-terraform`.

## Handoff gate

Require an explicit wrapper handoff with these fields: `Primary`, `Execution
owner`, `Reason`, `Context`, `Safety evidence`, and `Validation`. `Primary`
must be `/internal-terraform`, the execution owner must be
`/internal-terraform-import`, and the handoff must identify the consumer root,
selected mode, scopes, identity, ownership, state, runner, mutation,
convergence, and recovery evidence. Protocol v2 is mandatory for live
execution; protocol v1 is assessment-only and is never converted implicitly.

The machine-readable handoff projects these fields as `primary_owner`,
`execution_owner`, `reason`, `context`, `safety_evidence`, and `validation`.
`context.consumer_root`, `context.mode`, and `context.scopes` must match the
top-level run fields. The runner validates this projection for assessment and
live runs before loading adapters or inspecting state.

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

For live adoption, validate one explicit disposition per manifest record.
`import_candidate` and a proven `moved_candidate` are the only adoption
dispositions. `absent_create`, collisions, disputed ownership, unsupported
capabilities, and other non-adoption dispositions are deferred or stop the run.
Classify the machine-readable plan before mutation and fail closed on
`create`, `update`, `delete`, `replace`, or unknown actions. Every live mode
must save and bind one plan artifact to the run, state boundary, configuration,
dependency lock, and artifact digest, then apply that exact artifact.

Authorization, runtime evidence, and the completion receipt are separate
records sharing one `run_id`. Do not rewrite an authorization record with
runtime results. The receipt links the authorization and evidence digests, the
applied plan, final state identities, live verification, post-apply plan, and
recovery evidence.

## Run

Before any run, load
[`references/import-orchestration.md`](references/import-orchestration.md)
for the JSONL record shape, dispositions, modes, resume, generated HCL, plan
safety, and records. Load
[`references/aws-identity-center-import.md`](references/aws-identity-center-import.md)
only for the AWS Identity Center adapter path.

Invoke `scripts/import-manifest-runner.sh` from this bundle:

```text
Usage: import-manifest-runner.sh --manifest FILE --mode script|hcl --root DIR --handoff FILE --runner-adapter FILE --resource-adapter FILE [options]
Options: --runner FILE --scope SCOPE --dry-run --continue-on-error --live
```

- Pass `--mode` and `--root` explicitly; they default to `script` and the
  current directory, and must match the handoff.
- `hcl` mode requires exactly one `--scope` authorized by the handoff.
- Without `--live`, a run performs no import, apply, or state mutation. `hcl`
  mode still writes the scoped `imports.generated.tf`.
- `--dry-run` reports candidates only and cannot be combined with `--live`.
- `--continue-on-error` is opt-in and still exits non-zero when any record
  fails.
- `--live` requires a protocol v2 handoff with `decision=execute` and complete
  safety evidence.

The consumer root's executable `./terraform.sh` is the mandatory default
runner. An absent, unexecutable, or capability-incomplete runner is a
fail-closed stop. The runner never falls back to direct `terraform import`.
An explicit `--runner`, and every live run, must use exactly the runner path
authorized in the handoff; `--runner` cannot replace that authorization.

The runner and resource adapters are sourced Bash files. The runner checks
these functions before use:

| Function | Required when |
| --- | --- |
| `runner_preflight` | Every run |
| `runner_state_identity` | Every run |
| `runner_plan` | Every run |
| `resolve_import_record` | Every run (resource adapter) |
| `runner_destination_exists` | `hcl` mode |
| `runner_plan_json` | Live runs |
| `runner_plan_saved` | Live runs |
| `runner_apply_saved` | Live runs |
| `runner_move` | Live adoption of a `moved_candidate` record by state move |

**Complete when:** the run exits zero with every record in a terminal status,
or it stops fail-closed with the failing record, reason, and retained recovery
evidence reported.

## Final report

Report, in this order:

1. Run ID, mode, consumer root, scopes, and whether the run was live.
2. Per-record status as emitted by the runner (`imported`, `moved`,
   `skipped_already_managed`, `excluded_by_disposition`, `not_found`,
   `ambiguous`, `aws_error`, or `terraform_error`) and the runner summary
   counts.
3. Plan classification and the saved plan artifact, for live runs.
4. Paths of the authorization, evidence, recovery, and receipt records under
   `.terraform-import-adoption/`.
5. Exit status, unresolved evidence gaps, and the next required action.

## Boundaries

Route general Terraform semantics to `/antonbabenko-terraform-skill`,
language-only HCL to `/internal-tf`, and independent cloud design or governance
to the relevant cloud owner. This skill does not own adoption policy, general
operational validation, or cloud governance.

When changing this bundle, load
[`references/maintenance.md`](references/maintenance.md).
