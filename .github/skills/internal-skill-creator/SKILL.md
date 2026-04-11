---
name: internal-skill-creator
description: Use first when creating, modifying, replacing, splitting, or materially revising any repository-owned skill under `.github/skills/`. This is the canonical local entrypoint for skill work in this repository and should load before `openai-skill-creator` so repo-local ownership, routing, retrieval, and validation rules are established before the OpenAI core workflow expands the bundle.
---

# Internal Skill Creator

Use this skill as the canonical repository-owned first entrypoint for skill authoring in this repository.

Keep the ownership model explicit:

- `internal-skill-creator` is the canonical local owner for repository-owned `.github/skills/` work.
- `openai-skill-creator` is the core operating engine inside that wrapper for bundle anatomy, reusable resources, `agents/openai.yaml`, initialization workflow, and structural validation.
- this skill adds the repository-specific gate: prove the need, choose reuse versus creation, keep triggers retrieval-safe, and harden the result against rationalization and boundary drift

This means `internal-skill-creator` should trigger first for repository-owned skill work, and then deliberately load `openai-skill-creator` as its embedded core workflow instead of competing with it as a parallel first choice.

Use `internal-agent-sync-control-center` when the task is broader catalog governance, sync-managed external assets, or inventory-wide retirement and refresh work.

Use `internal-agent-development` when the primary output is an agent change or an agent/skill boundary rewrite.

## Read first

- After this skill triggers, immediately read `openai-skill-creator` and treat it as the base workflow for skill bundle design, `agents/openai.yaml`, and structural validation.
- Read the target `SKILL.md` plus the nearest competing skills that could already own the request.
- Read root `AGENTS.md` and `.github/copilot-instructions.md` before changing repository-owned scope or policy language.
- Read `.github/INVENTORY.md` when a skill may be added, retired, renamed, or replaced.
- Load `references/writing-skills-checklist.md` when creating a new skill or materially revising an existing one.

## When to use

- Creating a new repository-owned skill under `.github/skills/`.
- Replacing or splitting an existing repository-owned skill whose current boundary is wrong.
- Materially revising a repository-owned skill's scope, trigger, structure, bundled resources, or validation.
- Tightening a skill whose description is too broad, too procedural, or too weak to retrieve reliably.

## When not to use

- The task is catalog governance, inventory maintenance, or sync routing. Use `internal-agent-sync-control-center` instead.
- The task is primarily agent authoring or agent/skill architecture. Use `internal-agent-development` instead.
- The task is outside `.github/skills/` or does not change a repository-owned skill.
- The existing skill already covers the need and only a small wording or routing tweak is required.

## Core wrapper model

Treat `openai-skill-creator` as the core workflow, not as an afterthought:

1. Use the OpenAI skill to shape the bundle.
   Reuse its anatomy for `SKILL.md`, `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`.
2. Apply the local decision gate before expanding the bundle.
   Decide whether the right answer is no-op, reuse, revise in place, split, replace, or retire.
3. Add repository-specific guardrails.
   Keep `description:` trigger-only, preserve local ownership boundaries, and force baseline evidence before major changes.
4. Validate twice.
   Run the OpenAI structural validator, then run retrieval and behavior checks appropriate to the skill type.

This skill is therefore a wrapper with stronger local policy, not a substitute for the OpenAI skill-creation engine.

## Trigger precedence

- For any repository-owned skill work under `.github/skills/`, start with `internal-skill-creator`, not `openai-skill-creator`.
- Use `openai-skill-creator` only after this wrapper has established that the task really belongs to a repository-owned skill in this repository.
- If both skills appear relevant, prefer this skill first because its description is the repo-local route and the OpenAI skill is the embedded engine.

## Decision gate

| Situation | Best answer |
| --- | --- |
| Wording cleanup with no change to retrieval, owner, or validation | Update in place or do nothing |
| Same owner, but weak trigger/body/validation is causing misses | Revise the existing skill |
| One skill is handling two intents or colliding with another local owner | Split, replace, or retire the weaker skill |
| The change affects multiple skills, inventory meaning, or sync-managed assets | Use `internal-agent-sync-control-center` |
| The change is mostly about skill-bundle anatomy, reusable resources, `agents/openai.yaml`, or validator usage | Use `openai-skill-creator` as the core engine inside this wrapper |

## Core rules

- Start by checking whether an existing repository-owned skill can be reused, narrowed, or updated in place.
- Do not create a new skill until you can state the concrete failure, ambiguity, or repeated authoring miss it must prevent.
- Require a baseline failure before a new or materially revised skill is accepted. If the undesired behavior has not been observed, the case is not ready.
- Treat skills as reusable reference guides, not narratives about how one task was solved once.
- Prefer the smallest change that fixes the local problem.
- Keep `description:` trigger-only. It should say when the skill applies, not summarize the workflow.
- Use active, searchable naming when creating a new skill. Prefer direct verbs or action-shaped names over abstract labels when that improves retrieval.
- Make descriptions searchable with concrete terms people would actually type: skill, trigger, `.github/skills/`, `SKILL.md`, create, replace, revise, update, reuse, validation.
- Keep the body lean. Put only the local contract in `SKILL.md` and move optional depth into references or reusable tools when repeated need justifies it.
- Keep cross-references explicit instead of duplicating large chunks of generic bundle guidance.
- A good outcome may be reuse, narrowing, deletion, or replacement. Do not let the workflow bias toward creating another skill.

## Bundle requirements

For repository-owned skills in this repository, treat these as the default bundle expectations unless there is a concrete reason not to:

