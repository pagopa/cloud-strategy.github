# Agent Review Checklist

Use this checklist before finalizing a new or revised internal agent.

## Route Clarity

- Does `description:` start with `Use this agent when ...`?
- Could a reader tell when this agent wins over neighboring agents?
- Does the agent include at least one real negative boundary?
- If the agent is a direct owner rather than a coordinator, does it avoid active delegation and recommend the next owner instead?
- Is the route behavioral rather than prestige-based?
- If the agent works in a fast-moving vendor domain, does the route make current-documentation verification visible?

## Cohesion

- Does the agent own one operating role?
- Would the same user expect one consistent style of output from every task routed here?
- Are unrelated responsibilities forcing `and/or` language into the route?
- Does any large procedure make the edit out of scope for an agent-only workflow?

## Requirements and Operating Stance

- Was the requirements gate proportional to the ambiguity and risk?
- Does the role describe observable behavior instead of a prestige biography?
- Are expertise and personality statements limited to behavior that changes the result?
- Are approval, stopping, and validation boundaries explicit where needed?
- For a new agent, was the canonical name validated and the resolved target kept under `.github/agents/`?

## Core Skill Section Contract

- Are the skill identifiers exact and canonical?
- Does `## Core Skill`, when present, list exactly one skill?
- Does the core skill own required reusable logic rather than decorative symmetry?
- If there is no core skill, are skill-list sections absent?
- Are legacy sections such as `## Mandatory Engine Skills`, `## Optional Support Skills`, and `## Preferred/Optional Skills` absent unless the user explicitly asked for legacy compatibility?
- Does the agent avoid `## Skill Usage Contract` unless a user-approved exception requires durable multi-skill guidance?
- If the agent cites an existing core skill or reference, does the agent stay summary-level instead of repeating the same subtopic inventory?

## Output Contract

- Does `## Output Expectations` make success observable?
- Are the expected outputs specific to the role?
- Would a reviewer know what is missing from a weak response?
- For architecture specialists, do outputs make requirement gaps, tradeoffs, or evidence-backed facts visible?

## Imported Pattern Normalization

- Have retired frontmatter keys such as `infer:` and `color:` been removed?
- Does the repository-owned internal agent declare `tools:` explicitly?
- If the agent declares `tools:`, does it use canonical aliases or explicit MCP namespaces?
- Is the `tools:` list role-shaped rather than an implicit or copied all-tools contract?
- Have broad expertise claims been translated into routing or output rules?
- Has UI-only or platform-only content been deleted?
- Is the converted content now repo-local and reusable?

## Subagent and Orchestration

- If the agent dispatches to subagents, does it declare `agents:` with an explicit target list instead of relying on the default `*`?
- If the agent must not dispatch, does it declare `agents: []`?
- If the agent should only be invoked as a subagent, is `user-invocable: false` set?
- If the agent should never be invoked as a subagent, is `disable-model-invocation: true` set?
- If `agents:` is present, is `agent` included in `tools:`?
- Are `handoffs` used only for user-visible sequential transitions, not for autonomous within-turn delegation?
- Has `references/subagent-patterns.md` been consulted for orchestration design?
- Does each coordinator-to-worker context handoff include objective, bounded evidence, constraints, expected output, and validation?
- Does the handoff avoid assuming that the worker can see the parent conversation?

## Platform Verification

- Has the agent author verified frontmatter properties against the live official documentation before making platform-behavior claims?
- If a new or unfamiliar frontmatter property is used, has `internal-copilot-docs-research` been loaded and its source map consulted?
- Are any unverified platform-behavior claims explicitly marked as unverified?

## Final Validation

- Does the filename stem match frontmatter `name:`?
- Do all referenced local files exist?
- Were directly referenced core skills and local docs checked for drift?
- Does the agent avoid making a neighboring agent redundant?
- Have the repository validation entrypoints that currently exist been run, or has the validation gap been called out explicitly?

## Red Flags

Refactor before finishing when several of these are true:

- the agent sounds like "expert at everything in X"
- the body is mostly a long checklist
- the declared skill list spans unrelated domains
- the route still collides with an existing internal agent
- the output expectations could fit almost any agent in the repository
