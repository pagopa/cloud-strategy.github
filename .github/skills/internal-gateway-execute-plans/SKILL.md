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

Route an unclear idea to `/internal-gateway-idea` and a missing or unapproved
plan to `/internal-gateway-writing-plans`. Do not execute a legacy plan that
contains `## Execution Manifest`; preserve it read-only and route an explicit
re-authoring request to the writer. This legacy clause applies to that manifest
only. Historical run files and runtime records remain read-only and are never
auto-resumed or migrated; residual work requires current source and new
approval. A normal resume of a current approved task remains allowed under this
contract, but never a custom old runtime.

## Approval and task contract

Select the explicit path or active plan. Ask which plan only when selection is
ambiguous; never choose the latest file merely by timestamp. The user's
invocation is approval of every declared task unless they limited the subset.
Do not ask for another plan approval or confirmation after each task. A writer
result, readiness flag, or internal skill call is not a user invocation.
Invocation means an explicit mention of this skill (`$` in Codex, `/` in
Copilot); a natural-language request such as "procedi" is not plan approval.

Verify source coherence and consume the plan's stable task IDs, criteria,
dependencies, checks, writable paths, and explicitly selected human gates.
Unresolved references block start. A material change to those contracts or the
source needs reevaluation and reapproval, not reconstruction from the spec.
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
If `/mattpocock-implement` is not loaded, stop before the first write and ask
the user to mention it explicitly.

Execute in dependency order. After each task, run its checks and record progress;
count it complete only after required verification passes. Run automatic
checkpoints and continue without asking permission. Repair safe in-scope failures
and rerun checks. Stop on genuine missing decisions, source/contract drift,
unsafe actions, conflicts, out-of-scope changes, or an explicit user gate. A
required failed or unavailable check is never silently waived.

## Review without commits

Before the first write, capture the current HEAD identity and initial state of
authorized files, including existing untracked files, types, modes and absence.
When they already contain user edits, preserve a targeted baseline snapshot
under `tmp/.plans/.baselines/<plan-id>/`. This is disposable support, not a
second plan, ledger, or approval gate. Preserve the same baseline on an ordinary
resume; if unavailable, report the attribution gap rather than inventing it.

For one final review, compare actual start and end state of the authorized
files, including new untracked files, deletions, and both rename endpoints.
Distinguish preexisting edits from this execution's changes; include the final
code and stable requirements as context. `git diff <initial-HEAD> --` covers
tracked changes only; inspect untracked paths separately without staging them.
For dirty authorized files use the captured file state, not a subtraction of
two patch texts. Do not follow symlinks outside authority or copy secrets into
baseline artifacts; keep those read-only unless a safe review path is authorized.

Supply that review scope, diff evidence, and the plan/source to
`/mattpocock-code-review`. Its commit-range defaults and missing-reference
questions are overridden by this execution package. A `main` comparison is
optional on request and covers broader branch work; `main...HEAD` alone cannot
review uncommitted work. Do not fetch, stage or commit to manufacture a baseline.
Repair in-scope findings and recheck their affected behavior before closing.

## Simple chat status

At meaningful state changes, show the plan name and a short localized global
state with an emoji, verified completed/total tasks, and the current task.
Use `IN CORSO`, `IN VERIFICA`, `NON CONCLUSO`, `BLOCCATO`, or `CONCLUSO` in
Italian chat, translating labels for other languages. Keep updates to a few
lines, not one message per command. Do not create a separate status store.

```text
🟡 PIANO IN CORSO · <plan> · 2/5 task completati
🔧 Task 3 · Implementazione

⛔ PIANO BLOCCATO · <plan> · 4/5 task completati
📌 Motivo: <concrete blocker>; resta <remaining work>.
➡️ Per ripartire: <necessary action or decision>.

✅ PIANO CONCLUSO · <plan> · 5/5 task completati
🔎 Verifiche e review finale completate.
```

Use `IN VERIFICA` while final checks/review are pending. If stopping incomplete,
use `NON CONCLUSO` or `BLOCCATO` with the reason, remaining work, and next action.
Never label completion while a required check, dependency, review, or user gate
is unresolved. Preserve material warnings and evidence gaps even in short output.
