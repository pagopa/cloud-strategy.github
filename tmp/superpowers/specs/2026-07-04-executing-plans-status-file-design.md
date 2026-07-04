# Executing Plans Status File Design

## Purpose

Improve `.github/skills/superpowers-executing-plans/SKILL.md` so every plan
execution leaves a compact, deterministic state file next to the plan. The file
must make the plan status obvious and give the next agent enough context to
resume without rereading the whole conversation.

This spec is a design handoff only. It must not implement the skill change.

## Target Skill

- Modify: `.github/skills/superpowers-executing-plans/SKILL.md`
- Do not modify adjacent Superpowers skills unless implementation finds a direct
  contract conflict that blocks this change.
- Keep the skill portable. Do not add repository-local paths, validators, or
  examples beyond generic plan-relative behavior.

## Decisions

- The status file is written next to the original plan file.
- The filename format is `<plan-basename>.<STATUS>.md`.
- `<plan-basename>` is the plan filename without the final `.md` suffix.
- Supported statuses are `DONE`, `BLOCKED`, `PARTIAL`, and `NEEDS_REVIEW`.
- Status values are uppercase.
- The skill writes a status file whenever execution reaches a terminal stop,
  including success, blocker, partial completion, or initial review failure.
- Only one current status file should exist for a plan. Before writing a new
  status file, the agent removes or replaces stale status files for the same
  plan basename.
- The status file should stay short, normally under 40 lines.
- The main session owns the final status file, even when subagents contribute.

## Status Semantics

Use `DONE` only when all planned work is complete, required verification has
passed or any validation gaps are explicitly accepted, and the finishing step is
complete.

Use `PARTIAL` when some plan work was completed but the execution cannot be
declared done. Typical cases include failing final validation, unfinished
finishing work, or a stop after meaningful progress.

Use `BLOCKED` when execution cannot continue without user input, missing access,
missing dependency, unclear instructions, or a repeated non-repairable failure.

Use `NEEDS_REVIEW` when the initial plan review finds critical gaps before
implementation starts, or when the plan itself needs user correction before it
can be safely executed.

## Required File Shape

The status file must use concise Markdown with these sections:

```markdown
# <Plan Title Or Basename> - <STATUS>

## Status
<STATUS>

## Reason
<one or two sentences explaining why this status was chosen>

## Completed
- <brief completed item, or "None">

## Remaining
- <brief remaining item, or "None">

## Validation
- <command/result pairs actually run, or explicit validation gap>

## Next
<single recommended next action>

## Resume Notes
<short notes needed to resume, including any user question or blocker detail>
```

The file must include only commands that were actually run. If validation was
not run, the file must say why.

## Workflow Change

Add a new terminal step to the skill after task execution and after any stop
condition:

1. Determine the final status from the execution outcome.
2. Build the target status filename from the plan path and status.
3. Remove or replace stale sibling files matching the same plan basename and a
   supported status suffix.
4. Write the compact status file.
5. Report the status file path in the final chat response.

This step must also run when the agent stops before implementation because the
plan has critical gaps.

## Relationship To Existing Finishing Step

The existing `superpowers-finishing-a-development-branch` handoff remains part
of the workflow.

`DONE` is valid only after that finishing workflow is complete. If task work is
complete but the finishing workflow is not complete, the correct status is
`PARTIAL` unless the user explicitly accepts the remaining gap.

## Anti-Scope

- Do not create timestamped status history files.
- Do not embed the only state summary inside the original plan.
- Do not require a repository-specific `tmp/superpowers/` path.
- Do not introduce a helper script unless the implementation clearly needs one.
- Do not create status files when there is no reliable plan path.

## Validation

The implementation should run the closest available skill validator for the
changed skill. In this repository, the expected validator is:

```bash
./.github/scripts/.venv/bin/python ./.github/scripts/validate_internal_skills.py --skill superpowers-executing-plans --strict
```

If that validator is unavailable, run the closest Markdown or repository check
and report the validation gap explicitly.

## Acceptance Criteria

- `.github/skills/superpowers-executing-plans/SKILL.md` requires a status file
  for every terminal execution outcome.
- The filename contract is clearly documented as
  `<plan-basename>.<STATUS>.md`.
- The allowed statuses and their meanings are unambiguous.
- The status file content is short and resume-oriented.
- The skill preserves its existing critical-review, task execution, blocker,
  and finishing workflow behavior.
- The implementation validates the changed skill or reports why validation could
  not be run.
