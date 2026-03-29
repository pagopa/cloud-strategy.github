---
name: internal-skill-management
description: Audit, create, improve, import, consolidate, and retire Copilot skills with strict naming, trigger, evaluation, and overlap control. Use when creating a new SKILL.md, importing upstream skills, extracting agent logic into a skill, tuning skill descriptions, testing trigger quality, deleting overlapping skills, or validating skill lifecycle quality in this repository.
---

# Internal Skill Management

Use this skill for repository-owned skill governance. It is the operating manual behind `internal-agent-sync` whenever the work involves skill creation, import, consolidation, or retirement.

## Goals

- Keep one clear canonical skill per intent.
- Prefer the best directly instead of keeping fallback duplicates.
- Move repo-specific operational logic into internal skills when an agent becomes too large or too procedural.
- Keep naming, frontmatter, links, and descriptions deterministic.
- Replace Claude-only skill-authoring workflow with a portable Copilot-first process.

## Decision Order

1. Decide whether the capability should be `internal-`, external-prefix, or deleted.
2. Check nearby skills before writing or importing anything.
3. Prefer consolidation over coexistence when two skills compete for the same trigger space.
4. Repair broken references only when the skill still adds distinct value.
5. Delete lower-value overlap when a stronger replacement already exists.

## Classification Matrix

| Case | Action |
|---|---|
| Repo-specific governance or workflow | Create or update an `internal-*` skill |
| Approved upstream capability with broad reusable value | Import under `<short-repo>-<name>` |
| Thin alias of a stronger skill | Delete the weaker skill |
| Broken or stale skill with no unique value | Retire it |
| Large agent containing reusable procedural logic | Extract the logic into a skill |

## Workflow

### 1. Inventory Before Editing

- Read the target skill and at least the closest competing skills.
- Compare `description:` lines first. Trigger overlap starts there.
- Check whether the repository already has a stronger internal equivalent.
- Check whether the skill references files that do not exist.

### 2. Pick the Right Outcome

Use these heuristics:

- Keep both only when they serve clearly different intents.
- Merge only when the surviving skill becomes easier to trigger and easier to maintain.
- Delete when one skill is just a noisier, thinner, or less structured version of another.
- Create an internal skill when the capability is strategic for this repository and should not depend on an upstream wording style.

### 3. Author or Import Carefully

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
- If adapting an upstream skill, normalize wording to GitHub Copilot terminology where needed.

### 3.1 Skill Authoring Loop

When creating or improving a skill, use this loop:

1. Capture intent, trigger phrases, output shape, and exclusions.
2. Draft the frontmatter and the smallest useful workflow body.
3. Test the description against realistic prompts from this repository's domains.
4. Tighten the trigger language when the skill under-triggers or collides with nearby skills.
5. Expand only after the workflow is already coherent.

Prefer lightweight local evaluation:

- Compare the new skill against nearby competing skills.
- Use 2-5 realistic prompts that resemble actual user requests.
- Judge whether the skill should trigger, not only whether the body looks polished.
- Record structural gaps in the skill itself instead of relying on external eval tooling.

Do not depend on Claude-only benchmarking flows, subagent-only evaluators, or viewer-specific tooling.

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

## Import Rules

When importing upstream skills:

1. Preserve the original capability.
2. Rename with the approved upstream prefix.
3. Remove or adapt stale wording that conflicts with this repository.
4. Avoid broken `references/` or `resources/` links.
5. Record the imported capability in repository governance files when it changes routing materially.

## Extraction Rules

When an agent is turning into a knowledge dump:

1. Keep the agent focused on routing, scope, and orchestration.
2. Move long reusable procedures into an internal skill.
3. Point the agent at that skill explicitly.
4. Keep the skill reusable outside the single current task.

This is the preferred pattern for `internal-agent-sync`.

## Validation

Before finishing:

- Confirm `name:` equals the folder name.
- Confirm every referenced local file exists.
- Confirm the description is specific enough to trigger, but not so broad that it collides with half the catalog.
- Confirm the skill is in English.
- Confirm inventory or governance files do not point to removed paths.
- Confirm the skill does not depend on runtime-specific tool names or deprecated frontmatter.
- Confirm nearby prompts or agents are not now redundant because of the new skill.

## Anti-Patterns

- Keeping duplicate skills "just in case."
- Importing upstream skills unchanged when they carry stale runtime assumptions.
- Creating internal skills that merely say "see another skill."
- Leaving retired skills in approved sync scope.
- Hiding important trigger words deep in the body instead of the description.
- Treating body length as a substitute for trigger quality.

## Handoff

When this skill is used from `internal-agent-sync`:

1. Audit the catalog.
2. Decide keep, import, replace, extract, or retire.
3. Apply the catalog changes.
4. Update dependent governance artifacts.
5. Run repository validation.
