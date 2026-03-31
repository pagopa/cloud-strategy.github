# Agent Review Checklist

Use this checklist before finalizing a new or revised internal agent.

## Route Clarity

- Does `description:` start with `Use this agent when ...`?
- Could a reader tell when this agent wins over neighboring agents?
- Does the agent include at least one real negative boundary?
- Is the route behavioral rather than prestige-based?
- If the agent works in a fast-moving vendor domain, does the route make current-documentation verification visible?

## Cohesion

- Does the agent own one operating role?
- Would the same user expect one consistent style of output from every task routed here?
- Are unrelated responsibilities forcing `and/or` language into the route?
- Should any large procedure move into a skill instead?

## Skill Contract

- Are the skill identifiers exact and canonical?
- Do all declared skills reinforce the same operating role?
- Does the agent need `## Skill Usage Contract`, or would that add noise?

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

## Final Validation

- Does the filename stem match frontmatter `name:`?
- Do all referenced local files exist?
- Does the agent avoid making a neighboring agent redundant?
- Has `python3 .github/scripts/validate-copilot-customizations.py --scope root --mode strict` been run?

## Red Flags

Refactor before finishing when several of these are true:

- the agent sounds like "expert at everything in X"
- the body is mostly a long checklist
- the declared skill list spans unrelated domains
- the route still collides with an existing internal agent
- the output expectations could fit almost any agent in the repository
