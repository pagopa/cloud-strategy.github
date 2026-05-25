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
8. `critical challenge`: For non-trivial or governance-sensitive retained plans, what did `internal-gateway-critical-master` challenge before plan files were written, and what outcome must the plan absorb?

For non-trivial retained plans and strategic-to-operational or
monolithic-to-executable conversions, also answer this:

1. `coverage`: How does `02-source-item-ledger.md` preserve every requested or
   source item before execution or before the source artifact is retired?

For retained plans with numbered files, confirm that `01-change-summary.md` is a
brief change summary only, and that `02-source-item-ledger.md` exposes the same
target, anti-scope, owner, validator, and stop conditions, plus `Uso consigliato`,
`Mappa file e ruolo`, `Evidence pass iniziale`, `Budget lettura`, and source-item
coverage.

For retained plans that rewrite an existing strategic or review-only artifact,
confirm that the folder contains `02-source-item-ledger.md` or an equivalently
clear traceability owner before the source artifact is deleted, replaced, or
compressed.

## Gate Result

Use one of these outcomes:

- `READY`: all required answers are concrete enough for execution.
- `NEEDS_REVISION`: one or more answers are missing or too vague.
- `BLOCKED`: a required decision, permission, or evidence source is missing.

For non-trivial retained plans, `READY` also requires explicit source-item
coverage in the ledger and a recorded critical challenge outcome or explicit
not-applicable reason.

## Output Template

```text
Scope Challenge: READY | NEEDS_REVISION | BLOCKED
Target: <smallest target state>
Anti-scope: <explicit exclusions>
Owner: <primary owner and lane-change owner>
Validator: <command, review path, or explicit gap>
Stop conditions: <what stops execution>
Summary file: <brief change summary only, overloaded, or missing>
Source-item ledger: <complete, incomplete, stale, or missing>
Reading budget: <first files or checks before broader reading>
Observable acceptance: <diff, file, validator, manual, explicit non-action, or blocker>
Critical challenge: <outcome, absorbed change, not-applicable, or blocker>
Coverage: <ledger coverage, explicit not-applicable, or blocker>
```

Do not proceed to `apply-plan` when the result is `NEEDS_REVISION` or `BLOCKED`
unless the user explicitly accepts the risk.
