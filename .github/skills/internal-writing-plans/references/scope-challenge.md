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

For strategic-to-operational or monolithic-to-executable conversions, also answer this:

7. `coverage`: Which traceability matrix or equivalent owner preserves every source item before the source artifact is retired?

For retained plans with numbered files, confirm that `01-riassunto-direzione-e-decisione.md` exposes the same target, anti-scope, owner, validator, and stop conditions, plus `Uso consigliato`, `Mappa file e ruolo`, `Evidence pass iniziale`, and `Budget lettura`.

For retained plans that rewrite an existing strategic or review-only artifact, confirm that the folder contains `02-matrice-operativa.md` or an equivalently clear traceability owner before the source artifact is deleted, replaced, or compressed.

## Gate Result

Use one of these outcomes:

- `READY`: all five answers are concrete enough for execution.
- `NEEDS_REVISION`: one or more answers are missing or too vague.
- `BLOCKED`: a required decision, permission, or evidence source is missing.

For strategic-to-operational conversions, `READY` also requires explicit source-item coverage.

## Output Template

```text
Scope Challenge: READY | NEEDS_REVISION | BLOCKED
Target: <smallest target state>
Anti-scope: <explicit exclusions>
Owner: <primary owner and lane-change owner>
Validator: <command, review path, or explicit gap>
Stop conditions: <what stops execution>
Summary file: <present and decision-ready, or missing>
Reading budget: <first files or checks before broader reading>
Coverage: <traceability owner, explicit not-applicable, or blocker>
```

Do not proceed to `apply-plan` when the result is `NEEDS_REVISION` or `BLOCKED`
unless the user explicitly accepts the risk.
