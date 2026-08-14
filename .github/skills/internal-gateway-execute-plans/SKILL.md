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
- The writer-owned `## Execution Manifest` v1 is authoritative for targets,
  tasks, controls, validations, approval, hashes, and authority boundaries.
- Do not rewrite the Manifest or broaden the plan. A plan change requires the
  writer route, refreshed approval, and refreshed hashes.
- Do not dispatch a subagent, worker, model switch, or delegated execution
  path. `internal-luna-executor` is metadata only and is never invoked here.
- Do not run Git mutations. Leave the worktree uncommitted.

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

1. Confirm the exact retained-plan path and explicit approval.
2. Resolve the loaded physical bundle and run its runner:
   `bash <physical-executor-bundle>/scripts/run.sh preflight <plan> --format compact`.
3. Record explicit approval evidence bound to the semantic fingerprint and
   exact content hash, then create the one `PARTIAL` status sibling with zero
   completed tasks before the first task edit.
4. Record the worktree baseline and the plan's required baseline validation.
5. Read `## Control Inventory` and map each obligation to a validation,
   external or human follow-up, or authority boundary.
6. Stop when a required control is uncovered, the plan is stale, or approval is
   absent. Ask one focused authority question only after local checks are
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

`schema_version`, `status`, `plan`, `plan_fingerprint`, `content_hash`,
`approval_evidence`, `delivery_verdicts`, `completed_task_ids`,
`remaining_task_ids`, `last_validation`, `next_action`.

Runtime status uses schema version `2`; the Execution Manifest remains schema
version `1`. Older status siblings must be regenerated before resuming.
YAML is the only runtime status representation.

`status` is exactly one of `DONE`, `PARTIAL`, or `BLOCKED`:

- `DONE`: every task is complete, every required local or observable check
  passes, and no task remains.
- `PARTIAL`: execution is paused but remains resumable; remaining task IDs and
  one concrete next action are recorded.
- `BLOCKED`: an authority, scope, safety, or unresolved task-local condition
  prevents progress; record one focused next action and make no out-of-scope
  edit.

`approval_evidence` records the source and statement of explicit execution
approval and repeats the exact `plan_fingerprint` and `content_hash` it
authorizes. The supported sources are `current-conversation` and
`external-authority-record`; the statement is exactly `explicit execution
approval`. `delivery_verdicts` contains the five canonical category records.

Bind the sibling to the plan's semantic fingerprint and exact content hash.
The uppercase filename status and YAML `status` must agree. Validate it with
the loaded bundle runner:

`bash <physical-executor-bundle>/scripts/run.sh state-check <plan> <plan-basename>.<STATUS>.yaml --format compact`

The validator checks the Manifest, sibling location, hashes, plan binding, task
IDs, and status/task consistency. Malformed, stale, duplicate, conflicting, or
interrupted state remains blocked. The validator does not execute work or
select repairs.

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

## User Report

Always return exactly four lines, in this order, with no extra status prose:

`Plan: <path and terminal status>`

`Changed: <files or no changes>`

`Checks: <validation evidence and residual gap>`

`Next: <one action or none>`