- `SKILL.md` with exact `name:` and retrieval-safe `description:`
- `agents/openai.yaml` with `display_name`, `short_description`, and a `default_prompt` that mentions `$skill-name`
- `references/` when deeper material improves the skill without bloating `SKILL.md`
- `scripts/` only when deterministic or repeated workflow support is justified

When creating a new skill, prefer the OpenAI initializer:

```bash
.github/skills/openai-skill-creator/scripts/init_skill.py <skill-name> --path .github/skills --interface display_name="..." --interface short_description="..." --interface default_prompt="Use $<skill-name> ..."
```

When refreshing an existing skill's UI metadata, regenerate:

```bash
.github/skills/openai-skill-creator/scripts/generate_openai_yaml.py .github/skills/<skill-name> --interface display_name="..." --interface short_description="..." --interface default_prompt="Use $<skill-name> ..."
```

## Baseline evidence

- Iron law: no new skill and no material skill edit without a failing baseline first.
- Accept concrete local evidence such as a failed retrieval, repeated review feedback, trigger overlap, weak discovery wording, stale validation expectations, or a documented miss in `tmp/superpowers/`.
- Reject vague justification such as "this feels reusable", "the repo might need it later", or "the text looks light".
- Treat "it's only wording" as insufficient unless the wording change clearly alters retrieval, boundary, or validation behavior.
- Apply the same standard to edits as to new skills. A major edit without a failing baseline is still missing proof.

## Workflow

1. Start from the OpenAI core.
   Load `openai-skill-creator` and use its creation process, anatomy rules, and validation tooling as the base workflow.
2. Prove the need first.
   Record the baseline failure, ambiguity, or repeated authoring miss the skill must prevent.
3. Reject the weakest answer.
   Prefer reuse, tightening an existing trigger, or doing nothing when the evidence does not justify a new repository-owned owner.
4. Set the boundary before writing.
   Decide what this skill owns locally and which adjacent owner should win when the task is really sync governance, agent authoring, or another domain.
5. Build or refresh the bundle.
   Use the OpenAI workflow to keep `agents/openai.yaml`, reusable resources, and bundle structure coherent.
6. Apply the local wrapper checks.
   Use `references/writing-skills-checklist.md` to tighten trigger wording, token discipline, loophole closure, and test design.
7. Validate the right thing.
   Run the OpenAI structural validator and then check retrieval quality plus skill-type behavior before treating the skill as done.
8. Re-check routing fallout.
   Update nearby references only when the visible local entrypoint or ownership meaning actually changed.

## What this wrapper adds beyond `openai-skill-creator`

- A hard proof gate before creation or major revision.
- A local reuse-versus-create decision instead of automatic bundle expansion.
- Trigger-only description discipline for repository-owned skills.
- Boundary enforcement against sync governance and agent authoring drift.
- Skill-type testing and anti-rationalization checks distilled from `writing-skills`.

## What to absorb from `writing-skills`

- Fail first, then write: if there is no baseline miss, stop and reassess.
- Reuse or reject before inventing: reuse an existing skill, tighten routing, or do nothing when the evidence is weak.
- Treat skills as reusable guides rather than narratives.
- Close loopholes explicitly instead of relying on intent.
- Treat "it's obvious", "it's only wording", or "we can fix it later" as red flags, not reasons to proceed.
- Keep the token budget disciplined. Prefer selective cross-references over copying generic scaffolding or long examples.
- Test the skill type you are writing:
  - Discipline skills need negative cases, loophole checks, and reruns.
  - Technique skills need a failing case, a success case, and one misuse case.
  - Pattern skills need boundary checks and counterexamples.
  - Reference skills need example fidelity, retrieval checks, and application checks.

## Validation

Run the OpenAI structural validator:

```bash
python3 .github/skills/openai-skill-creator/scripts/quick_validate.py .github/skills/<skill-name>
```

Then confirm:

- `name:` matches the folder name exactly.
- `agents/openai.yaml` exists and still matches the skill's current purpose.
- the skill is repository-owned and still the smallest credible answer to the problem.
- the description matches the real trigger without describing the workflow.
- the description is strong enough that repository-owned skill requests should retrieve this skill before the generic OpenAI one.
- the result makes rejection, reuse, and in-place tightening as natural as creation or replacement.
- the skill still points to the right adjacent owner when the work is actually catalog governance or agent authoring.
- the skill reads like a reusable guide instead of a one-off narrative.
- the retrieval and pressure tests appropriate to the skill type have actually been run.
- the body did not become a maintenance fork of generic OpenAI bundle documentation.

## Repository follow-up

- Update nearby routing or support-skill references when this skill changes the visible local entrypoint.
- Re-check `.github/INVENTORY.md` whenever a repository-owned skill is added, retired, renamed, or replaced.
- Escalate to `internal-agent-sync-control-center` when the change becomes catalog governance instead of one-skill authoring.

## Common mistakes

- Writing a skill because a request feels familiar, not because the repository needs a reusable owner.
- Treating `openai-skill-creator` as irrelevant when it should be the bundle-design core.
- Mixing catalog governance into a repo-owned skill authoring contract.
- Turning every change into a new skill instead of tightening or reusing an existing one.
- Using a long description that tells the agent what to do instead of when to load the skill.
- Skipping `agents/openai.yaml` even though the repository expects it for internal skills.
- Skipping the baseline and rationalizing the change as "small enough".
- Copying OpenAI bundle anatomy or OBRA process weight wholesale into the local wrapper instead of selecting only what improves the repository-owned owner.
