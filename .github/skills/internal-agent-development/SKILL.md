---
name: internal-agent-development
description: Create, refine, split, or realign repository-owned Copilot agents with focused routing, concise system prompts, and command-center responsibilities. Use when adding or updating a `.github/agents/*.agent.md`, renaming agents to canonical internal identifiers, or splitting broad agents into narrower command centers.
---

# Internal Agent Development

Use this skill when designing or updating repository-owned agents.

## Purpose

This skill defines the current repository standard for building command-center agents for GitHub Copilot without deprecated frontmatter or runtime-specific assumptions.

Use `internal-skill-development` when the work is about writing a skill. Use this skill when the output is an agent.

## Core repository inputs

Read these assets before finalizing an internal agent:

- `AGENTS.md` for routing language and repository inventory
- `.github/copilot-instructions.md` for the non-negotiable behavior layer
- `.github/scripts/validate-copilot-customizations.sh` for canonical validation expectations
- `references/agent-template.md` for the standard internal agent skeleton
- `references/conversion-checklist.md` for normalizing imported or older agent patterns into the current repository standard

## Agent Design Rules

- Frontmatter must contain `name:` and `description:` only.
- `name:` must match the filename stem exactly.
- Internal agent files must use the canonical pattern `internal-<agent-name>.agent.md`.
- The `description:` must explain when the agent should be selected.
- The body should define role, declared skills, routing rules, and output expectations.
- Every agent must include a `## Declared Skills` section.
- The `## Declared Skills` section is the explicit skill contract for the agent.
- List each skill by its exact canonical identifier in backticks, one per bullet.
- Do not rely on narrative references alone when an agent is expected to use a skill.
- Keep the agent focused on orchestration and decision-making. Put long reusable procedures into skills.
- Never use deprecated agent frontmatter such as `tools:`, `model:`, or `color:`.

## File structure

Use this structure:

```markdown
---
name: internal-example
description: Use this agent when ...
---

# Internal Example

## Role

You are ...

## Declared Skills

- `internal-skill-a`
- `external-skill-b`

## Routing Rules

- Use this agent when ...
- Do not use this agent when ...

## Output Expectations

- Scope or objective
- Main risks or constraints
- Recommended next action
```

Do not invent extra frontmatter or hidden runtime fields.
The `## Declared Skills` section is mandatory for repository-owned agents.

## Description design

The `description:` line is the routing contract.

- Start with `Use this agent when ...`
- Describe the situations where the command center should be selected
- Mention boundaries when ambiguity is likely
- Keep it behavioral, not language-specific, unless the agent is intentionally provider-specific

Weak descriptions describe prestige, expertise, or generic capability. Strong descriptions describe selection conditions.

## Command-Center Pattern

Use an agent when the repository benefits from a named orchestration role such as:

- CI/CD command center
- Copilot governance command center
- principal cloud strategist for a provider
- code review gate
- architecture lead

Do not create a new agent when a prompt plus a skill already gives enough routing clarity.

## Agent authoring workflow

1. Define the exact operating role and what command center problem it solves.
2. Check whether the repository already has an agent, prompt, or skill that should own the intent.
3. Pick the canonical name and file path.
4. Draft the `description:` for routing before writing the body.
5. Build a narrow declared skill list instead of a kitchen-sink list.
6. Write routing rules that make the selection boundaries obvious.
7. Validate naming, references, and overlap before finishing.

## Imported Pattern Normalization

When adapting an external or older agent-authoring pattern:

1. Preserve the useful conceptual guidance.
2. Remove runtime-specific instructions and deprecated frontmatter.
3. Rewrite the naming rules to this repository's `internal-*` contract.
4. Replace tool-specific assumptions with repo-local references and validations.
5. Drop historical context that no longer affects current routing.
6. Keep examples and templates only if they still map cleanly to GitHub Copilot behavior.

## Splitting Rule

Split an agent when one file is trying to do more than one of these at once:

- CI/CD delivery
- Copilot catalog governance
- architecture strategy
- implementation delivery
- provider-specific cloud strategy

Prefer two narrow command centers over one overloaded "platform" agent.

## Principal Cloud Agent Pattern

For principal cloud agents:

- start with architecture and operating-model analysis
- include bug and incident triage responsibilities
- end with tactical next steps, not just high-level advice
- combine provider knowledge with cross-cutting skills such as networking, performance, code review, and IaC

## Anti-Patterns

- Deprecated frontmatter keys
- Agents that just restate a skill body
- Runtime-specific tool instructions in repository-facing agents
- Agent bodies that only imply skill usage in prose without a `## Declared Skills` section
- Overloaded platform agents with unrelated governance and delivery duties
- Agent names that repeat `agent` in both the canonical identifier and the `.agent.md` suffix
- Bodies that never explain when not to use the agent
- Command centers that own both catalog governance and unrelated delivery work

## Validation

- Confirm the agent filename stem, frontmatter `name:`, and command identifier are identical.
- Confirm the `description:` says when to use the agent instead of restating its workflow.
- Confirm the agent includes `## Declared Skills` and that the list matches the intended reusable procedures.
- Confirm reusable procedures live in skills, not in the agent body.
- Confirm the new or changed agent does not make an existing agent redundant.
- Run `python3 .github/scripts/validate-copilot-customizations.sh --scope root --mode strict` after changes that affect agent naming or inventory.
