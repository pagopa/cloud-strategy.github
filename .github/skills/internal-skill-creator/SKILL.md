---
name: internal-skill-creator
description: Use when creating, replacing, or materially revising repository-owned skills under `.github/skills/`, especially when trigger drift, overlap, vague discovery wording, or a missing baseline makes the right scope unclear.
---

# Internal Skill Creator

Use this skill as the canonical entrypoint for repository-owned skill work in this repository.

Use `internal-agent-sync-control-center` when the task is broader catalog governance, sync-managed external assets, or inventory-wide retirement and refresh work.

Use `openai-skill-creator` only as support depth after this skill has established that a repository-owned skill should exist and the remaining question is bundle anatomy, helper workflow, progressive disclosure, or structural validation details.

## When to use

- Creating a new skill under `.github/skills/`.
- Replacing an existing repository-owned skill.
- Materially revising a repository-owned skill's scope, trigger, structure, or validation.
- Tightening a skill whose description is too broad, too procedural, or hard to discover.

## When not to use

- The task is catalog governance, inventory maintenance, or sync routing. Use `internal-agent-sync-control-center` instead.
- The task is outside `.github/skills/` or does not change a repository-owned skill.
- The existing skill already covers the need and only a small wording or routing tweak is required.

## Core rules

- Start by checking whether an existing repository-owned skill can be reused, narrowed, or updated in place.
- Do not create a new skill until you can state the concrete failure, ambiguity, or repeated need it is meant to prevent.
- Require a baseline failure before a new or revised skill is accepted: if the undesired behavior has not been observed, the case is not ready.
- Prefer the smallest change that fixes the local problem.
- Keep the description trigger-only. It should say when the skill applies, not summarize the workflow.
- Make descriptions searchable with concrete terms: skill, trigger, `.github/skills/`, `SKILL.md`, create, replace, revise, update, reuse, validation.
- Keep the body concise. Avoid narrative history, duplicated examples, and process that belongs in another skill.

## Workflow

1. Prove the need first.
   Record the failure, ambiguity, or repeated authoring miss that the skill must prevent.
2. Reject the weakest answer.
   Prefer reuse, tightening an existing trigger, or doing nothing when the evidence does not justify a new repository-owned owner.
3. Set the boundary before writing.
   Decide what this skill owns locally and which adjacent owner should win when the task is really sync governance, agent authoring, or another domain.
4. Write trigger-safe frontmatter.
   Keep `description:` focused on when the skill should load, not on what workflow it will execute.
5. Keep the bundle lean.
   Put only the local contract in `SKILL.md` and reference support-depth material instead of cloning it.
6. Validate the right thing.
   Check both retrieval quality and skill-type behavior before treating the skill as done.

## What to absorb from `obra-writing-skills`

- Fail first, then write: if there is no baseline miss, stop and reassess.
- Reuse or reject before inventing: reuse an existing skill, tighten routing, or do nothing when the evidence is weak.
- Close loopholes explicitly instead of relying on intent.
- Treat "it's obvious", "it's only wording", or "we can fix it later" as red flags, not reasons to proceed.
- Test the skill type you are writing:
  - Discipline skills need negative cases, loophole checks, and reruns.
  - Technique skills need a failing case, a success case, and one misuse case.
  - Pattern skills need boundary checks and counterexamples.
  - Reference skills need example fidelity and retrieval checks.

## What to leave to `openai-skill-creator`

Use `openai-skill-creator` as support depth only for:

- bundle anatomy
- helper scripts
- progressive disclosure
- structural validation details

Do not copy those materials here unless they are needed to keep the repository-owned skill coherent.

When those details matter, reference the upstream support asset instead of turning this skill into a maintenance fork of generic Codex bundle documentation.

## Repository follow-up

- Update nearby routing or support-skill references when this skill changes the visible local entrypoint.
- Re-check `.github/INVENTORY.md` whenever a repository-owned skill is added or retired.
- Escalate to `internal-agent-sync-control-center` when the change becomes catalog governance instead of one-skill authoring.

## Validation

- Confirm the skill name is exact and repository-owned.
- Confirm the description would match the real trigger without describing the workflow.
- Confirm the new or revised skill is the smallest credible answer to the problem.
- Confirm the skill still points to the right adjacent owner when the work is actually catalog governance.
- Recheck that the skill would help a future search find it quickly using the terms people would actually type.

## Common mistakes

- Writing a skill because a request feels familiar, not because the repository needs a reusable owner.
- Mixing catalog governance into a repo-owned skill authoring contract.
- Using a long description that tells the agent what to do instead of when to load the skill.
- Forking helper material from support-depth skills instead of keeping the internal skill focused.
- Skipping the baseline and rationalizing the change as "small enough".
