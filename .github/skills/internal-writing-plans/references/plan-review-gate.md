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
| Validability | Is there a concrete validator, review path, or explicit validation gap? |
| Evidence | Are external claims, provenance paths, or comparative patterns cited where needed? |
| Scope | Are anti-scope and stop conditions explicit enough to prevent drift? |

## Outcomes

- `READY`: the plan can move to execution or handoff.
- `REVISE`: the plan needs local edits before execution.
- `ASK`: a user decision is required before execution.

## Rules

- Keep the gate plain text and short.
- Prefer editing the retained plan over explaining around a bad plan.
- Do not add persona agents, runtime-specific frontmatter, or external workflow
  dependencies.
