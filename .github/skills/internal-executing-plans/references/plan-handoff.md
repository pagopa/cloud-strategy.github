# Plan Handoff

Use this reference when `internal-executing-plans` receives a retained plan or
Decision Brief from planning. It defines the minimum input contract before the
`done-*` loop starts.

## Source Pattern

- Comparative source: `tmp/external-comparison/compound-engineering-plugin/plugins/compound-engineering/skills/ce-plan/references/plan-handoff.md`.
- Adopt the handoff checks only. Do not import Compound runtime behavior.

## Required Inputs

- Plan folder under `tmp/superpowers/<clear-action-or-task-name>/`.
- `01-riassunto-direzione-e-decisione.md` with `Uso consigliato` and `Mappa file e ruolo`.
- `Evidence pass iniziale` and `Budget lettura` in the summary control file.
- Numbered executable plan files after the summary control file.
- A plan for closing the summary control file through a matching `done-*` marker when the folder completes.
- Confirmed target state and anti-scope.
- Selected owner and known lane-change owner.
- Validation path or explicit validation gap.
- Observable acceptance for each executable action, especially broad verbs such
   as compress, rewrite, refactor, harden, align, or simplify.
- Stop conditions.

## Before Starting

1. Read `01-riassunto-direzione-e-decisione.md` first and use it to classify folder purpose, next expected treatment, file roles, and reading budget.
2. Run the declared `Evidence pass iniziale` before broad reading. Use `rg --no-ignore` for retained artifacts under `tmp/` when checking plan claims.
3. Read `dubbi-e-domande.md` for accepted decisions, then exclude it from the
   executable loop.
4. Read numbered plan files in order after the summary control file.
5. Check whether a Decision Brief exists in chat, a prompt, or a retained plan
   artifact.
6. If a required input is missing, inspect repository evidence before asking.
7. If the missing input cannot be recovered, stop with a visible gap instead of
   guessing.

## Standard Stop Conditions

- Scope moves outside the declared files, owners, or asset family.
- The summary control file, `Uso consigliato`, or `Mappa file e ruolo` is missing from a non-trivial retained plan.
- `Evidence pass iniziale` or `Budget lettura` is missing from a non-trivial retained plan.
- Owner is missing or the active owner no longer fits.
- Validation path is absent and no closest check exists.
- A promotion-gated contract would be violated.
- A cited evidence path cannot be read.

When a stop condition fires, package the next step through
`internal-agent-support-next-step` or lane-change through
`internal-agent-support-lane-change-engine`.
