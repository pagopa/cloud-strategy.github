# Internal Agent Contract Reference

Use this reference when editing frontmatter, tool scope, core-skill sections, or subagent controls for repository-owned agents.

## Frontmatter Contract

- GitHub Copilot custom agents currently support `name`, `description`, `target`, `tools`, `model`, `disable-model-invocation`, `user-invocable`, `agents`, `handoffs`, `hooks`, `argument-hint`, `mcp-servers`, and `metadata` in frontmatter.
- `handoffs`, `hooks`, and `argument-hint` are VS Code only; GitHub.com ignores them.
- Repository-owned internal agents must keep `name:` aligned with the filename stem exactly.
- Repository-owned agents that are intentionally non-internal may keep a different `name:` only when route, origin, or compatibility requires it.
- Repository-owned internal agents must use the canonical filename pattern `internal-<agent-name>.agent.md`.
- `description:` is the routing contract and should start with `Use this agent when ...`.
- Keep `name:` and `description:` even though current GitHub Copilot treats `name:` as optional.
- Repository-owned internal agents must declare `tools:` explicitly. Do not rely on implicit all-tools access for internal agents in this repository.
- Add optional frontmatter only when it materially changes environment behavior, selection behavior, or execution model.
- When `tools:` is present, prefer canonical aliases such as `read`, `edit`, `search`, `execute`, `agent`, and `web`, plus explicit MCP namespaces such as `github/*`, `playwright/*`, `server/tool`, or `server/*`.
- Keep `tools:` short and role-shaped instead of copying kitchen-sink catalogs.
- Do not cargo-cult legacy tool ids such as `terminalCommand`, `search/codebase`, `search/searchResults`, `search/usages`, `edit/editFiles`, `execute/runInTerminal`, `web/fetch`, or `read/problems`.
- Use `target:` only when the agent should behave differently between GitHub.com and IDE environments.
- Use `mcp-servers:` only when the agent truly needs agent-local MCP server configuration.
- Prefer `disable-model-invocation` and `user-invocable` over retired `infer:`.
- Never use `color:`.
- Do not depend on `argument-hint`, `handoffs`, or `hooks` for GitHub.com compatibility.

## Core Skill Section Contract

- When an internal agent depends on one existing repo-owned skill for its required operating logic, add `## Core Skill`.
- Treat `## Core Skill` as a repository-owned contract for the one existing skill that must be loaded before the agent's core routing or decision logic runs.
- `## Core Skill` must list exactly one canonical skill identifier, one bullet, in backticks.
- If the agent has no true core skill, omit skill-list sections entirely.
- Do not introduce `## Mandatory Engine Skills`, `## Optional Support Skills`, or `## Preferred/Optional Skills` in new repository-owned agents unless the user explicitly requests a legacy-compatible edit.
- When an agent depends on an existing core skill or reference for detailed workflow, keep the agent summary-level and avoid re-listing the same operational subtopics.
- Do not present `## Core Skill` as a native GitHub Copilot property or as a guarantee that every referenced file will be invoked automatically.
- When expressing the resource model, treat `superpowers-*` as the cross-cutting workflow lane, `internal-*` as the canonical repository-owned layer, imported skills as support depth by default, and `local-*` as consumer-local extensions. Do not infer strategic, tactical, or operational role from prefix alone.
- Do not add a 1:1 dedicated skill per agent just for symmetry. Cite a core skill only when it already owns real reusable logic that would otherwise bloat the agent or drift.
- When several neighboring repository-owned agents share the same stop-and-recommend behavior, prefer one shared boundary-recommendation core skill over repeating the same next-owner matrix in every agent body. Keep the route and at least one real boundary in each agent.
- Router agents are the strongest default candidate for a core skill because their classification matrix, fallback rules, and ownership mapping are highly procedural.

## Standard Changes And Migration

- When changing an authoring standard while live agents still use the old shape, separate the new standard from migration work.
- Use existing live assets as read-only benchmark evidence unless the user explicitly authorizes migration edits.
- Start new validator checks as report-only unless the migration is in scope and current assets already satisfy the standard.
- Do not change blocking validators or retrofit all existing agents to enforce a new standard without explicit migration approval.

## Delegation And Invocation Controls

- Only dedicated coordinator or router agents should own active downstream routing logic. Canonical direct owners should recommend a better owner to the user instead of routing on the user's behalf.
- Prefer user-visible lane changes or direct user choice over hidden peer dispatch between canonical owners.
- If a narrower scoped contract allows one canonical owner to invoke another, the exception must be explicit, one-directional, auditably bounded, and must not create an all-to-all mesh or nested ping-pong.
- When an agent should dispatch to specific subagents, declare `agents:` with the explicit list of allowed targets.
- When an agent must not dispatch subagents, declare `agents: []` to enforce the recommendation-only boundary.
- When an agent should only be accessible as a subagent and not appear in the user dropdown, set `user-invocable: false`.
- When an agent should never be invoked as a subagent by other agents, set `disable-model-invocation: true`.
- Use `handoffs` only for user-visible sequential transitions, not for autonomous within-turn delegation.
- Load `references/subagent-patterns.md` when designing coordinator/worker orchestration or restricting subagent access.

## Body Contract

- Every agent must explain both positive routing and at least one meaningful boundary.
- Every agent must define `## Output Expectations`.
- Add `## Skill Usage Contract` only as an explicit exception for a broader command center where the user requested durable multi-skill guidance.
- Do not keep `## Skill Usage Contract` on a single-core-skill agent.
- When `## Skill Usage Contract` is present, explain selection criteria and boundaries, not a blanket execution order or optional-support catalog.
- If an agent points to an existing core skill or reference as the detailed contract owner, keep deep procedure, matrices, and templates out of the agent body.
- When an agent can influence external actions, call out where human approval or review gates apply.
- Keep long reusable workflows out of the agent body.

## Platform Verification Gate

- Before claiming that a frontmatter property is supported, unsupported, deprecated, or behaves in a specific way, verify against the live official documentation.
- Load `internal-copilot-docs-research` to identify the authoritative page.
- Open the authoritative page for the surface involved: VS Code custom agents, GitHub.com custom agents, or subagents.
- If the live docs contradict the current assumption, stop and tell the user what changed before proceeding.
- If the docs are unreachable, state explicitly that the platform claim is unverified and proceed with caution.
- This gate applies whenever the change depends on platform behavior: frontmatter fields, tool aliases, subagent invocation, MCP integration, or environment-specific feature support.
- This gate does not apply when the work is purely repo-local convention with no platform-behavior dependency.
