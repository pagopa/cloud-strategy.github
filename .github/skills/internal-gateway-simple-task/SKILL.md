---
name: internal-gateway-simple-task
description: Use when a concrete low-to-medium-risk repository-owned coding or non-coding task can be answered, edited, diagnosed, or validated quickly without a retained plan, review mode, critical challenge, or staged workflow.
---

# Internal Gateway Simple Task

Use this skill as the skill-first fast path for concrete repository-owned work.
It exists for runtimes where the user selects skills directly and does not want
to manually switch between Copilot wrapper agents for small or medium tasks.

This skill does not replace `internal-gateway-operational-flow`. It keeps simple
work light and escalates visibly when the task needs full `plan`, `review`, or
critical challenge ownership.

## When to use

- The requested outcome is already concrete enough to answer, edit, or validate.
- The task is coding or non-coding work with a known target file, artifact,
  command, question, or validation path.
- The user wants tactical support skills, but not a full retained plan or staged full-cycle workflow.
- The task needs a short approach note before implementation.
- The work is local, low to medium risk, and has a focused validation path.
- The user asks for skill-first UX instead of selecting planning or delivery
  wrapper agents manually.
- `internal-gateway-operational-flow` or `internal-gateway-critical-master`
  de-escalates because the remaining work is concrete and low risk.

## When not to use

- Real ambiguity remains about ownership, target shape, rollout, governance, or
  validation. Use `internal-gateway-operational-flow` with the `plan-only` or
  `full-cycle` entry point.
- The primary request is pressure testing, pre-mortem analysis, hidden
  assumptions, or failure modes. Use `internal-gateway-critical-master`.
- The primary request is defect-first review of an existing artifact, diff, or
  validation result. Use the `review` entry point in
  `internal-gateway-operational-flow`.
- The main need is architecture, workflow, cross-cutting impact, or merge-risk
  evidence. Use `internal-systems-review` through review mode.
- The main need is line-level code defects, regressions, tests, or language
  anti-patterns. Use `internal-code-review` through review mode.
- The work needs a retained numbered plan under `tmp/superpowers/`. Use
  `internal-writing-plans`.
- The task is catalog sync governance or consumer propagation. Use the repo-only
  sync owners.

## Protected Trigger

Use this lane only when the task can be completed without settling a new
operating model, ownership boundary, rollout path, or critical assumption. If a
selected staged workflow reveals that the remaining work is just a clear edit,
focused answer, or deterministic validation, de-escalate here visibly instead of
continuing the heavier flow.

## Simple Flow

1. Inspect local files first when repository evidence can answer the question.
2. Decide whether the target state is concrete enough for lightweight execution.
3. Pick one quick lane: answer, edit, diagnose, validate, or escalate.
4. Give a brief approach note when it helps the user understand the execution.
5. Discover only the support skills needed for the domain, file type, symptom,
   or validation path.
6. Answer, implement, diagnose, or validate without creating a retained plan.
7. Run focused validation, or name the explicit validation gap.
8. Escalate visibly if the work becomes planning, review, or critical challenge.

## Quick Lanes

Use the smallest lane that can honestly finish the request:

- `answer`: explain or decide from repository evidence without editing files.
- `edit`: make a clear local change and run the closest focused validation.
- `diagnose`: reproduce a bug, failing test, build failure, validator drift, or
  unexpected behavior before fixing it.
- `validate`: run or design the focused check for an already concrete artifact.
- `escalate`: stop when the request becomes planning, review, retained-plan
  execution, or critical challenge.

Read `references/simple-lanes.md` when the prompt is simple but the right quick
lane or output shape is unclear.

## Support-Skill Discovery

Load support skills after the simple lane is confirmed.

Examples:

- Python scripts: use `internal-script-python`.
- Executable behavior with a meaningful test seam: use `internal-tdd` only when
  test-first delivery is requested or clearly valuable.
