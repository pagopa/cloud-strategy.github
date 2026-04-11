---
name: internal-skill-creator
description: Use when creating, replacing, splitting, or materially revising a repository-owned skill under `.github/skills/`, especially when trigger drift, overlap, weak discovery wording, or unclear local ownership make the current skill unreliable as the canonical local answer.
---

# Internal Skill Creator

Use this skill as the canonical entrypoint for repository-owned skill work in this repository.

This skill owns the local decision gate for repository-owned `.github/skills/` authoring:

- should the repository create, reuse, tighten, split, replace, or reject a skill change at all
- what belongs in the local owner versus support depth
- how to validate that the result improves retrieval and behavior instead of only adding text

Use `internal-agent-sync-control-center` when the task is broader catalog governance, sync-managed external assets, or inventory-wide retirement and refresh work.

Use `internal-agent-development` when the primary output is an agent change or an agent/skill boundary rewrite.

Use `openai-skill-creator` only as support depth after this skill has established that a repository-owned skill should exist and the remaining question is bundle anatomy, helper workflow, progressive disclosure, degrees-of-freedom guidance, or structural validation details.

## Read first

- Read the target `SKILL.md` plus the nearest competing skills that could already own the request.
- Read root `AGENTS.md` and `.github/copilot-instructions.md` before changing repository-owned scope or policy language.
- Read `.github/INVENTORY.md` when a skill may be added, retired, renamed, or replaced.
- Read `openai-skill-creator` only when bundle structure, helper scripts, or validation tooling is directly relevant.

## When to use

- Creating a new repository-owned skill under `.github/skills/`.
- Replacing or splitting an existing repository-owned skill whose current boundary is wrong.
- Materially revising a repository-owned skill's scope, trigger, structure, or validation.
- Tightening a skill whose description is too broad, too procedural, or too weak to retrieve reliably.

## When not to use

- The task is catalog governance, inventory maintenance, or sync routing. Use `internal-agent-sync-control-center` instead.
- The task is primarily agent authoring or agent/skill architecture. Use `internal-agent-development` instead.
- The task is outside `.github/skills/` or does not change a repository-owned skill.
- The existing skill already covers the need and only a small wording or routing tweak is required.
- The only missing detail is bundle anatomy, helper scripting, progressive disclosure, or structural validation. Use `openai-skill-creator` as support depth instead of widening this skill.

## Decision gate

| Situation | Best answer |
| --- | --- |
| Wording cleanup with no change to retrieval, owner, or validation | Update in place or do nothing |
| Same owner, but weak trigger/body/validation is causing misses | Revise the existing skill |
| One skill is handling two intents or colliding with another local owner | Split, replace, or retire the weaker skill |
| The change affects multiple skills, inventory meaning, or sync-managed assets | Use `internal-agent-sync-control-center` |
| The local policy decision is done and only bundle scaffolding or validation tooling remains | Use `openai-skill-creator` as support depth |

## Core rules

- Start by checking whether an existing repository-owned skill can be reused, narrowed, or updated in place.
- Do not create a new skill until you can state the concrete failure, ambiguity, or repeated authoring miss it must prevent.
- Require a baseline failure before a new or materially revised skill is accepted. If the undesired behavior has not been observed, the case is not ready.
- Prefer the smallest change that fixes the local problem.
- Keep `description:` trigger-only. It should say when the skill applies, not summarize the workflow.
- Make descriptions searchable with concrete terms people would actually type: skill, trigger, `.github/skills/`, `SKILL.md`, create, replace, revise, update, reuse, validation.
- Keep the body lean. Put only the local contract in `SKILL.md` and move optional depth into references or support skills only when repeated need justifies it.
- Do not turn this skill into a wrapper that claims to call an upstream skill. It owns the local policy gate directly.
- A good outcome may be reuse, narrowing, or deletion. Do not let the workflow bias toward creating another skill.

## Baseline evidence

- Accept concrete local evidence such as a failed retrieval, repeated review feedback, trigger overlap, weak discovery wording, stale validation expectations, or a documented miss in `tmp/superpowers/`.
- Reject vague justification such as "this feels reusable", "the repo might need it later", or "the text looks light".
- Treat "it's only wording" as insufficient unless the wording change clearly alters retrieval, boundary, or validation behavior.

## Workflow

1. Prove the need first.
   Record the baseline failure, ambiguity, or repeated authoring miss the skill must prevent.
2. Reject the weakest answer.
   Prefer reuse, tightening an existing trigger, or doing nothing when the evidence does not justify a new repository-owned owner.
3. Set the boundary before writing.
   Decide what this skill owns locally and which adjacent owner should win when the task is really sync governance, agent authoring, or another domain.
4. Draft trigger-safe frontmatter.
   Keep `name:` exact and keep `description:` focused on when the skill should load.
5. Keep the bundle lean.
   Add scripts, references, assets, or `agents/openai.yaml` only when they solve a repeated repository need rather than decorate the skill.
6. Validate the right thing.
   Check both retrieval quality and skill-type behavior before treating the skill as done.
7. Re-check routing fallout.
   Update nearby references only when the visible local entrypoint or ownership meaning actually changed.

## What to absorb from `obra-writing-skills`

- Fail first, then write: if there is no baseline miss, stop and reassess.
- Reuse or reject before inventing: reuse an existing skill, tighten routing, or do nothing when the evidence is weak.
- Close loopholes explicitly instead of relying on intent.
- Treat "it's obvious", "it's only wording", or "we can fix it later" as red flags, not reasons to proceed.
- Keep the token budget disciplined. Prefer selective cross-references over copying generic scaffolding or long examples.
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
- degrees-of-freedom guidance
- `agents/openai.yaml` generation details
- structural validation details

Do not copy those materials here unless the repository-owned skill would become incoherent without one small local pointer.

Do not import the OpenAI rule that `description:` should explain both what the skill does and when to use it; repository-owned skills here keep `description:` trigger-first and workflow-free.

When those details matter, reference the upstream support asset instead of turning this skill into a maintenance fork of generic Codex bundle documentation.

## Repository follow-up

- Update nearby routing or support-skill references when this skill changes the visible local entrypoint.
- Re-check `.github/INVENTORY.md` whenever a repository-owned skill is added, retired, renamed, or replaced.
- Escalate to `internal-agent-sync-control-center` when the change becomes catalog governance instead of one-skill authoring.

## Validation

- Confirm `name:` matches the folder name exactly.
- Confirm the skill is repository-owned and still the smallest credible answer to the problem.
- Confirm the description matches the real trigger without describing the workflow.
- Confirm the result makes rejection, reuse, and in-place tightening as natural as creation or replacement.
- Confirm the skill still points to the right adjacent owner when the work is actually catalog governance, agent authoring, or support-depth anatomy.
- Confirm no copied OpenAI bundle documentation or broad OBRA process baggage slipped into the body.
- Recheck that the skill would help a future search find it quickly using the terms people would actually type.

## Common mistakes

- Writing a skill because a request feels familiar, not because the repository needs a reusable owner.
- Mixing catalog governance into a repo-owned skill authoring contract.
- Turning every change into a new skill instead of tightening or reusing an existing one.
- Using a long description that tells the agent what to do instead of when to load the skill.
- Forking helper material from support-depth skills instead of keeping the internal skill focused.
- Skipping the baseline and rationalizing the change as "small enough".
- Copying OpenAI bundle anatomy or OBRA process weight into the local policy gate.
