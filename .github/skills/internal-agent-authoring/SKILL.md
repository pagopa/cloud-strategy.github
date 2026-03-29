---
name: internal-agent-authoring
description: Create or refine repository-owned Copilot agents with focused routing, concise system prompts, and command-center responsibilities. Use when adding a new `.github/agents/*.agent.md`, splitting broad agents, or replacing runtime-specific agent-authoring guidance with Copilot-safe patterns.
---

# Internal Agent Authoring

Use this skill when designing or updating repository-owned agents.

## Purpose

This is the repository-owned replacement for Claude-only agent-authoring guidance. It defines how to build command-center agents for GitHub Copilot without deprecated frontmatter or runtime-specific assumptions.

## Agent Design Rules

- Frontmatter must contain `name:` and `description:` only.
- `name:` must match the filename stem exactly.
- The `description:` must explain when the agent should be selected.
- The body should define role, routing rules, skill composition, and output expectations.
- Keep the agent focused on orchestration and decision-making. Put long reusable procedures into skills.

## Command-Center Pattern

Use an agent when the repository benefits from a named orchestration role such as:

- CI/CD command center
- Copilot governance command center
- principal cloud strategist for a provider
- code review gate
- architecture lead

Do not create a new agent when a prompt plus a skill already gives enough routing clarity.

## Authoring Workflow

1. Define the exact operating role.
2. List the skills and prompts the agent should combine.
3. Separate strategic duties from tactical duties.
4. State routing boundaries: when to use it and when not to use it.
5. Keep repository-facing wording in English and GitHub Copilot terminology.

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
- Overloaded platform agents with unrelated governance and delivery duties
