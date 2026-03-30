# Example Transformations

Use these examples as patterns, not boilerplate.

They show how to convert richer external agent ideas into repository-owned internal agents that fit the local contract.

## Example 1: Capability-Heavy External Expert to Internal Specialist

### Situation

An imported agent has:

- deprecated frontmatter such as `model:` and `tools:`
- long expertise catalogs
- broad claims about being an expert in a domain

### Keep

- the distinct domain
- the decisions the agent should own
- the output shape users expect

### Rewrite

- make `description:` say when the route wins
- move capability lists into `## Declared Skills`
- turn expertise bullets into routing priorities or output expectations
- drop platform-specific tool wiring

### Internal Pattern

```markdown
---
name: internal-example-domain
description: Use this agent when the repository needs domain-specific strategy, tradeoff analysis, and tactical next steps for ...
---

# Internal Example Domain

## Role

You are the specialist command center for ...

## Declared Skills

- `internal-domain-skill`
- `internal-cross-cutting-skill`

## Routing Rules

- Use this agent when ...
- Do not use this agent when implementation delivery is the main task.

## Output Expectations

- Decision frame
- Main tradeoffs
- Top risks
- Recommended next action
```

## Example 2: Workflow-Heavy Scaffold Agent to Internal Control Center

### Situation

An imported agent is organized around commands such as bootstrap, validate, migrate, or sync.

### Keep

- the ordered workflow
- the governing rules
- the checkpoints that protect correctness

### Rewrite

- keep one command-center role
- use `## Core Rules` for policy guardrails
- use `## Skill Usage Contract` only when declared skills are conditional
- rewrite slash commands into repo-local execution steps

### Internal Pattern

```markdown
---
name: internal-example-control-center
description: Use this agent when the repository needs ...
---

# Internal Example Control Center

## Role

You are the command center for ...

## Declared Skills

- `internal-audit-skill`
- `internal-authoring-skill`

## Core Rules

- Treat ... as canonical.
- Do not preserve fallback variants.

## Skill Usage Contract

- `internal-audit-skill`: Use when ...
- `internal-authoring-skill`: Use when ...

## Routing Rules

- Use this agent when ...
- Do not use this agent when one-resource authoring is enough.

## Execution Workflow

1. Inspect current state.
2. Classify findings.
3. Apply the canonical change.
4. Validate and report drift.

## Output Expectations

- Objective
- Findings or decisions
- Changes applied or recommended
- Validation status
```

## Example 3: Governance Reviewer to Agent-plus-Skill Split

### Situation

An imported agent is mostly made of checklists, policy rules, and enforcement steps.

### Decision

Keep a short agent only if named routing matters. Move the detailed review procedure into a skill when another agent could reuse it.

### Split Pattern

Agent owns:

- when the governance route wins
- which reusable skills it depends on
- how findings should be reported

Skill owns:

- detailed checks
- policy matrices
- step-by-step review workflow
- validation rules

### Smell

If the agent body reads like a long handbook, it is probably a skill pretending to be an agent.
