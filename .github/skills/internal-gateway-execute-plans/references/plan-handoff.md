# Plan Handoff

Use this reference when `internal-gateway-execute-plans` receives a retained
plan or Decision Brief from planning. It defines the minimum input contract
before the `done-*` loop starts.

## Source Pattern

- Comparative source: `tmp/external-comparison/compound-engineering-plugin/plugins/compound-engineering/skills/ce-plan/references/plan-handoff.md`.
- Adopt the handoff checks only. Do not import Compound runtime behavior.

## Required Inputs

- Plan folder under `tmp/superpowers/<clear-action-or-task-name>/`.
- `Plan profile` declared as `compact` or `extended` in `02-execution.md`
  (`compact`) or `02-control.md` (`extended`).
  Unsupported or missing profiles return `unsupported-plan-contract`.
- `01-change-summary.md`: compressed Italian decision capsule with required
  sections and a `Risorsa | Azione | Scopo` table for non-trivial plans.
  Non-executable.
- `02-execution.md` (`compact`) with merged control header and executable steps.
- `02-control.md` (`extended`) with `Recommended use`, `File map and role`,
  `Initial evidence pass`, `Reading budget`, source-item coverage, and merged
  implementation-contract sections.
- Execution strategy is inferred by `internal-gateway-execute-plans` from the
  declared profile, folder shape, and validation path; do not require a
  separate consumer field in the retained plan.
- Numbered executable plan files after the summary and control files.
- A plan for closing the summary and ledger files through matching `done-*`
  markers when the folder completes as `DONE`.
- Confirmed target state and anti-scope.
- Selected owner and known lane-change owner.
- Validation path or explicit validation gap.
- Observable acceptance for each executable action, especially broad verbs such
   as compress, rewrite, refactor, harden, align, or simplify.
- A stable ledger row for every requested or source item, with status and route.
- Stop conditions.

## Before Starting

1. Read `01-change-summary.md` first for human decision context, then read
  `02-execution.md` (`compact`) or `02-control.md` (`extended`) to classify
  folder purpose, next expected treatment, file roles, reading budget, and
  source-item coverage.
2. Run the declared `Initial evidence pass` before broad reading. Use `rg --no-ignore` for retained artifacts under `tmp/` when checking plan claims.
3. For `compact`, `02-execution.md` is the only executable file after the
  summary. For `extended`, read numbered executable plan files in order after
  `02-control.md`.
4. Check whether a Decision Brief exists in chat, a prompt, or a retained plan
   artifact.
5. If a required input is missing, inspect repository evidence before asking.
6. If the missing input cannot be recovered, stop with a visible gap instead of
   guessing.

## Standard Stop Conditions

- `Plan profile` is missing, unsupported, or cannot be classified as `compact`
  or `extended`. Return `unsupported-plan-contract`.
- `compact` plans do not use the `tmp/superpowers/mini-plan-*` folder convention.
- `compact` plans include additional executable numbered files beyond
  `02-execution.md` without escalating to `extended`.
- Scope moves outside the declared files, owners, or asset family.
- `01-change-summary.md` is missing, overloaded with control details, written in
  English, or missing the required decision-capsule sections or
  `Risorsa | Azione | Scopo` table for non-trivial plans.
- `02-control.md`, `Recommended use`, or `File map and role` is missing from an
  `extended` retained plan.
- `Initial evidence pass`, `Reading budget`, or source-item coverage is missing
  from a non-trivial retained plan (`02-execution.md` for `compact`,
  `02-control.md` for `extended`).
- Merged implementation-contract sections in `02-control.md` are missing, stale,
  or too weak to recover exact sources, target files, validators, blockers, or
  required external pins for a non-trivial or lower-context retained plan.
- Owner is missing or the active owner no longer fits.
- Validation path is absent and no closest check exists.
- A promotion-gated contract would be violated.
- A cited evidence path cannot be read.

When a stop condition fires, package the next step through
`internal-agent-support-next-step` or lane-change through
`internal-agent-support-lane-change-engine`.
