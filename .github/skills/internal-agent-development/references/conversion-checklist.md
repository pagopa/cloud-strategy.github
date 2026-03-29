# Agent Conversion Checklist

Use this checklist when converting an upstream agent or agent-authoring pattern into a repository-owned internal agent.

1. Preserve the underlying decision model or workflow value.
2. Remove deprecated frontmatter such as `tools:`, `model:`, and `color:`.
3. Rewrite the name into the canonical internal agent contract: `internal-<name>.agent.md`.
4. Rewrite the `description:` so it explains when the internal agent should be selected.
5. Replace runtime-specific tool assumptions with repository-local files, skills, prompts, and validators.
6. Check whether the converted content belongs in an agent body or should move into an internal skill.
7. Remove weaker external aliases when the new internal agent clearly supersedes them.
