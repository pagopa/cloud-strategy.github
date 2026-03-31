# Internal Agent Templates

Use the smallest template that matches the job. Keep the body concise and move reusable procedures into skills.

## 1. Specialist Agent

Use this when the agent owns one clear specialist role.

```markdown
---
name: internal-example
description: Use this agent when the repository needs ...
---

# Internal Example


## Routing Rules

- Use this agent when ...
- Do not use this agent when ...
- Prefer `internal-other-agent` when ...

## Output Expectations

- Objective or scope
- Main risks or tradeoffs
- Recommended next action
```

## 2. Command-Center Agent

Use this when the agent governs a broader recurring workflow and its declared skills are conditional.

```markdown
---
name: internal-example-control-center
description: Use this agent when the repository needs ...
---

# Internal Example Control Center

## Role

## Core Rules

- Keep ...
- Do not ...
- Treat ... as canonical

## Skill Usage Contract

- `internal-skill-a`: Use when ...
- `internal-skill-b`: Use when ...

## Routing Rules

- Use this agent when ...
- Do not use this agent when ...
- Escalate to `internal-other-agent` when ...

## Execution Workflow

1. Inspect ...
2. Decide ...
3. Apply ...
4. Validate ...

## Output Expectations

- Objective or decision
- Key findings or risks
- Change or recommendation
- Validation status
```

## Notes

- `## Skill Usage Contract` is optional. Add it only when the agent owns conditional use of multiple declared skills.
- `## Core Rules` is optional. Add it when the agent governs policy, scope, or sync behavior.
- Repository-owned internal agents should declare `tools:` explicitly. Prefer canonical aliases such as `read`, `edit`, `search`, `execute`, `agent`, and `web`.
- Keep `tools:` short and role-shaped instead of copying long product-specific tool catalogs.
- If you can remove a section without losing routing clarity, remove it.
- `description:` should describe selection conditions, not prestige or generic expertise.
