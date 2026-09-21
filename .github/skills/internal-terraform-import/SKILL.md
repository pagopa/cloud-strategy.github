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
provided the required handoff. Do not use this skill as a general Terraform
entrypoint.

## Handoff gate

Require an explicit wrapper handoff with these fields: `Primary`, `Execution
owner`, `Reason`, `Context`, `Safety evidence`, and `Validation`. The execution
owner must be `/internal-terraform-import`, and the handoff must identify the
consumer root, selected mode, scopes, identity, ownership, state, runner,
mutation, convergence, and recovery evidence. Protocol v2 is mandatory for
live execution; protocol v1 is assessment-only and is never converted
implicitly.

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

## Validation and testing

Run the focused bundle tests and syntax checks after changes:

```text
python -m pytest .github/skills/internal-terraform-import/tests -q
python -m py_compile .github/skills/internal-terraform-import/scripts/adoption_protocol.py
bash -n .github/skills/internal-terraform-import/scripts/import-manifest-runner.sh
shellcheck -s bash .github/skills/internal-terraform-import/scripts/import-manifest-runner.sh
```

The runner remains a single operator entrypoint by design. Runner and resource
adapters are sourced into the same Bash process, and the live lifecycle shares
trap cleanup, fail-closed exits, plan artifacts, authorization, evidence, and
receipt state. Splitting those stages would require a new cross-file state
contract and would make adapter injection and immutable-record ordering less
explicit. Keep the exception bounded: new provider or resource behavior must
remain in adapters, and a future lifecycle helper extraction must preserve the
bundle-local portability contract.

The live protocol tests must cover protocol-v2 handoff validation, complete
plan-action classification, import and state-move adoption, exact saved-plan
application, immutable records, and bundle portability.

Load `references/import-orchestration.md` for bulk or multi-state imports.
Load `references/aws-identity-center-import.md` only for the AWS Identity
Center adapter path.

Route general Terraform semantics to `antonbabenko-terraform-skill`,
language-only HCL to `/internal-tf`, and independent cloud design or governance
to the relevant cloud owner. This skill does not own adoption policy,
general operational validation, or cloud governance.
