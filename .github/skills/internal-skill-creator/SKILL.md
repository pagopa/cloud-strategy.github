---
name: internal-skill-creator
description: Use when creating or materially revising repository-owned skills under `.github/skills/`, including splits, replacements, or changes to scope, triggers, structure, or validation.
---

# Internal Skill Creator

## Core method

`mattpocock-writing-great-skills` is the core method for skill authoring and
revision. Load it before drafting. Apply its relevant rules throughout the
change instead of repeating them here.

## When to use

- The requested skill change affects repository-owned behavior or structure.

## Local reference

Read `references/authoring-and-evaluation.md` when creating a skill, changing
its boundary or trigger, or selecting an evaluation branch.

## Workflow

### 1. Repository preflight

Read the target `SKILL.md`, the nearest competing skills, and the applicable
`AGENTS.md`. Inventory the touched bundle. Read `.github/INVENTORY.md` only
when adding, retiring, renaming, or replacing a skill.

Completion criterion: the intended boundary, anti-scope, touched files, and
repository validation path are explicit.

### 2. Core authoring and revision

Load `mattpocock-writing-great-skills` as the core method. Draft or revise the
smallest coherent bundle. Check invocation, description, information hierarchy,
retrieval quality, and predictability. Remove duplication, sediment, and no-ops;
revise the draft in place instead of only reporting findings.

Completion criterion: every applicable core rule is reflected in the draft,
and each retained local instruction has a repository-specific reason to exist.

### 3. Proportional evaluation

Read `references/authoring-and-evaluation.md`. Select the applicable evaluation
branches. Record skipped branches and reasons.

Completion criterion: applicable branches have evidence; evidence, blockers,
and completion status are explicit.

### 4. Repository closure

1. Update `agents/openai.yaml` to match the revised skill purpose.
2. Run `python3 .github/scripts/validate_internal_skills.py --skill <name> --strict`.
3. Check routing fallout in nearby skills and agents.
4. Record before/after line and word counts for the touched bundle.

Completion criterion: structural validation passes, routing fallout is resolved, and
before/after measurements are recorded.
