# Internal Gateway Operational Flow Usage Guide

This README explains how to use `internal-gateway-operational-flow` in practice.
`SKILL.md` remains the canonical contract. This file is an operator guide with
examples and expected results.

## Core Idea

Use this skill to choose one visible staged entry point, then run one active
phase at a time:

- `full-cycle`: plan, optional critical challenge, checkpointed delivery, and
  final evidence. The name alone does not skip the pre-execute checkpoint.
- `plan-only`: plan, Decision Brief, optional critical pass, and stop before
  apply.
- `apply-plan`: apply an approved retained plan through
  `internal-executing-plans`.
- `review`: inspect an existing artifact, diff, or validation result with
  findings first and the smallest review lens that fits the evidence.
- `mode-explicit`: honor a direct `plan`, `execute`, or `review` request.

Use `internal-gateway-critical-master` instead when the primary job is pressure
testing, pre-mortem analysis, hidden-assumption challenge, or reframing.

## How To Decide

Start with the smallest mode that can honestly finish the current phase:

| Question | If yes | Result |
| --- | --- | --- |
| Is the task concrete and only needs skill-first quick routing or support-skill selection? | Use `internal-gateway-simple-task`. | Lightweight analysis, minimal support skills, focused execution, and validation are returned. |
| Does the user want questions before any plan output? | Use `plan-only (clarify-first)`. | `grill-me` asks bulk questions with recommended answers before the plan is written. |
| Is the target state already clear and verifiable? | Use `mode-explicit` `execute`. | Files, commands, or guidance are delivered with validation evidence. |
| Does a concrete artifact or diff already exist and need defect-first or systems-level analysis? | Use `review`. | Findings, severity, evidence gaps, and fix routing are returned. |
| Is there an approved retained plan under `tmp/superpowers/` to apply? | Use `apply-plan`. | `internal-executing-plans` runs the `done-*` loop and ignores `dubbi-e-domande.md`. |
| Are ownership, shape, rollout, or tradeoffs still unresolved? | Use `plan-only` or `full-cycle`. | A decision frame, Decision Brief when retained, and next-step package are returned. |
| Is the main request to attack the reasoning before action? | Use `internal-gateway-critical-master`. | Weak assumptions and failure modes are challenged before reformulation. |

If two modes still fit, choose `plan` and state why the boundary is uncertain.

## Common Use Cases

| Use case | Example request | Mode and support | Expected result |
| --- | --- | --- | --- |
| Clear local implementation with analysis | "Create a Python script that lists public Azure Storage accounts." | `internal-gateway-simple-task` plus `internal-script-python`; add Azure support skills or current Microsoft docs only when needed. | Script or implementation approach, focused validation, and residual risk. No retained plan by default. |
| Simple advisory analysis before coding | "Tell me how you would build this script, then implement it." | `execute` if the target is concrete. Use a short tactical note, not full `plan` mode. | Brief approach, implementation, and checks. |
| Deterministic multi-file alignment | "Rename this approved skill reference across adjacent files and run the focused tests." | `execute`. File count alone does not force planning. | Updated files, stale-name search, and validation evidence. |
| New repository-owned workflow with unclear owner | "Should this be an agent, a skill, or an instruction?" | `plan` plus relevant authoring support skills. | Ownership decision, anti-scope, tradeoffs, next owner, and validation path. |
| Plan with user grilling before final plan | "Ask all grill-me questions first, then write the plan after my answers." | `plan` plus `grill-me` before final planning. | Numbered questions with recommended answers; after responses, a plan-ready decision frame. |
| Plan, then critical challenge | "Make a plan, then pressure-test it before implementation." | `full-cycle`, then visible critical phase through `internal-gateway-critical-master`. | Plan, Decision Brief when retained, strongest objections, explicit outcome, and checkpoint before delivery. |
| Apply retained plan | "Apply this plan under `tmp/superpowers/example`." | `apply-plan` plus `internal-executing-plans`. | Completed items move into `done-*`, active numbered files shrink or delete, and validation evidence is reported. |
| Review an existing result | "Review this diff for merge readiness." | `review` plus `internal-code-review`; add `internal-systems-review` when architecture, workflow, cross-cutting impact, or blind spots are in scope. | Findings first, severity, causal layer, evidence gaps, and fix routing. |
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

## Full Cycle With Grill And Critical

Use this sequence when the user wants the rigorous path:

1. Inspect repository evidence first.
2. Run `grill-me` as conditional support.
3. If the user asks for bulk questions, provide numbered questions with a
   recommended answer for each.
4. Wait for the user answers when the answers affect the plan.
5. Create the `plan` phase output.
6. If a retained plan is created or materially reformulated, provide a Decision
  Brief in chat.
7. Move visibly to `internal-gateway-critical-master` for pressure testing when
  reasoning risk remains.
8. Reformulate, de-escalate, execute, review, continue critical, or accept risk
  according to the critical outcome.
9. Move to `execute` or `apply-plan` only after the target state and validation
  path are clear and the checkpoint is satisfied or the user explicitly asked
  to apply or run the work end to end.

Expected result:

- Pre-plan questions expose preferences and constraints.
- The plan records assumptions, tradeoffs, selected direction, and anti-scope.
- The Decision Brief is a compact chat projection, not a second canonical plan.
- Critical challenge attacks the completed plan, not every small delivery step.
- The final next-step package names owner, scope, action, validation, and risk.

## Example Prompts

Use these prompts when you want a specific amount of process.

```text
Use internal-gateway-simple-task.
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
After that, use the explicit critical outcome before recommending execution.
```

```text
Apply the approved retained plan under tmp/superpowers/example.
Use internal-executing-plans for the done-* loop.
Do not execute dubbi-e-domande.md.
```

```text
Review this diff with review mode.
Use code review for code defects and systems review for cross-cutting impact.
Findings first, then evidence gaps, then route each fix to execute, plan,
critical challenge, or defer.
```

## Output And Support Calibration

Keep operational-flow responses compact unless evidence or user scope requires
detail. Plan and review outputs should usually stay within about 40 lines, and
execution reports should usually stay within about 30 lines.

Use imported support only after the gateway phase is selected. `grill-me`
supports planning questions. `mattpocock-caveman` is only a compression pass for
long sync, review, or governance reports after blockers, risks, and validation
evidence are explicit.

## Maintenance Notes

- Keep this README aligned with [SKILL.md](SKILL.md) and the reference files.
- Do not copy long workflow tables into Copilot wrapper agents.
- Update this README when mode boundaries, support-skill behavior, or wrapper
  projections change.
- Run Markdown and catalog validation after meaningful edits.
