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
| Evidence | Are external claims, provenance paths, or comparative patterns cited where needed? |
| Scope | Are anti-scope and stop conditions explicit enough to prevent drift? |
| Semantic coverage | When converting an existing strategic or monolithic plan, does the new plan preserve each source item in a traceability matrix or equivalent owner before retiring the source artifact? |
| Executor context | Can a smaller or lower-context executor see the key files, validators, owner, assumptions, and stop conditions without rediscovering the plan? |
| Folder semantics | Does `01-riassunto-direzione-e-decisione.md` state `Uso consigliato` and `Mappa file e ruolo` so a generic reader can tell whether the folder is for review, apply, resume, rewrite, or status only? |
| Token discipline | Does the summary define `Evidence pass iniziale` and `Budget lettura` so the executor can classify the folder with the fewest safe reads? |

## Outcomes

- `READY`: the plan can move to execution or handoff.
- `REVISE`: the plan needs local edits before execution.
- `ASK`: a user decision is required before execution.

## Rules

- Keep the gate plain text and short.
- Prefer editing the retained plan over explaining around a bad plan.
- Reframe vague requirements into observable success criteria when evidence supports it; otherwise return `ASK` instead of accepting an unverifiable plan.
- Do not add persona agents, runtime-specific frontmatter, or external workflow
  dependencies.
- For strategic-to-operational conversions, coverage review comes before shape-only validation.
- For plans intended for a smaller or lower-context executor, keep technical
  identifiers, file names, commands, and validation steps explicit. Short
  English glosses near critical decisions are allowed when they reduce handoff
  ambiguity.
- Treat a missing or weak summary control file as a plan-quality defect, not as a documentation nit.
- Treat a missing evidence pass or reading budget as a token-waste defect for non-trivial retained plans.
- Treat missing source-item coverage in a strategic-to-operational conversion as a plan-quality defect, not as an editorial preference.
