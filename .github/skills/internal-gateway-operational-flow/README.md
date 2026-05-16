# Internal Gateway Operational Flow Usage Guide

This README explains how to use `internal-gateway-operational-flow` in practice.
`SKILL.md` remains the canonical contract. This file is an operator guide with
examples and expected results.

## Core Idea

Use this skill to choose and run one visible operational mode for the current
phase:

- `plan`: settle ambiguity, ownership, tradeoffs, rollout, or validation before
  delivery.
- `execute`: apply a clear local change or deterministic task with concrete
  validation.
- `review`: inspect an existing artifact, diff, or validation result with
  findings first.

Use `internal-gateway-critical-master` instead when the primary job is pressure
testing, pre-mortem analysis, hidden-assumption challenge, or reframing.

## How To Decide

Start with the smallest mode that can honestly finish the current phase:

| Question | If yes | Result |
| --- | --- | --- |
| Is the task concrete and only needs skill-first quick routing or support-skill selection? | Use `internal-gateway-simple`. | Lightweight analysis, minimal support skills, focused execution, and validation are returned. |
| Is the target state already clear and verifiable? | Use `execute`. | Files, commands, or guidance are delivered with validation evidence. |
| Does a concrete artifact or diff already exist and need defect-first analysis? | Use `review`. | Findings, severity, evidence gaps, and fix routing are returned. |
| Are ownership, shape, rollout, or tradeoffs still unresolved? | Use `plan`. | A decision frame and next-step package are returned. |
| Is the main request to attack the reasoning before action? | Use `internal-gateway-critical-master`. | Weak assumptions and failure modes are challenged before reformulation. |

If two modes still fit, choose `plan` and state why the boundary is uncertain.

## Common Use Cases

| Use case | Example request | Mode and support | Expected result |
| --- | --- | --- | --- |
| Clear local implementation with analysis | "Create a Python script that lists public Azure Storage accounts." | `internal-gateway-simple` plus `internal-script-python`; add Azure support skills or current Microsoft docs only when needed. | Script or implementation approach, focused validation, and residual risk. No retained plan by default. |
| Simple advisory analysis before coding | "Tell me how you would build this script, then implement it." | `execute` if the target is concrete. Use a short tactical note, not full `plan` mode. | Brief approach, implementation, and checks. |
| Deterministic multi-file alignment | "Rename this approved skill reference across adjacent files and run the focused tests." | `execute`. File count alone does not force planning. | Updated files, stale-name search, and validation evidence. |
| New repository-owned workflow with unclear owner | "Should this be an agent, a skill, or an instruction?" | `plan` plus relevant authoring support skills. | Ownership decision, anti-scope, tradeoffs, next owner, and validation path. |
| Plan with user grilling before final plan | "Ask all grill-me questions first, then write the plan after my answers." | `plan` plus `mattpocock-grill-me` before final planning. | Numbered questions with recommended answers; after responses, a plan-ready decision frame. |
| Plan, then critical challenge | "Make a plan, then pressure-test it before implementation." | `plan`, then visible next step to `internal-gateway-critical-master`, then back to `plan` if reformulation is needed. | Plan, strongest objections, reformulated plan or explicit residual risk. |
| Review an existing result | "Review this diff for merge readiness." | `review` plus `internal-code-review`. | Findings first, severity, causal layer, evidence gaps, and fix routing. |
| Pure challenge | "Attack this proposal before we trust it." | `internal-gateway-critical-master`, not this skill as the primary owner. | Failure modes, hidden assumptions, and a recommendation for reformulation. |
| Runtime without Copilot agent UI | "Use the operational flow directly in Codex." | Load this skill and references manually. | Text next-step packages replace Copilot handoff buttons. |

## Lightweight Execute Pattern

Use this pattern when the task needs tactical analysis or support skills but not
a full planning phase.

1. Inspect the repository or target files if local facts can answer the question.
2. Confirm the target state is concrete enough to deliver.
3. Select `execute`.
4. Load only the tactical support skills needed for the domain.
5. Give a short approach note only if it helps the implementation.
6. Implement or answer.
7. Run focused validation or name the explicit validation gap.

Good fit:

```text
Create a Python script that lists public Azure Storage accounts.
Use Python script guidance and Azure operational context.
Do not create a retained plan unless you find an ownership or rollout decision.
```

Expected result:

- The assistant may inspect existing script layout and Python rules.
- The assistant uses `internal-script-python` for script shape.
- The assistant may use Azure operations or governance depth for service
  semantics.
- The assistant delivers code or a concrete implementation path.
- The assistant does not invoke critical challenge unless the user asks or a
  serious hidden risk appears.

This is analysis-assisted execution, not `plan` mode.

## Full Plan With Grill And Critical

Use this sequence when the user wants the rigorous path:

1. Inspect repository evidence first.
2. Run `mattpocock-grill-me` as conditional support.
3. If the user asks for bulk questions, provide numbered questions with a
   recommended answer for each.
4. Wait for the user answers when the answers affect the plan.
5. Create the `plan` mode output.
6. Move visibly to `internal-gateway-critical-master` for pressure testing.
7. Reformulate the plan if the challenge changes the direction.
8. Move to `execute` only after the target state and validation path are clear.

Expected result:

- Pre-plan questions expose preferences and constraints.
- The plan records assumptions, tradeoffs, selected direction, and anti-scope.
- Critical challenge attacks the completed plan, not every small delivery step.
- The final next-step package names owner, scope, action, validation, and risk.

## Example Prompts

Use these prompts when you want a specific amount of process.

```text
Use internal-gateway-simple.
Load the relevant Python and Azure support skills.
Give only the short approach needed to implement and validate the script.
```

```text
Use plan mode.
Before writing the plan, use grill-me in bulk:
give numbered questions and your recommended answer for each.
Wait for my answers before finalizing the plan.
```

```text
Create the plan first.
Then use internal-gateway-critical-master to pressure-test the plan.
After that, reformulate the plan before recommending execution.
```

```text
Review this diff with review mode.
Findings first, then evidence gaps, then route each fix to execute, plan,
critical challenge, or defer.
```

## Maintenance Notes

- Keep this README aligned with [SKILL.md](SKILL.md) and the reference files.
- Do not copy long workflow tables into Copilot wrapper agents.
- Update this README when mode boundaries, support-skill behavior, or wrapper
  projections change.
- Run Markdown and catalog validation after meaningful edits.
