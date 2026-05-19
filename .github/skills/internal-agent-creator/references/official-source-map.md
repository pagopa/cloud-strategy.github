# Official Source Map

Use this reference only when a platform claim, current best practice, or external
agent-authoring pattern affects the agent contract. Keep the local repository
contract in `SKILL.md` and `agent-contract.md`.

## GitHub Copilot Custom Agents

- GitHub custom agents configuration:
  `https://docs.github.com/en/copilot/reference/custom-agents-configuration`
  - Use for YAML frontmatter, `tools`, MCP namespacing, retired `infer`,
    GitHub.com support boundaries, and prompt-size limits.
- GitHub custom agents overview:
  `https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents`
  - Use for the high-level model: agent profiles are Markdown files with
    frontmatter plus behavior instructions.

## VS Code Custom Agents

- VS Code custom agents:
  `https://code.visualstudio.com/docs/copilot/customization/custom-agents`
  - Use for VS Code-only fields such as `agents`, `handoffs`, `hooks`,
    `argument-hint`, and tool availability behavior.
- VS Code subagents:
  `https://code.visualstudio.com/docs/copilot/agents/subagents`
  - Use for subagent inheritance, `user-invocable`,
    `disable-model-invocation`, `agents: []`, and nested-subagent limits.

## OpenAI Guidance

- OpenAI prompt engineering, coding section:
  `https://developers.openai.com/api/docs/guides/prompt-engineering#coding`
  - Use for role clarity, structured tool use, testing, validation, clean
    Markdown, persistence, preambles, and progress tracking.
- OpenAI Codex best practices:
  `https://developers.openai.com/codex/learn/best-practices#improve-reliability-with-testing-and-review`
  - Use for test/check/review loops and guidance placement in prompts or
    `AGENTS.md`.

## Mapping Rules

- Product behavior facts come from GitHub or VS Code docs.
- Agent execution quality guidance may use OpenAI docs when it is about
  prompts, testing, validation, tool-use transparency, or review loops.
- Bundle token discipline comes from repository validators.
- Repository policy wins over broader product capability when this repository
  deliberately chooses a narrower contract.
