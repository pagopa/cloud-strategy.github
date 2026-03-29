# Agent Conversion Checklist

Use this checklist when converting an upstream agent or agent-authoring pattern into a repository-owned internal agent.

1. Preserve the underlying decision model or workflow value.
2. Remove deprecated frontmatter such as `tools:`, `model:`, and `color:`.
3. Rewrite the name into the canonical internal agent contract: `internal-<name>.agent.md`.
4. Rewrite the `description:` so it explains when the internal agent should be selected.
5. Add a `## Declared Skills` section that lists the exact canonical skill identifiers the agent is expected to use.
6. Replace runtime-specific tool assumptions with repository-local files, skills, prompts, and validators.
7. Check whether the converted content belongs in an agent body or should move into an internal skill.
8. Remove weaker external aliases when the new internal agent clearly supersedes them.
