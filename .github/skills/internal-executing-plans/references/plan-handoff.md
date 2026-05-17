# Plan Handoff

Use this reference when `internal-executing-plans` receives a retained plan or
Decision Brief from planning. It defines the minimum input contract before the
`done-*` loop starts.

## Source Pattern

- Comparative source: `tmp/external-comparison/compound-engineering-plugin/plugins/compound-engineering/skills/ce-plan/references/plan-handoff.md`.
- Adopt the handoff checks only. Do not import Compound runtime behavior.

## Required Inputs

- Plan folder under `tmp/superpowers/<clear-action-or-task-name>/`.
- Numbered executable plan files.
- Confirmed target state and anti-scope.
- Selected owner and known lane-change owner.
- Validation path or explicit validation gap.
- Stop conditions.

## Before Starting

1. Read `dubbi-e-domande.md` for accepted decisions, then exclude it from the
   executable loop.
2. Read numbered plan files in order.
3. Check whether a Decision Brief exists in chat, a prompt, or a retained plan
   artifact.
4. If a required input is missing, inspect repository evidence before asking.
5. If the missing input cannot be recovered, stop with a visible gap instead of
   guessing.

## Standard Stop Conditions

- Scope moves outside the declared files, owners, or asset family.
- Owner is missing or the active owner no longer fits.
- Validation path is absent and no closest check exists.
- A promotion-gated contract would be violated.
- A cited evidence path cannot be read.

When a stop condition fires, package the next step through
`internal-agent-support-next-step` or lane-change through
`internal-agent-support-lane-change-engine`.
