---
description: Repository-owned Copilot agent and skill authoring guardrails for boundary clarity, paired-asset coherence, and minimal duplication.
applyTo: ".github/agents/*.agent.md,.github/skills/**/SKILL.md"
---

# Copilot Agent And Skill Authoring Instructions

## Scope

- Use this instruction for repository-owned agent entrypoints and skill entrypoints.
- Keep repository artifact authoring in English.

## Workflow

- Load `internal-agent-development` before planning or editing a repository-owned agent, or before redefining the boundary between an agent, skill, prompt, and instruction.
- Load `internal-skill-creator` before creating or materially revising a repository-owned `SKILL.md`. If the change also rewrites the adjacent agent/skill split, load `internal-agent-development` as well.
- When editing one asset in a paired bundle, inspect the adjacent paired asset plus any directly referenced local docs before finalizing. Fix only the necessary drift in the same change.

## Cohesion

- Keep agents focused on routing, role, boundaries, tool contract, and output expectations.
- Keep `SKILL.md` focused on reusable workflow, anti-scope, and validation. Move detailed matrices, templates, and long checklists into local `references/` files when they are reusable.
- Do not duplicate the same operational subtopic inventory across an agent, its paired skill, and supporting references. Keep one owner per detail layer.
- If an agent points to a paired skill or reference as the detailed contract owner, keep the agent summary-only and remove re-listed subtopics.
- If a skill points readers to local references for depth, keep `SKILL.md` lean and avoid re-copying reference-owned material inline.

## Skill Sections

- Use `## Mandatory Engine Skills` only for required engines.
- Use `## Optional Support Skills` only for conditional helpers.
- Use `## Skill Usage Contract` only when declared skills are genuinely conditional.
- Treat `## Preferred/Optional Skills` as legacy and do not introduce it in repository-owned agents.

## Validation

- Re-check frontmatter alignment, declared skills, adjacent paired assets, and local references before finishing.
- Run the closest existing catalog or skill validation that covers the touched assets.
