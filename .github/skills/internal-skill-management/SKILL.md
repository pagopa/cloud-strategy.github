---
name: internal-skill-management
description: Govern the repository skill catalog as a declared managed system audit overlap, normalize naming, refresh approved in-scope skills, extract reusable repo logic, and retire obsolete skills. Use when deciding which skills should remain in `.github/skills/` and removing fallback or deprecated variants.
---

# Internal Skill Management

Use this skill for source-side governance of `.github/skills/`. It is the operating manual behind `internal-sync-control-center` whenever the work involves catalog cleanup, naming normalization, targeted refresh, or retirement.

Use the current repository state as evidence and starting context, but keep decisions anchored to the declared governance contract in the relevant agent and root governance files.

Use `openai-skill-creator` when drafting or iterating the content of one specific skill.

## Goals

- Keep one clear canonical skill per intent.
- Keep the local catalog aligned with the declared repo routing and naming contract.
- Keep sync-control assets sync-specific and defer repository-wide bridge ownership to `AGENTS.md` and `.github/copilot-instructions.md`.
- Refresh approved in-scope external-prefixed skills without expanding scope implicitly.
- Move repo-specific operational logic into internal skills when an agent becomes too large or too procedural.
- Keep naming, frontmatter, links, and descriptions deterministic.
- Remove fallback, deprecated, or compatibility-only skills and aliases.

## Decision Order

1. Check the declared managed scope plus the current local inventory and neighboring trigger space.
2. Decide whether the capability should stay as an existing `internal-*` skill, stay as an existing approved in-scope external-prefixed skill, or be deleted.
3. Prefer consolidation over coexistence when two skills compete for the same trigger space.
4. Repair broken references only when the skill still adds distinct value.
5. Update downstream governance immediately after catalog changes.
6. When catalog changes touch managed resources or their references, re-check `.github/copilot-instructions.md` and root `AGENTS.md` in the same workflow and update them whenever drift or stale routing remains.

## Classification Matrix

| Case | Action |
|---|---|
| Repo-specific governance or workflow | Create or update an `internal-*` skill |
| Installed external-prefixed skill still useful and distinct | Refresh in place |
| Thin alias, fallback copy, or deprecated variant | Delete the weaker skill |
| Broken or stale skill with no unique value | Retire it |
| Large agent containing reusable procedural logic | Extract the logic into a skill |

## Workflow

### 1. Inventory Before Editing

- Read the target skill and at least the closest competing skills.
- Compare `description:` lines first. Trigger overlap starts there.
- Check whether the repository already has a stronger internal equivalent.
- Check whether an external-prefixed skill is still needed or only present out of habit.
- Check whether the skill references files that do not exist.
- Check whether nearby agents, prompts, or `AGENTS.md` still route to the skill.
- Check whether the skill still belongs to the declared managed scope or only survives due to repository drift.

### 2. Pick the Right Outcome

Use these heuristics:

- Keep both only when they serve clearly different intents.
- Merge only when the surviving skill becomes easier to trigger and easier to maintain.
- Delete when one skill is just a noisier, thinner, or less structured version of another.
- Create an internal skill when the capability is strategic for this repository and should not depend on external wording or lifecycle.
- Refresh an in-scope external-prefixed skill only when it still adds distinct value to the managed catalog.

### 3. Author or Refresh Carefully

Required frontmatter:

```yaml
---
name: internal-example
description: Clear trigger language that says what the skill does and when to use it.
---
```

Rules:

- `name:` must match the directory name exactly.
- Put trigger language in `description:`, not buried in the body.
- Keep repository-facing text in English.
- Do not keep runtime-specific clutter that weakens portability.
- Keep the local canonical identifier when refreshing an installed external-prefixed skill.
- Do not add compatibility notes or historical conversion prose unless the user explicitly asks for it.

### 3.1 Skill Authoring Handoff

When the decision is to create or improve one specific skill:

1. Use `openai-skill-creator` for the authoring and evaluation loop.
2. Return here to confirm the new or changed skill still belongs in the catalog.
3. Re-check overlap, naming, references, and downstream governance after the draft is ready.

### 4. Keep the Body High Signal

A good skill body should contain:

- A short statement of purpose.
- A concrete workflow.
- Decision rules and anti-patterns.
- Output expectations when the task benefits from structure.
- References to bundled files only when those files actually exist.
- A testing note when trigger accuracy or output shape is easy to verify.

Do not fill the body with marketing language, roleplay framing, or vague expertise claims.

## Overlap Review Checklist

Delete or replace a skill when most of these are true:

- The description triggers on the same user requests as another installed skill.
- The competing skill is more structured or more complete.
- The weaker skill adds no distinctive workflow.
- The weaker skill routes to missing resources or stale instructions.
- The repository already has an internal skill that should own the domain.

Keep specialized subskills only when they narrow the trigger space instead of broadening collision.

## Refresh Rules

When refreshing an installed external-prefixed skill:

1. Keep the existing local identifier and prefix.
2. Preserve only the capability that still maps to the current repository.
3. Remove stale runtime assumptions, deprecated frontmatter, and broken bundled references.
4. Do not add new sibling skills from the same family unless the user explicitly expands scope.
5. Update governance files only when routing or inventory meaningfully changes.

## Extraction Rules

When an agent is turning into a knowledge dump:

1. Keep the agent cohesive around routing, scope, and orchestration.
2. Move long reusable procedures into an internal skill.
3. Point the agent at that skill explicitly.
4. Keep the skill reusable outside the single current task.

Apply the same standard when broadening an agent: keep the operating role cohesive, and do not split purely to minimize file size or token count.

This is the preferred pattern for `internal-sync-control-center`.

For that agent specifically, keep managed scope, approval posture, and sync orchestration in the agent, keep reusable catalog procedure in skills, and keep repository-wide bridge policy in `AGENTS.md` plus `.github/copilot-instructions.md`.

## Validation

Before finishing:

- Confirm `name:` equals the folder name.
- Confirm every referenced local file exists.
- Confirm the description is specific enough to trigger, but not so broad that it collides with half the catalog.
- Confirm the skill is in English.
- Confirm inventory or governance files do not point to removed paths.
- Confirm the skill does not depend on runtime-specific tool names or deprecated frontmatter.
- Confirm nearby prompts or agents are not now redundant because of the new skill.
- Confirm no fallback alias or compatibility-only duplicate remains beside the canonical skill.

## Anti-Patterns

- Keeping duplicate skills "just in case."
- Refreshing an external skill just because the upstream changed when the local catalog does not need it.
- Importing or reintroducing historical variants that the live repository no longer uses.
- Creating internal skills that merely say "see another skill."
- Leaving retired or deprecated skills in the live catalog.
- Hiding important trigger words deep in the body instead of the description.
- Treating body length as a substitute for trigger quality.

## Handoff

When this skill is used from `internal-sync-control-center`:

1. Audit the catalog.
2. Decide keep, refresh, replace, extract, or retire.
3. Apply the catalog changes.
4. Re-check `.github/copilot-instructions.md` and root `AGENTS.md`, then update dependent governance artifacts.
5. Run repository validation.
