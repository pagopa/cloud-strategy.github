---
name: internal-gateway-execute-plans
description: "Use when executing or resuming an approved repository-owned retained plan under tmp/superpowers/plans/."
---

# Internal Gateway Execute Plans

Execute one approved retained plan directly in the current session. This
gateway owns the task loop, validation, bounded repair, stopping decision, and
user report. It does not delegate plan work.

## When to use

- Execute or resume an approved repository-owned retained plan under
   `tmp/superpowers/plans/`.

## Use And Boundaries

- Use only for an approved plan under `tmp/superpowers/plans/`.
- The writer-owned `## Execution Manifest` v3 is authoritative for targets,
  tasks, controls, validations, approval, warnings, deviations, and authority
  boundaries.
- Do not rewrite the Manifest or broaden the plan. A plan change requires the
  writer route and refreshed approval; v3 has no hash or fingerprint binding.
- Do not dispatch a subagent, worker, model switch, or delegated execution
  path. `internal-luna-executor` is metadata only and is never invoked here.
- Do not run Git mutations. Leave the worktree uncommitted.

## Manifest Contract Loading

Load the bundle-local `references/manifest-v3.md` only for Manifest v3 validation
or review. It is the detailed producer-consumer checklist for exact Manifest
v3 fields, nested values, projection bindings, task references, approval and
status separation, bootstrap, handoff, retry posture, and no-Git rules.
The executor's `plan_execution.py` and `scripts/run.sh preflight` remain the
sole mechanical authority; the parser wins if prose and implementation differ.
Keep the always-loaded route focused on physical preflight, state binding,
direct task execution, recovery, completion, and handoff. Do not create a
second parser or a shared cross-bundle dependency.

Before any task edit, resolve the executor from its physically loaded bundle
entrypoint; a consumer working directory or a home-directory fallback is never
an executor owner.

The executor bundle owns its runtime dependencies. Declare direct dependencies
in `scripts/requirements.in`, generate the hash-locked
`scripts/requirements.txt` with the repository lock generator, and invoke the
bundle through `scripts/run.sh`. The runner must derive its physical bundle
from its loaded entrypoint and must not use repository-global requirements.
Provision the local runtime only with the explicit
`bash <physical-executor-bundle>/scripts/run.sh --bootstrap` command; ordinary
preflight and state-check calls reuse the provisioned runtime and fail closed
when it is unavailable.

Bootstrap output is a separate compact projection with exactly `check`,
`status`, and `next_action`; status is only `PASS` or `BLOCKED`. A bounded local
bootstrap collects its finite local checks and stops before external or live
work after a blocker. Delivery readiness remains five independent verdicts:
`structure`, `semantic_review`, `artifact_provenance`, `source_baseline`, and
`execution_readiness`, each with outcome, coverage, and limit. Persist those
five records in runtime state; a `DONE` state requires all five to be passed.
Do not replace those records with a standalone `validated` field.

## Bind Before Editing

1. Confirm the exact retained-plan path. Do not ask the user to re-confirm
   approval; the approved plan is the authority.
2. Resolve the loaded physical bundle and run its runner:
   `bash <physical-executor-bundle>/scripts/run.sh preflight <plan> --format compact`.
3. Record approval evidence as `external-authority-record` citing the approved
   plan, then create the one `PARTIAL` status sibling with zero completed tasks
   before the first task edit.
4. Record the worktree baseline and the plan's required baseline validation.
5. Read `## Control Inventory` and map each obligation to a validation,
   external or human follow-up, or authority boundary.
6. Stop when a required control is uncovered or the plan is stale. Ask one
   focused authority question only after local checks are
   exhausted.

## Direct Finish Loop

For each Manifest task, in order:

1. Apply the task posture and load `/internal-tdd` when executable or
   evaluable behavior changes. Establish red evidence only for
   `mandatory-test-first` tasks.
2. Execute the approved task in the current session. Preserve task IDs and
   dependencies; do not invent a parallel execution API.
3. Run the task's focused validation and record the command, result, and
   evidence. Continue independent tasks when a failure is pre-existing or
   unrelated.
4. If validation fails, diagnose the controlling local cause. Try a distinct
   safe repair only when it is directly implied by the task acceptance, inside
   an approved target, and does not change scope or authority.
5. Re-run the same validation after a repair. Do not repeat an unchanged
   attempt. Preserve any residual failure and its effect on remaining tasks.
6. Audit the approved targets for clearly implied omissions before marking the
   task complete. An omission that is normative, unsafe, out of scope, or
   authority-required stops execution.

## Delivery Verdicts

