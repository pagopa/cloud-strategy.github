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

## Bind Before Editing

1. Confirm the exact retained-plan path and explicit approval.
2. Run `python3 scripts/plan_execution.py preflight <plan> --format compact`.
3. Record the semantic fingerprint, exact content hash, worktree baseline, and
   the plan's required baseline validation.
4. Read `## Control Inventory` and map each obligation to a validation,
   external or human follow-up, or authority boundary.
5. Stop when a required control is uncovered, the plan is stale, or approval is
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
inconclusive. Do not use a standalone `validated` signal as user-facing
readiness evidence.

The serial predecessor gate must verify the IGI-01 state sibling, its exact
plan and manifest hashes, `DONE` task closure, final validation evidence, and
an observed IDEA workflow-count record before T1 begins. A native seam test
that demonstrates count derivation is evidence of coverage, not retrospective
authorship or proof of a historical execution run.

## Stop And State

Use exactly one compact JSON sibling when execution must be resumed or its
terminal evidence must be recorded: `<plan-basename>.status.json`. Do not
create Markdown status siblings or separate protocol evidence files. The JSON
object has exactly these fields:

`schema_version`, `status`, `plan`, `plan_fingerprint`, `content_hash`,
`completed_task_ids`, `remaining_task_ids`, `last_validation`, `next_action`.

`status` is exactly one of `DONE`, `PARTIAL`, or `BLOCKED`:

- `DONE`: every task is complete, every required local or observable check
  passes, and no task remains.
- `PARTIAL`: execution is paused but remains resumable; remaining task IDs and
  one concrete next action are recorded.
- `BLOCKED`: an authority, scope, safety, or unresolved task-local condition
  prevents progress; record one focused next action and make no out-of-scope
  edit.

Bind the sibling to the plan's semantic fingerprint and exact content hash.
The state path is in the same directory as the plan, with `.md` replaced by
`.status.json`. Validate it with:

`python3 scripts/plan_execution.py state-check <plan> <plan-sibling>.status.json --format compact`

The validator checks the Manifest, sibling location, hashes, plan binding, task
IDs, and status/task consistency. It does not execute work or select repairs.

## Completion Evidence

After the last task, run the plan's required final validations, preserve the
baseline/final delta, run `git diff --check`, and load
`/superpowers-verification-before-completion` before claiming success. Load
`/addyosmani-code-simplification` only when the approved plan authorizes it.

Pending human judgment or unavailable external evidence is recorded as a
follow-up when no material implementation failure remains. It does not replace
technical validation or justify an out-of-scope change.

## User Report

Always return exactly four lines, in this order, with no extra status prose:

`Plan: <path and terminal status>`

`Changed: <files or no changes>`

`Checks: <validation evidence and residual gap>`

`Next: <one action or none>`
