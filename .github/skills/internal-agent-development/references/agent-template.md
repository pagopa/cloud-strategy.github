# Internal Agent Template

Use this template when creating a new repository-owned internal agent.

```markdown
---
name: internal-example
description: Use this agent when the repository needs ...
---

# Internal Example

## Role

You are the command center for ...

## Declared Skills

- `internal-skill-a`
- `external-skill-b`

## Routing Rules

- Use this agent when ...
- Do not use this agent when ...
- Prefer a different specialist when responsibilities become disjoint or the routing boundary no longer matches.

## Output Expectations

- Objective or scope
- Main risks or tradeoffs
- Recommended next action
```

Keep the agent body concise. Move reusable procedures into skills.
