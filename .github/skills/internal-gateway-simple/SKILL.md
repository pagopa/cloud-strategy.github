---
name: internal-gateway-simple
description: Use when a concrete repository-owned task needs skill-first quick routing, lightweight analysis, support-skill selection, execution, or focused validation without a retained plan or critical challenge.
---

# Internal Gateway Simple

Use this skill as the skill-first fast path for concrete repository-owned work.
It exists for runtimes where the user selects skills directly and does not want
to manually switch between Copilot wrapper agents for small or medium tasks.

This skill does not replace `internal-gateway-operational-flow`. It keeps simple
work light and escalates visibly when the task needs full `plan`, `review`, or
critical challenge ownership.

## When to use

- The requested outcome is already concrete enough to answer, edit, or validate.
- The user wants tactical support skills, but not a full retained plan.
- The task needs a short approach note before implementation.
- The work is local, low to medium risk, and has a focused validation path.
- The user asks for skill-first UX instead of selecting planning or delivery
  wrapper agents manually.

## When not to use

- Real ambiguity remains about ownership, target shape, rollout, governance, or
  validation. Use `internal-gateway-operational-flow` in `plan` mode.
- The primary request is pressure testing, pre-mortem analysis, hidden
  assumptions, or failure modes. Use `internal-gateway-critical-master`.
- The primary request is defect-first review of an existing artifact, diff, or
  validation result. Use `internal-gateway-operational-flow` in `review` mode.
- The work needs a retained numbered plan under `tmp/superpowers/`. Use
  `internal-writing-plans`.
- The task is catalog sync governance or consumer propagation. Use the repo-only
  sync owners.

## Simple Flow

1. Inspect local files first when repository evidence can answer the question.
2. Decide whether the target state is concrete enough for lightweight execution.
3. Select only the support skills needed for the domain or file type.
4. Give a brief approach note when it helps the user understand the execution.
5. Answer or implement without creating a retained plan.
6. Run focused validation, or name the explicit validation gap.
7. Escalate visibly if the work becomes planning, review, or critical challenge.

## Support-Skill Selection

Load support skills after the simple lane is confirmed.

Examples:

- Python scripts: use `internal-script-python`.
- Azure validation or evidence: use `internal-azure-operations`.
- Azure RBAC, Policy, identity, or guardrails: use `internal-azure-governance`.
- Terraform changes: use `internal-terraform`.
- GitHub Actions changes: use `internal-github-actions`.
- Markdown-only edits: use matching scoped Markdown instructions and the closest
  repository-owned owner, without forcing a full plan.

Do not load every plausible support skill. Load the smallest set that can
complete the task and validate the result.

## Escalation Rules

Move out of this skill when the simple lane stops being true:

- Move to `plan` when there are multiple credible paths with real tradeoffs.
- Move to `review` when correctness evidence or merge readiness becomes the main
  job.
- Move to `internal-gateway-critical-master` when the user asks to attack the
  reasoning or when a high-value pressure test is needed.
- Move to `internal-writing-plans` when the work must survive the current turn as
  a retained plan.

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

## Validation

- The target state was concrete enough for simple execution, or escalation was
  explicit.
- The selected support skills were minimal and relevant.
- No retained plan was created unless the task moved to `internal-writing-plans`.
- Focused validation was run or the validation gap was named.
- Any lane change included owner, scope, action, validation path, and risk.
