---
name: internal-skill-creator
description: Use when creating, splitting, replacing, or materially revising a repository-owned skill under `.github/skills/`.
---

# Internal Skill Creator

## Referenced skills

- `anthropic-skill-creator`: authoring and proportional evaluation stage for repository-owned skill work.
- `mattpocock-writing-great-skills`: predictability review and revision stage applied after authoring.
- `local-agent-sync-external-resources`: catalog-governance sync for broader external-asset or inventory-wide work.
- `internal-agent-creator`: agent authoring and agent/skill boundary rewrites.

## When to use

- Creating a new repository-owned skill under `.github/skills/`.
- Replacing or splitting an existing repository-owned skill whose boundary is wrong.
- Materially revising a repository-owned skill's scope, trigger, structure, or validation.

## When not to use

- Catalog governance, inventory maintenance, or sync routing. Use `local-agent-sync-external-resources`.
- Agent authoring or agent/skill boundary rewrites. Use `internal-agent-creator`.
- Pure copyedit that does not affect retrieval, boundary, validation, or bundle structure.

## Preflight

1. Read the target `SKILL.md` and the nearest competing skills.
2. Read `AGENTS.md` before changing repository-owned scope or policy.
3. Read `.github/INVENTORY.md` when a skill may be added, retired, renamed, or replaced.
4. Inventory the touched bundle: `SKILL.md`, `agents/openai.yaml`, `references/`, `scripts/`, `assets/`.

## Workflow

### 1. Anthropic authoring

Load `anthropic-skill-creator` and run the authoring stage. Run only the
applicable evaluation branches for the current task; record every omitted
branch and its reason. Produce a draft with evidence: draft, evidence, blockers, and completion status for each evaluation branch.

Exit criteria: the draft exists with applicable evaluation branches assessed,
skipped branches and reasons recorded, and completion status stated.

### 2. Predictability review

Load `mattpocock-writing-great-skills` and use its vocabulary to revise the draft.
Apply all relevant rules. Check invocation, description, information hierarchy,
retrieval quality, and predictability. Detect duplication, sediment, no-op, and predictability failures. Revise the draft in place; do not merely report findings.

Exit criteria: the draft has been revised with all applicable predictability
rules applied and the changes are traceable to specific rules.

### 3. Repository closure

1. Update `agents/openai.yaml` to match the revised skill purpose.
2. Run `python3 .github/scripts/validate_internal_skills.py --skill <name> --strict`.
3. Check routing fallout in nearby skills and agents.
4. Record before/after line and word counts for the touched bundle.

Exit criteria: structural validation passes, routing fallout is resolved, and
before/after measurements are recorded.
