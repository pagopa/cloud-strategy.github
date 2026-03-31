---
name: internal-agents-md-bridge
description: Generate or update repository-root `AGENTS.md` files as lightweight bridges to `.github/copilot-instructions.md`. Use when designing AGENTS routing, naming policy, inventory sections, or command-center guidance without exposing runtime-specific assistant details.
---

# Internal AGENTS.md Bridge

Use this skill when creating or updating a repository-root `AGENTS.md`.

## Purpose

`AGENTS.md` is not the full operating manual. In this repository model it is a thin bridge that:

- tells assistants where the real Copilot policy lives
- explains routing, naming, and discovery
- points to prompts, skills, instructions, and agents
- stays light enough to remain portable across assistant runtimes

## Core Rule

Keep `.github/copilot-instructions.md` as the primary detailed policy layer.
Keep root `AGENTS.md` short, navigational, and runtime-agnostic.
When both files change in the same workflow, finalize `.github/copilot-instructions.md` first and refresh `AGENTS.md` second.

Do not make root `AGENTS.md` say or imply that the repository uses a specific internal assistant runtime. Some consumer repositories cannot make that claim and should not encode it.

## What AGENTS.md Should Own

- Naming policy
- Decision priority
- Agent routing
- High-level repository defaults
- Discovery of `.github/instructions`, `.github/prompts`, `.github/skills`, `.github/agents`, and `.github/scripts`
- Inventory references or inventory listing

## What AGENTS.md Should Not Own

- Full implementation standards already defined in `.github/copilot-instructions.md`
- Repeated language-specific coding rules already covered by instructions
- Runtime-specific tool internals
- Large duplicated prompt or skill bodies

## Authoring Workflow

1. Read the existing root `AGENTS.md`.
2. Read `.github/copilot-instructions.md`.
3. Identify what belongs in the bridge versus the Copilot policy layer.
4. Keep only the bridge-owned content in `AGENTS.md`.
5. Ensure references to instructions, prompts, skills, agents, and scripts are correct.
6. Regenerate inventory paths if the repository keeps inline inventory.

## Bridge Style

- Prefer short sections with strong headings.
- Use repository-facing GitHub Copilot terminology only.
- Keep the file tool-agnostic: "assistants", "coding assistants", or "AI assistants" is fine.
- Explain the relationship to `.github/copilot-instructions.md` explicitly.
- Avoid long narrative prose.

## Required Bridge Statement

Make the relationship explicit in wording similar to:

- `.github/copilot-instructions.md` is the primary detailed policy file.
- Root `AGENTS.md` is the external bridge for routing, naming, and discovery.

## Inventory Guidance

If the inventory is inline:

- keep it auto-generated in structure and deterministic in ordering
- include only real paths
- do not mention assets that were deleted

If the inventory is externalized:

- keep only a short pointer in `AGENTS.md`
- validate the external inventory file in the same workflow

## Anti-Patterns

- Turning `AGENTS.md` into a second copy of `.github/copilot-instructions.md`
- Naming a specific runtime that the consumer repository does not officially declare
- Hiding command-center routing deep in the file instead of giving it a dedicated section
- Leaving stale asset paths after catalog cleanup

## Output Expectations

When updating `AGENTS.md`, ensure:

- the bridge-to-policy relationship is explicit
- the file remains lightweight
- all listed assets exist
- agent routing points only to agents that actually exist in `.github/agents/`
