# Plan Review Gate

Use this gate for a lightweight review before a retained plan moves to execution
or handoff. It checks clarity and validity without creating reviewer personas.

## Source Patterns

- Comparative source: `tmp/external-comparison/compound-engineering-plugin/plugins/compound-engineering/skills/ce-plan/SKILL.md`.
- Comparative source: `tmp/external-comparison/compound-engineering-plugin/plugins/compound-engineering/skills/ce-doc-review/SKILL.md`.
- Adopt the document/plan review gate only. Do not import Compound runtime or
  persona agents.

## Checklist

| Check | Question |
| --- | --- |
| Clarity | Can an executor identify the target files, owner, and next action without guessing? |
| Coherence | Do the objective, rationale, executable steps, and validation path agree? |
| Spec sufficiency | Are the target, success criteria, boundaries, validation path, and open questions concrete enough to decide whether execution is safe? |
| Validability | Is there a concrete validator, review path, or explicit validation gap? |
| Observable acceptance | Does each executable verb name the expected diff, file state, assertion, or explicit non-action that will prove it was done? |
| Evidence | Are external claims, provenance paths, or comparative patterns cited where needed? |
| Scope | Are anti-scope and stop conditions explicit enough to prevent drift? |
| Summary focus | Does `01-change-summary.md` contain only the compressed Italian decision capsule with required sections and a `Risorsa \| Azione \| Scopo` table for non-trivial plans? |
| Summary clarity | Are changed resources and intended actions obvious in the summary? |
| Summary counter-validation | Does `01-change-summary.md` preserve enough observable result criteria for the user to counter-validate coverage without reading `02-execution.md` or `02-control.md`? |
| Semantic coverage | For `compact`, does `02-execution.md` preserve each requested or source item with stable item id, observable acceptance, evidence class, status, and route? For `extended`, does `02-control.md` preserve the same coverage? |
| Implementation contract | For `extended` profiles, does `02-control.md` include the exact sources, target files, validation order, blockers, and any external pin or fallback? For `compact` profiles, a separate implementation contract is not required. |
| Profile | Is `Plan profile` declared as `compact` or `extended`? Missing or unsupported profiles return `unsupported-plan-contract`. |
| Executor context | Can a smaller or lower-context executor see the key files, validators, owner, assumptions, and stop conditions without rediscovering the plan? |
| File naming | Are plan file names English while `01-change-summary.md` is Italian and all executable/control files are English? |
| Folder semantics | For `extended`, does `02-control.md` state `Recommended use` and `File map and role` so a generic reader can tell whether the folder is for review, apply, resume, rewrite, or status only? |
| Route map | Do ledger `Route` values map to existing executable numbered files, or to explicit non-action routes such as `closed`, `manual`, `gap`, or `not applicable`? |
| Open questions | Is `questions.md` present and set to `- none` for execution handoff, or explicitly blocking handoff? |
| Lifecycle status | Is plan state explicit (`scaffold`, `ready`, or `closed`) so an executor does not infer readiness? |
| Token discipline | Does the ledger define `Initial evidence pass` and `Reading budget` so the executor can classify the folder with the fewest safe reads? |
| Profile token budget | Is `compact` within the 2,000 estimated-token total budget, with `01-change-summary.md` under 300 and `02-execution.md` under 1,500, or escalated to `extended`? For `extended`, are soft limits reviewed with completeness over compression and split-by-slice decisions when files grow large? |

## Outcomes

- `READY`: the plan can move to execution or handoff.
- `REVISE`: the plan needs local edits before execution.
- `ASK`: a user decision is required before execution.

## Rules

- Keep the gate plain text and short.
- Prefer editing the retained plan over explaining around a bad plan.
- Reframe vague requirements into observable success criteria when evidence supports it; otherwise return `ASK` instead of accepting an unverifiable plan.
- Treat clarification-only completion for executable verbs as a plan defect. Rewrite the item until an executor can prove it from diff, file, validator, manual, or explicit-gap evidence.
- Do not add persona agents, runtime-specific frontmatter, or external workflow
  dependencies.
- For strategic-to-operational conversions, coverage review comes before shape-only validation.
- For plans intended for a smaller or lower-context executor, keep technical
  identifiers, file names, commands, and validation steps explicit. Short
  English glosses near critical decisions are allowed when they reduce handoff
  ambiguity.
- Treat missing merged-contract sections in `02-control.md` as a plan-quality defect for `extended` profiles. For `compact` profiles, a separate implementation contract is not required unless the plan changes always-on guidance, validators, or cross-family contracts.
- For `compact`, treat missing `Plan profile` and control header in `02-execution.md` as a plan-quality defect.
- When external evidence is needed, require an exact pin or explicit fallback in `02-control.md` before approving execution.
- Treat a long or overloaded `01-change-summary.md` as a plan-quality defect, not as a documentation nit. It should be a compressed decision capsule, not a control file.
- Treat an English `01-change-summary.md` as a plan-quality defect per the current retained-plan contract (Italian only).
- Treat an unclear resource table or missing resource-action-purpose columns in `01-change-summary.md` as a plan-quality defect.
- Treat a summary as a plan-quality defect when output, schema, or data-contract
  changes are compressed into generic formulas without concrete observable
  examples. Keep those user-visible facts in `Risultato atteso` or
  `Risorse coinvolte`, not in execution detail.
- Treat a missing or weak source-item ledger as a plan-quality defect, not as a documentation nit.
- Treat a missing evidence pass or reading budget as a token-waste defect for non-trivial retained plans.
- Treat missing source-item coverage for requested work as a plan-quality defect, not as an editorial preference.
- Treat an unsupported or missing `Plan profile` as a plan-quality defect.
