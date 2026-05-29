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
| Critical challenge | Did non-trivial or governance-sensitive retained-plan authoring use `internal-gateway-critical-master` before plan files were written, and did the plan absorb the outcome? |
| Summary focus | Does `01-change-summary.md` contain only the short proposed-change summary, problem, rationale, validation path, and decision request? |
| Semantic coverage | Does `02-source-item-ledger.md` preserve each requested or source item with stable item id, observable acceptance, evidence class, status, and route before execution starts? |
| Implementation contract | Does `04-implementation-contract.md` name the exact sources, target files, validation order, blockers, and any external pin or fallback, or clearly say `Implementation contract: not applicable`? |
| Executor context | Can a smaller or lower-context executor see the key files, validators, owner, assumptions, and stop conditions without rediscovering the plan? |
| File naming | Are new or rewritten retained-plan file names English while the plan content stays Italian by default? |
| Folder semantics | Does `02-source-item-ledger.md` state `Uso consigliato` and `Mappa file e ruolo` so a generic reader can tell whether the folder is for review, apply, resume, rewrite, or status only? |
| Token discipline | Does the ledger define `Evidence pass iniziale` and `Budget lettura` so the executor can classify the folder with the fewest safe reads? |

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
- Treat a missing critical challenge for non-trivial or governance-sensitive retained plans as a plan-quality defect unless the ledger records an explicit not-applicable reason.
- For plans intended for a smaller or lower-context executor, keep technical
  identifiers, file names, commands, and validation steps explicit. Short
  English glosses near critical decisions are allowed when they reduce handoff
  ambiguity.
- Treat a missing or weak `04-implementation-contract.md` as a plan-quality defect when the plan changes skills, agents, prompts, instructions, workflows, imported assets, linked files, validators, inventory, or shared runtime behavior.
- Treat a missing `questions.md` as a plan-quality defect for retained plans; use `- none` when no user-only blocker remains.
- When external evidence is needed, require an exact pin or explicit fallback in `04-implementation-contract.md` before approving execution.
- Treat a long or overloaded `01-change-summary.md` as a plan-quality defect, not as a documentation nit.
- Treat a missing or weak source-item ledger as a plan-quality defect, not as a documentation nit.
- Treat a missing evidence pass or reading budget as a token-waste defect for non-trivial retained plans.
- Treat missing source-item coverage for requested work as a plan-quality defect, not as an editorial preference.
