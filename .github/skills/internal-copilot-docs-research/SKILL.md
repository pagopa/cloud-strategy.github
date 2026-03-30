---
name: internal-copilot-docs-research
description: Research current GitHub Copilot behavior and customization guidance using official GitHub documentation first and MCP servers or tools when available. Use when validating repository-owned Copilot agents, skills, prompts, instructions, custom agents, agent skills, or MCP integration behavior before changing `.github/` assets.
---

# Internal Copilot Docs Research

Use this skill when a repository customization decision depends on current GitHub Copilot behavior rather than repo-local convention alone.

## Purpose

This skill standardizes how to research GitHub Copilot platform behavior before changing repository-owned customization assets.

It is especially useful when the question touches:

- repository custom instructions
- path-specific instructions
- prompt files
- agent skills
- custom agents
- MCP support or MCP server behavior
- environment-specific feature support across GitHub, IDEs, and Copilot CLI

## Core repository inputs

Read the local contract before deciding that the platform should change the repo:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- the relevant local agent, prompt, skill, or instruction file being changed
- `references/official-source-map.md`

## Source Priority

Use sources in this order:

1. Local repository contract for repo-specific policy and naming
2. MCP resources, templates, or tools that are actually available in the current session
3. Official GitHub documentation on `docs.github.com`
4. GitHub-owned references explicitly linked from the official docs, such as the GitHub MCP Registry, only when needed

Do not assume MCP is configured just because GitHub Copilot supports it.

## Research Workflow

1. Read the local contract first.
2. Detect live MCP capability in the current session.
3. If a relevant MCP server, tool, resource, or template is available, use it for live capability facts or server-specific behavior.
4. If no relevant MCP capability is available, state that explicitly and continue with official documentation.
5. Search `docs.github.com` for the exact GitHub Copilot surface involved.
6. Re-check feature scope, preview status, and environment differences before drawing conclusions.
7. Reconcile the platform behavior with this repository's intentionally narrower implementation contract.
8. Convert the conclusion into precise repo changes and run validation after structural edits.

## Decision Heuristics

- Use repository-wide custom instructions for simple guidance that helps across the whole repository.
- Use path-specific instructions for rules that only matter for certain file families or directories.
- Use skills for detailed, reusable task workflows that should load only when relevant.
- Use agents for recurring orchestration roles with stable routing boundaries.
- Use MCP for live tools, external context, or server-backed workflows only when the current session actually exposes the needed capability.

## Reconciliation Rule

GitHub Copilot may support broader configuration than this repository chooses to expose.

When that happens:

- treat GitHub Docs as the product-behavior source of truth
- treat the local repository files as the implementation-policy source of truth
- widen the local contract only when the user explicitly wants the repository standard changed

## Output Expectations

- Confirmed platform facts with source links
- Any MCP capability found and whether it was actually used
- Clear distinction between official behavior and repo-local policy
- Specific file updates required to align the repository
- Validation command to run after changes
