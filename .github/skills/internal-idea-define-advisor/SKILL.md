---
name: internal-idea-define-advisor
description: Use when a repository-owned request has pre-action uncertainty about owner, workflow, AI asset, tool, validation, anti-scope, overkill, or simple-task fit.
---

# Internal Idea Define Advisor

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.

- `grill-me`: mandatory proportional interview pattern for unresolved Gate 0 decisions.
- `idea-refine`: optional option-exploration support when several credible directions remain after the minimum evidence pass.
- `internal-gateway-simple-task`: candidate next owner when one quick concrete lane can answer, edit, diagnose, or validate directly.

Use this skill as a simple pre-action advisor.
It helps recover the smallest safe next move before planning or execution.
It stays lightweight and does not own phase transitions, hidden dispatch, or file edits.

## When to use

- The user asks which owner, workflow, tool, skill, prompt, instruction, or validator should be used before action starts.
- The user asks to compare owners, skills, agents, workflows, or AI assets before choosing a direction.
- The request has pre-action uncertainty about validation, anti-scope, rollout fit, or whether the work is overkill.
- The request may collapse to `internal-gateway-simple-task`, but that fit still needs to be proven.

## When not to use

- The target state, scope, owner, and validation path are already concrete enough to act; recommend `internal-gateway-simple-task` or the already-selected path.
- The user explicitly asks for `execute`, `apply-plan`, defect-first `review`, or critical challenge and the lane is already settled.
- A retained plan folder is already approved for execution.
- The request is catalog governance, consumer propagation, or broad sync maintenance rather than a pre-action fit decision.

## Read On Demand

- Read `references/advisory-owner-map.md` when several candidate owners, relationship labels, or stop conditions compete.
- Read `references/advisory-question-bank.md` when `grill-me` needs proportionate question coverage for user-only decisions.
- Keep references as the deep owner for maps and question prompts. Do not copy them back into this file.

## Advisory Contract

1. Run the smallest evidence pass that can recover target, candidate owner, nearby validation, and anti-scope.
2. Classify the question before recommending action: owner fit, workflow fit, AI asset fit, tool or validator fit, overkill check, or simple-task fit.
3. Use `grill-me` only when unresolved user-only decisions can still change scope, owner, target state, validation, rollout, or anti-scope.
4. Use `idea-refine` only when the decision is genuinely exploratory rather than deterministic maintenance. See `references/advisory-owner-map.md` for `idea-refine` activation rules.
5. Recommend the next visible path or `none`. Keep the recommendation advisory; do not apply it silently.
6. Stop at a checkpoint unless the user explicitly approves the next visible owner.
7. Do not define surrounding workflow rules here. Keep flow-specific handling outside this bundle.
8. If the best next step is direct completion and risk is low, recommend `internal-gateway-simple-task` with target, action, validation, and risk.

## Gate 0 Advisory Packet

Every response that closes this skill should include:

- `Intent`: what the user is trying to decide.
- `Recovered evidence`: files, repository facts, or source facts used.
- `Open decisions`: user-only decisions or `none`.
- `Recommended default`: the default answer and why.
- `Alternatives considered`: realistic alternatives and why they lose or remain viable.
- `Recommended next path`: next skill, tool, workflow, or `none`. Sub-fields: `Use idea-refine` (`yes`/`no`, with reason), `Simple-task candidate` (`yes`/`no`, with reason).
- `Anti-scope`: what must not happen yet.
- `Validation path or gap`: command, review path, or explicit gap.
- `Stop & checkpoint`: where the agent must pause and the exact approval or decision needed from the user.

## Validation

- The answer explains whether the task should stay advisory, move to simple-task, move to plan, move to execute, or stop.
- `grill-me` was used proportionally for decisions that repository evidence could not recover.
- `idea-refine` was used only when option exploration actually mattered, and the fallback stayed with `grill-me` when it did not.
- The output names the next path without applying it silently.
- The packet includes anti-scope, validation path or gap, stop condition, and checkpoint question.
- Deep owner maps and question coverage live in local references instead of being duplicated inline.
