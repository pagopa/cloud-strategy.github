# Scope Challenge

Use this gate before retaining or approving a non-trivial execution plan. It
keeps the plan executable by forcing target, anti-scope, owner, validator, and
stop conditions into the open.

## Source Pattern

- Comparative source: `tmp/external-comparison/gstack/plan-eng-review/SKILL.md`
  Step 0.
- Adopt the scope challenge idea only. Do not import the external runtime.

## Required Questions

Every retained plan must be able to answer these questions:

1. `target`: What is the smallest target state that satisfies the request?
2. `anti-scope`: What tempting work is explicitly outside this plan?
3. `owner`: Which repository owner owns the change and which neighboring owner
   should win if the lane changes?
4. `validator`: Which validator, test, review path, or explicit gap will prove
   the result?
5. `stop conditions`: What missing input, unsafe scope, ownership conflict, or
   validation failure must stop execution?
6. `reading budget`: What is the smallest first read and evidence pass that can classify the folder without broad context loading?
7. `observable acceptance`: Which diff, file state, validator assertion, manual check, or explicit non-action will prove each executable item?
8. `implementation contract`: For `extended` profiles, does `02-control.md` list the exact sources, target files, validation order, blockers, and any external pin or fallback? For `compact` profiles, a separate implementation contract is not required.
9. `profile`: Is `Plan profile` declared as `compact` or `extended`? Currently, no other profiles are supported. Missing or unrecognized profiles return `unsupported-plan-contract`.
10. `summary language`: Is `01-change-summary.md` written in Italian as a compressed decision capsule with required sections and a `Risorsa | Azione | Scopo` table for non-trivial plans?
11. `summary clarity`: Are changed resources and intended actions obvious in the summary without reading deeper files?
12. `summary counter-validation`: Does the summary contain enough observable criteria to let the user counter-validate the plan without reading the control file?
13. `route map`: Do `Source item ledger` routes point to existing numbered files or explicit non-action routes?
14. `questions state`: Is `questions.md` either `- none` (ready) or explicitly blocking execution handoff?
15. `token budget`: For `compact`, is total plan Markdown within 2,000 estimated tokens, with `01-change-summary.md` under 300 and `02-execution.md` under 1,500?

For non-trivial retained plans and strategic-to-operational or
monolithic-to-executable conversions, also answer this:

1. `coverage`: How does `02-execution.md` (`compact`) or `02-control.md`
   (`extended`) preserve every requested or source item before execution or
   before the source artifact is retired?

For `compact`, answer how `02-execution.md` preserves coverage with inline item
rows.

For retained plans with numbered files, confirm that `01-change-summary.md` is a
brief compressed decision summary only (Italian, non-executable), and that
`02-execution.md` (`compact`) or `02-control.md` (`extended`) exposes the same
target, anti-scope, owner, validator, and stop conditions. For `extended`,
confirm `02-control.md` also carries `Recommended use`, `Plan profile`,
`File map and role`, `Initial evidence pass`, `Reading budget`, source-item
coverage, and merged implementation-contract sections.

For retained plans that rewrite an existing strategic or review-only artifact,
confirm that the folder contains `02-execution.md` (`compact`) or
`02-control.md` (`extended`) as a clear traceability owner before the source
artifact is deleted, replaced, or compressed.

## Gate Result

Use one of these outcomes:

- `READY`: all required answers are concrete enough for execution.
- `NEEDS_REVISION`: one or more answers are missing or too vague.
- `BLOCKED`: a required decision, permission, or evidence source is missing.

For non-trivial retained plans, `READY` also requires explicit source-item
coverage and, for `extended` profiles, complete merged implementation-contract
sections in `02-control.md`.

## Output Template

```text
Scope Challenge: READY | NEEDS_REVISION | BLOCKED
Target: <smallest target state>
Anti-scope: <explicit exclusions>
Owner: <primary owner and lane-change owner>
Validator: <command, review path, or explicit gap>
Stop conditions: <what stops execution>
Profile: <compact or extended>
Summary language: <Italian with required sections and resource table, or missing>
Summary clarity: <resources and actions obvious, or unclear>
Summary counter-validation: <enough observable criteria for user counter-validation, or too generic>
Source-item ledger: <complete, incomplete, stale, or missing>
Reading budget: <first files or checks before broader reading>
Observable acceptance: <diff, file, validator, manual, explicit non-action, or blocker>
Implementation contract: <complete, not applicable (compact), missing (extended), or blocker>
Coverage: <ledger coverage, explicit not-applicable, or blocker>
```

Do not proceed to `apply-plan` when the result is `NEEDS_REVISION` or `BLOCKED`
unless the user explicitly accepts the risk.
