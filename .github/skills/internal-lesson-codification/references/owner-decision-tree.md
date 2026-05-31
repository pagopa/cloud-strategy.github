# Lesson Owner Decision Tree

Use this reference when a lesson's canonical owner is not obvious.

## Owner routing

| Lesson shape | Preferred owner |
| --- | --- |
| Path-specific editing rule or file-family constraint | Relevant umbrella or specialist skill, owned file, validator, or repository config |
| Reusable workflow, procedure, decision tree, or domain operating method | `.github/skills/*/SKILL.md` or a skill reference |
| VS Code route UX, handoff, tool boundary, or agent persona contract | `.github/agents/*.agent.md` |
| Reusable user-invoked output template or prompt-shaped interaction | `.github/prompts/*.prompt.md` |
| Enforceable repository contract, schema, or regression risk | Validator, test, or repository config |
| Non-policy background, architecture, or explanatory context | Non-README technical docs under `docs/` |
| Stable lesson not codified yet | `LESSONS_LEARNED.md` pending row |
| Stable repository-wide default that must be always visible | Proposal for `AGENTS.md` and, when needed, `.github/copilot-instructions.md` |

## New-resource gate

Create a new resource only when all are true:

- No existing owner can carry the lesson without broadening its scope incorrectly.
- The lesson is likely to recur across tasks or repositories.
- The new resource has a clear trigger, scope, and validation path.
- The resource would reduce future drift more than it adds catalog weight.

Prefer updating an existing owner when the lesson is a missing sharp edge inside that owner.

## Always-on gate

Treat `AGENTS.md` and `.github/copilot-instructions.md` as the last resort.

Before proposing either file, verify:

- The lesson is repository-wide, stable, and not path-specific.
- The lesson must be visible before skills or narrower owners can load.
- It is not a workflow detail, checklist, command playbook, or catalog inventory.
- The proposed wording is compact enough for the always-on token budget.
- The matching projection impact is understood for `.github/copilot-instructions.md`.

If any check fails, route to a smaller owner or keep the lesson pending.

## Ledger fallback

Use `LESSONS_LEARNED.md` only when the lesson is worth retaining but cannot be safely codified in the current task.

The ledger row should name the intended codification target. It should not duplicate a lesson that was already codified in the same change.