Readiness evidence uses five independent categories: `structure`,
`semantic_review`, `artifact_provenance`, `source_baseline`, and
`execution_readiness`. Each category reports an outcome, its coverage, and its
limit. An aggregate result may be green only when every required category is
concluded and passed; missing or inconclusive categories keep the aggregate
inconclusive. Persist the category records in the status sibling and do not
use a standalone `validated` signal as user-facing readiness evidence.

## Stop And State

Runtime execution state uses exactly one readable YAML sibling named
`<plan-basename>.<STATUS>.yaml`. Do not create Markdown status siblings or
write more than one runtime status sibling. The YAML object has exactly these
fields:

`schema_version`, `status`, `plan`, `approval_evidence`, `delivery_verdicts`,
`completed_task_ids`, `remaining_task_ids`, `last_validation`, `next_action`,
`warnings`, `deviations`.

Runtime status and the Execution Manifest use schema version `2`. Older status
siblings and v1 plans must be regenerated before resuming.
YAML is the only runtime status representation.

`status` is exactly one of `DONE`, `DONE_WITH_WARNINGS`, `PARTIAL`, or `BLOCKED`:

- `DONE`: every task is complete, every required local or observable check
  passes, no warning remains, no deviation remains, and no task remains.
- `DONE_WITH_WARNINGS`: every task is complete and all five delivery verdicts
  pass; at least one typed warning is visible. Warning kinds are
  `human-follow-up`, `external-unavailable`, and `missing-tool-equivalent`.
  Technical failures never use this status.
- `PARTIAL`: execution is paused but remains resumable; remaining task IDs and
  one concrete next action are recorded.
- `BLOCKED`: an authority, scope, safety, or unresolved task-local condition
  prevents progress; record one focused next action and make no out-of-scope
  edit.

`approval_evidence` records exactly the source and statement of execution
approval. The executor derives it from the approved plan as
`external-authority-record` without asking the user; `current-conversation`
remains admissible only when an explicit statement already exists. The
statement is exactly `explicit execution approval`. `delivery_verdicts` contains the five canonical category records.
Each warning has exactly `kind`, `evidence`, and `next_action`. Each deviation
has exactly `task`, `mismatch`, and `resolution`; only unequivocal path moves,
structural ID/name alignment, equivalent missing-tool replacements, and targets
already in the declared state may be recorded.

The uppercase filename status and YAML `status` must agree. Validate it with
the loaded bundle runner:

`bash <physical-executor-bundle>/scripts/run.sh state-check <plan> <plan-basename>.<STATUS>.yaml --format compact`

The validator checks the Manifest, sibling location, plan binding, task IDs,
warning/deviation shapes, and status/task consistency. Malformed, stale,
duplicate, conflicting, or interrupted state remains blocked. The validator
does not execute work or select repairs.

## Completion Evidence

Before recording a terminal state, run the plan's required final validations,
preserve the baseline/final delta, run `git diff --check`, and load
`/superpowers-verification-before-completion` before claiming success. Load
`/addyosmani-code-simplification` only when the approved plan authorizes it.

Mechanical preflight rejects `.git` targets and explicit mutating Git
subcommands in manifest commands or task obligations. Execution still requires
the repository's permission boundary for commands assembled outside the
manifest; this gateway must never run Git mutations.

Pending human judgment or unavailable external evidence is recorded as a
follow-up when no material implementation failure remains. It does not replace
technical validation or justify an out-of-scope change.

For each task, use the manifest's finite `max_corrective_retries` budget, from
1 through 5, and retain retry state across resumptions. A recovery attempt must
be task-local, in scope, safe, and distinct; unchanged failure signatures stop
that task rather than reopening it indefinitely. Continue independent tasks
around a pre-existing failure, audit clearly implied omissions inside approved
targets, and preserve residual failures. Stop with `BLOCKED` for an authority,
scope, safety, no-progress, or unresolved task-local barrier, recording the
attempted recovery, no-progress or inadmissible-alternative evidence, and one
concrete unblock action. Never weaken a validation or represent a technical
failure as `DONE_WITH_WARNINGS`.

## User Report

For `DONE`, return exactly four lines, in this order, with no extra status prose:

`Plan: <path and terminal status>`

`Changed: <files or no changes>`

`Checks: <validation evidence and residual gap>`

`Next: <one action or none>`

For `DONE_WITH_WARNINGS`, add one `Warning:` line after `Checks`. For `PARTIAL`
and `BLOCKED`, report 1-3 evidence-backed causes under `Perché mi sono fermato`
and 2-4 concrete actions under `Cosa fare`; do not hide a blocker behind the
compact four-line projection.
