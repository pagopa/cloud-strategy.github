---
name: internal-define-advisor
description: Use when a repository-owned request needs pre-action advice before choosing a tool, skill, agent, workflow, owner, or simple-task execution path.
---

# Internal Define Advisor

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.

- `grill-me`: mandatory proportional interview pattern for unresolved Gate 0 decisions.
- `idea-refine`: optional divergent and convergent support when several credible directions or hidden assumptions remain.
- `internal-gateway-operational-flow`: owning gateway for define state, Gate 0 status, and phase transitions.
- `internal-gateway-simple-task`: recommended next owner when the request is concrete enough to answer, edit, diagnose, or validate directly.
- `internal-agent-support-next-step`: handoff package for next owner, scope, action, validation, and risk.
- `internal-skill-creator`: next owner when the approved action is creating or materially revising a repository-owned skill.

Use this skill as the pre-action advisory brain inside `define`. It decides what should happen next before tool use, planning, asset creation, review, or execution.

## When to use

- The user asks whether to use a tool, skill, agent, prompt, instruction, validator, workflow, or retained plan.
- The user asks to compare skills, agents, owners, or workflow options before acting.
- The user asks whether creating a new agent or skill is justified.
- The request may be overkill, under-specified, or better handled by `internal-gateway-simple-task`.
- The user wants to understand first and act later.

## When not to use

- The target state and validation path are already concrete; recommend `internal-gateway-simple-task`.
- The user asks for direct `execute`, `apply-plan`, defect-first `review`, or critical challenge only.
- A retained plan folder is already approved for execution.
- The request is source-side sync governance, consumer propagation, or broad catalog refresh.

## Advisory Flow

1. Run the smallest evidence pass needed to identify target, candidate owner, nearby validation, and anti-scope.
2. Use `grill-me` as the mandatory question format when user-only decisions can change scope, owner, target state, validation, rollout, or anti-scope.
3. Classify the advisory question as tool-fit, skill-fit, skill comparison, agent decision, owner placement, overkill check, or simple-task candidate.
4. Use `idea-refine` only when several credible directions remain or hidden assumptions need divergent and convergent exploration.
5. Prefer `internal-gateway-simple-task` when the work is concrete, low-to-medium risk, and can be completed through one quick lane.
6. Emit a `Gate 0 Advisory Packet`.
7. Stop at a checkpoint unless the user explicitly approves the next visible owner.

## Gate 0 Advisory Packet

Every response that closes this skill should include:

- `Intent`: what the user is trying to decide.
- `Recovered evidence`: files, repository facts, or source facts used.
- `Open decisions`: user-only decisions or `none`.
- `Recommended default`: the default answer and why.
- `Alternatives considered`: realistic alternatives and why they lose or remain viable.
- `Use idea-refine`: `yes` or `no`, with reason.
- `Simple-task candidate`: `yes` or `no`, with reason.
- `Best next owner`: next skill, agent, tool, or `none`.
- `Anti-scope`: what must not happen yet.
- `Validation path or gap`: command, review path, or explicit gap.
- `Stop condition`: where the agent must pause.
- `Checkpoint question`: the exact approval or decision needed from the user.

## Guardrails

- Do not run `graphify`, create a skill, create an agent, write a retained plan, modify files, or transition phases by implication.
- Do not replace `internal-gateway-operational-flow`; this skill advises inside `define`.
- Do not use `idea-refine` as mandatory support for simple tool-fit or deterministic maintenance decisions.
- Do not hide dispatch. Recommend the next owner visibly and wait for the user's checkpoint when action would begin.
- If the best next step is direct completion and risk is low, recommend `internal-gateway-simple-task` with target, action, validation, and risk.

## Validation

- The answer explains whether the task should stay advisory, move to simple-task, move to plan, move to execute, or stop.
- `grill-me` was used proportionally for decisions that repository evidence could not recover.
- `idea-refine` was used only when option exploration actually mattered.
- The output names the next owner without applying it silently.
- The packet includes anti-scope, validation path or gap, stop condition, and checkpoint question.
