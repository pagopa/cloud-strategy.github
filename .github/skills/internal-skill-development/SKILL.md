---
name: internal-skill-development
description: Create, revise, evaluate, and harden repository-owned Copilot skills. Use when drafting a new SKILL.md, converting upstream skill-authoring guidance into an internal skill, improving trigger quality, building bundled references or scripts, or testing whether a skill is strong enough to keep.
---

# Internal Skill Development

Use this skill when the output is a skill, not an agent.

## Purpose

This is the repository-owned Copilot-safe conversion of upstream skill-authoring guidance. It focuses on writing and improving one skill at a time.

Use `internal-skill-management` when the work is about catalog governance, imports, deduplication, retirement, or overlap decisions across multiple skills.

## Core repository inputs

- `AGENTS.md` for preferred skills, routing, and inventory alignment
- `.github/copilot-instructions.md` for non-negotiable repository behavior
- `.github/scripts/validate-copilot-customizations.sh` for final structural validation
- `references/evaluation-loop.md` for the Copilot-safe evaluation cycle

## Skill package model

A repository-owned skill may contain:

- `SKILL.md` as the canonical entry point
- `references/` for heavier documentation or examples
- `scripts/` for deterministic or repeated tasks
- `assets/` only when output generation truly depends on files

Do not add `README.md`, changelog files, or auxiliary process notes inside the skill directory.

## Authoring workflow

1. Capture the exact capability, triggering conditions, exclusions, and expected output.
2. Check nearby skills before writing anything.
3. Draft the `description:` first. It is the routing contract.
4. Write the smallest useful body: purpose, workflow, constraints, validation.
5. Decide whether helper material belongs inline, in `references/`, or in `scripts/`.
6. Test the skill with realistic prompts and near-miss prompts.
7. Tighten the wording until the skill is both discoverable and distinct.

## Description rules

Strong descriptions:

- start with `Use when`
- describe concrete situations, symptoms, or decision points
- stay concise enough to be scanned quickly
- make the skill's domain obvious without narrating the whole workflow

Weak descriptions:

- describe prestige instead of trigger conditions
- summarize every step of the skill
- collide with broad generic requests already owned by another skill

## Writing rules

- Keep repository-facing text in English.
- Prefer imperative, high-signal instructions.
- Explain why a rule matters instead of relying on rigid all-caps wording.
- Bundle helper scripts only when repeated work shows they would pay off.
- Prefer one strong internal skill over multiple overlapping aliases.

## Copilot-safe evaluation loop

Use a local evaluation loop that does not depend on Claude-specific viewers or runtime hooks:

1. Create 2-5 realistic prompts a real repository user might write.
2. Include near misses that should not trigger the skill.
3. Run the prompts against the current draft or compare before/after versions.
4. Inspect outputs, transcripts, diffs, and failure modes.
5. Improve the skill based on repeated mistakes, ambiguity, or wasted steps.
6. Repeat until the skill is reliably useful and clearly differentiated.

If the same helper script or reference keeps getting reinvented across tests, bundle it into the skill instead of repeating it in prose.

## When to add bundled resources

- Add `references/` when the body would otherwise become noisy or too long.
- Add `scripts/` when the workflow needs repeatable deterministic execution.
- Add `assets/` only when an output template or binary resource is actually needed.

Do not create bundled files just to imitate a richer upstream package.

## Anti-patterns

- Writing a skill before checking whether the repository already has one for the same trigger space
- Keeping `description:` vague and compensating with a giant body
- Importing upstream skill text unchanged when it assumes a different runtime
- Adding reference or script files that no part of `SKILL.md` actually uses
- Leaving a stronger internal and a weaker external skill active for the same intent

## Validation

- Confirm `name:` matches the directory name exactly.
- Confirm the `description:` is specific enough to trigger correctly.
- Confirm every referenced local path exists.
- Confirm the skill adds value beyond nearby internal or approved external skills.
- Run `python3 .github/scripts/validate-copilot-customizations.sh --scope root --mode strict` after changes that affect inventory or naming.