- Bug, test failure, build failure, validator drift, sync failure, or unexpected
  behavior: use `internal-debugging`.
- Azure validation or evidence: use `internal-azure-operations`.
- Azure RBAC, Policy, identity, or guardrails: use `internal-azure-governance`.
- Terraform changes: use `internal-terraform`.
- GitHub Actions changes: use `internal-github-actions`.
- Systems-level review evidence: use `internal-systems-review` through review
  mode, not imported zoom-out support.
- Code defect review evidence: use `internal-code-review` through review mode.
- Markdown-only edits: use matching scoped Markdown instructions and the closest
  repository-owned owner, without forcing a full plan.

Search or inspect nearby files first when the right support skill is not obvious
from the prompt. Prefer one targeted support skill over a broad bundle. Add a
second support skill only when the file type, runtime, or validation path proves
it is needed.

Do not load every plausible support skill. Load the smallest set that can
complete the task and validate the result.

Read `references/support-routing.md` when selecting among debugging, TDD,
review, systems review, worktree isolation, performance, or domain support.

Use `scripts/suggest_support_skills.py` only as an advisory helper when several
target paths or symptoms make support-skill selection noisy. Inspect repository
evidence and matching scoped instructions before acting on the suggestion.

## Escalation Rules

Move out of this skill when the simple lane stops being true:

- Move to `plan` when there are multiple credible paths with real tradeoffs.
- Move to `review` when correctness evidence or merge readiness becomes the main
  job.
- Move to `internal-gateway-critical-master` when the user asks to attack the
  reasoning or when a high-value pressure test is needed.
- Move to `internal-writing-plans` when the work must survive the current turn as
  a retained plan.
- Move back to `internal-gateway-operational-flow` when a task that looked
  simple becomes staged, cross-boundary, or apply-plan owned.

When escalating, state the boundary break and provide the next owner, scope,
action, validation path, and main risk.

## Output Shape

For simple execution, return:

- selected lane and support skills
- brief approach, only when useful
- files changed or answer delivered
- validation run or validation gap
- residual risk, if any

For escalation, return:

- why the simple lane no longer fits
- recommended next owner
- scope to carry forward
- next action
- validation path
- risk note

## Common Mistakes

| Mistake | Instead |
| --- | --- |
| Treating every analysis request as full `plan` mode | Use lightweight execution when the target is concrete. |
| Loading broad support-skill sets up front | Load only the support skills needed for the current task. |
| Creating retained plans for clear local work | Keep simple work in chat and validate directly. |
| Continuing after ownership or rollout ambiguity appears | Stop and move visibly to `plan`. |
| Running critical challenge by default | Use it only when the user asks or when reasoning risk is high. |
| Reopening settled decisions during implementation | Execute the known target state and stop if it breaks. |
| Using simple for an approved retained plan | Use `apply-plan` through `internal-gateway-operational-flow` and `internal-executing-plans`. |
| Treating de-escalation as hidden dispatch | State the boundary break and next owner before acting. |
| Using imported zoom-out support for broad review | Use `internal-systems-review` or `internal-code-review` through review mode. |

## Misuse Tests

- Concrete local edit with obvious validation should stay here and avoid a
  retained plan.
- Ambiguous agent, skill, or instruction ownership should move to
  `internal-gateway-operational-flow`.
- A completed diff that needs merge-readiness findings should move to `review`.
- A retained plan under `tmp/superpowers/` should move to `apply-plan`.
- A critical pass whose outcome is `de-escalate-to-simple` should name the
  simple scope, validation, and residual risk before continuing.

## Validation

- The target state was concrete enough for simple execution, or escalation was
  explicit.
- The selected support skills were minimal and relevant.
- No retained plan was created unless the task moved to `internal-writing-plans`.
- Focused validation was run or the validation gap was named.
- Any lane change included owner, scope, action, validation path, and risk.
- Misuse pressure cases still route to the heavier staged, review, retained-plan,
  or critical owner when simple work is not the smallest correct lane.
