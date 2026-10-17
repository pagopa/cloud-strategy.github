---
name: internal-gateway-execute-plans
description: Use when the user invokes execution of an identified retained implementation plan or resumes its authorized tasks.
---

# Internal Gateway Execute Plans

This gateway wraps `/mattpocock-implement` for continuous execution of an
identified retained plan. The user's invocation authorizes its declared tasks;
the gateway owns scope, progress, checks, and one final execution review.

## When to use

- The user invokes execute plans for a plan identified by explicit path or
  unambiguous active conversation context.
- The user resumes that plan or its explicitly selected subset, preserving the
  current source and stable task contracts.

Route an unclear idea to `/internal-gateway-idea` and a missing plan to
`/internal-gateway-writing-plans`. Legacy `## Execution Manifest` plans and
historical run files remain read-only; route explicit re-authoring to the writer.
They do not grant current authority or block a normal resume of a current plan.

## Approval and task contract

Select the explicit path or active plan. Ask which plan only when selection is
ambiguous; never choose the latest file merely by timestamp. The user's
invocation is approval of every declared task unless they limited the subset.
Do not ask for another plan approval or confirmation after each task. A writer
result, readiness flag, or internal skill call is not a user invocation.
An explicit natural-language execution request is sufficient when the plan is
unambiguous. A skill mention is not required; a vague acknowledgement is not
an execution request.

Verify source coherence and consume the plan's stable task IDs, criteria,
dependencies, checks, writable paths, and explicitly selected human gates.
Unresolved required references block affected tasks. Material source or contract
changes need reevaluation and reapproval, not reconstruction from the spec.
Checkbox and concise verification/blocker changes in `Progress` are state, not
contract drift, and do not invalidate approval.

Each task's declared writable paths are its perimeter, with one limited
exception: update only checklist state and concise execution evidence in the
selected plan's `Progress` section. Do not change requirements or scope there.
`Files likely touched` is not authority. Preserve user changes and stop on
conflicts or out-of-scope writes. Never stash, overwrite user work, stage,
commit, create a branch, or create a worktree. New targets outside the approved
plan and separate provider or destructive actions need their own authority.

## Implementer handoff

Pass the identified plan and full authorized task set to
`/mattpocock-implement`. Its commit and per-invocation review instructions are
subordinate to this gateway: no Git mutation, no routine per-task full review,
and one whole-plan review at the end. Keep `/internal-tdd` posture and native
checks authoritative. Do not replace it with a parallel executor or widen scope.
If it is not loaded, locate and read its `SKILL.md` in the declared skill roots
without asking for another mention. A readable file does not prove execution
capability: report a genuinely missing file or unsupported host capability
before affected writes; do not substitute another executor.

Execute in dependency order. Run each task's required checks and record their
actual results in `Progress`; count completion only after they pass. Continue
through automatic checkpoints and repair safe in-scope failures without routine
permission prompts. A blocker stops affected tasks and their dependents;
independent authorized tasks may continue. Preserve explicit user gates and stop
unsafe or out-of-scope work, conflicts, and material contract changes.

Do not add skill evaluation runs or baselines to an approved plan. Report
optional unavailable evaluations as `not-run`. A failed or unavailable required
check remains a blocker to whole-plan completion. Structural validation does
not prove skill behavior. Paid runs require an explicit initial spending limit.

## Review without commits

Before writes, record HEAD and the initial state of authorized paths. Preserve
existing user edits with a targeted disposable snapshot when needed; retain it
on resume. Do not copy secrets or follow symlinks outside write authority.

Give `/mattpocock-code-review` one final review package: plan requirements and
actual changes from execution start to end, including untracked files, deletions,
and both rename endpoints. Use HEAD and captured initial file state to separate
user edits from execution changes; inspect untracked files without staging.
Override the reviewer's commit-range defaults with this package. Report missing
attribution evidence honestly. Repair in-scope findings and rerun affected checks.

## Simple chat status

At meaningful changes, show the plan name, emoji, verified completed/total tasks,
current task, and a short localized state. In Italian use `IN CORSO`,
`IN VERIFICA`, `NON CONCLUSO`, `BLOCCATO`, or `CONCLUSO`. While final checks or
review are pending, use `IN VERIFICA`. When blocked or unfinished, name the
reason, remaining work, and next action. Use `CONCLUSO` only after all required
tasks, checks, and final review finish. Keep material warnings and evidence gaps
visible without a separate status store.
