---
name: internal-agent-development
description: Create, refine, split, or realign repository-owned Copilot agents with clear routing, explicit declared-skill contracts, reusable command-center patterns, and repo-local normalization of imported agent ideas. Use when adding or updating a `.github/agents/*.agent.md`, strengthening an agent's operating model, or deciding whether broad behavior belongs in an agent, skill, prompt, or instruction.
---

# Internal Agent Development

Use this skill when authoring or materially revising repository-owned agents in `.github/agents/`.

Use `openai-skill-creator` when the main output is a skill. Use `internal-skill-management` when deciding keep, refresh, replace, or retire outcomes across the catalog rather than improving one agent.

## Goals

- Build agents that are easy to route to.
- Keep one cohesive operating role per agent.
- Translate imported agent value into repo-local GitHub Copilot form.
- Move reusable procedures into skills instead of bloating agent bodies.
- Make declared-skill contracts explicit and reviewable.
- Preserve evidence-first guidance patterns for fast-moving vendor or platform domains without copying runtime-specific tool wiring.

## Read First

Load these inputs before finalizing an internal agent:

- `AGENTS.md` for routing language and repository inventory
- `.github/copilot-instructions.md` for the non-negotiable behavior layer
- `.github/scripts/validate-copilot-customizations.sh` for canonical validation expectations
- `references/agent-template.md` when drafting a new agent from scratch
- `references/conversion-checklist.md` when normalizing an imported or legacy agent
- `references/design-patterns.md` when broadening, splitting, or strengthening an agent
- `references/example-transformations.md` when you need before-and-after conversion examples
- `references/review-checklist.md` before final validation or when reviewing an existing agent

If the work is being routed through an existing agent, load that agent's `## Declared Skills` next and open the skill files that are directly relevant to the task before editing any target agent. Do not treat declared skills as optional background context when they govern the kind of resource being changed.

Prefer role-based matching over identifier memorization:

- When the selected agent is being used to create, revise, split, or normalize agents, load the declared skill that governs agent authoring before drafting or editing the target agent.
- When the selected agent declares a research or documentation-verification skill and the task depends on current vendor guidance, load that skill before finalizing routing or domain claims.
- When multiple declared skills are present, load the ones that directly constrain the artifact being changed before treating the rest as optional supporting context.

## Decision Gate

Pick the right artifact before drafting:

| Need | Prefer |
| --- | --- |
| Named operating role with routing responsibility | Agent |
| Reusable procedure, checklist, or domain workflow | Skill |
| Short repeatable drafting aid | Prompt |
| File-type or stack-wide coding rule | Instruction |

Choose an agent only when the repository benefits from a stable command center or specialist persona. If the draft is mostly procedure, move the procedure into a skill and keep the agent short.

## Non-Negotiable Agent Contract

- Frontmatter must contain `name:` and `description:` only.
- `name:` must match the filename stem exactly.
- Repository-owned agents must use the canonical pattern `internal-<agent-name>.agent.md`.
- `description:` is the routing contract and should start with `Use this agent when ...`.
- Every agent must include `## Declared Skills`.
- `## Declared Skills` is the explicit skill contract. List exact canonical skill identifiers, one per bullet, in backticks.
- Every agent must explain both positive routing and at least one meaningful boundary.
- Every agent must define `## Output Expectations`.
- Add `## Skill Usage Contract` only when the agent is a broader command center whose declared skills are used conditionally.
- Keep long reusable workflows in skills, not in the agent body.
- Never use deprecated frontmatter such as `tools:`, `model:`, or `color:`.

## Authoring Workflow

1. Define the operating role in one sentence.
   Use behavioral scope, not prestige language.
2. If the work is routed through an existing agent, read its `## Declared Skills` and load the skills that directly govern the task.
   Treat those skills as part of the execution contract, not as optional follow-up reading.
3. Scan neighboring agents and trigger overlap.
   Compare `description:` lines first. If two descriptions trigger on the same request, resolve the overlap before drafting.
4. Decide whether the behavior belongs in an agent, a skill, or both.
   Extract reusable procedure into a skill if the draft starts becoming a playbook.
5. Draft the `description:` before the body.
   If the routing sentence is vague, the rest of the agent will stay vague.
6. Translate capabilities into repo-local building blocks.
   Map tool lists, expertise claims, and workflows into declared skills, role language, routing rules, and output expectations.
7. Build a cohesive `## Declared Skills` list.
   Keep skills that reinforce the same operating role. Delete kitchen-sink additions.
8. Write routing rules with a real boundary.
   State when to use the agent, when not to use it, and which neighboring agent should win ambiguous cases.
9. Add output expectations that match the role.
   Ask what a successful response from this command center should reliably contain.
10. Normalize imported patterns and remove runtime baggage.
   Preserve the decision model; remove platform-specific frontmatter, command syntax, and UI-only metadata.
11. Validate and de-duplicate.
    Run repository validation and re-check whether the new agent makes another one redundant.

## Capability Translation Rules

When learning from richer upstream agents, keep the signal and drop the scaffolding.

- Translate tool lists into skills or repo inputs, not frontmatter.
- Translate vendor documentation tools or MCP endpoints into docs-first routing rules or dedicated research skills, not copied tool catalogs.
- Translate expertise lists into routing rules, role focus, or output expectations.
- Translate framework pillars or evaluation matrices into a short decision lens in routing rules or output expectations.
- Translate long clarification question banks into a compact list of critical requirements that must be confirmed before strong recommendations.
- Translate multi-step workflows into a short execution order only when the agent truly orchestrates a recurring command-center flow.
- Translate exhaustive question banks into a few high-value discovery priorities unless the branching logic is unique and reusable.
- Translate platform-specific setup or deployment details into repo-local references only if this repository actually needs them.
- Keep only examples that clarify routing or output shape; move broader examples into references.

## Cohesion and Splitting

Split an agent when one file mixes disjoint operating roles, conflicting instructions, or different winning routes.

Good reasons to split:

- The same agent tries to own both governance and delivery.
- The routing sentence needs `and/or` across unrelated domains.
- The declared skills fall into separate clusters with different triggers.
- Different outcomes are expected by different users.

Do not split only because the file is long. First ask whether the reusable procedure belongs in a skill.

## Command-Center Heuristics

A strong internal agent usually has:

- a precise routing sentence
- a short role statement that defines its operating stance
- a declared skill list that matches the role
- routing boundaries against nearby agents
- output expectations that make success observable

Load `references/design-patterns.md` when deciding how much workflow, discovery, or governance logic belongs in the agent body.

## Imported Pattern Normalization

When adapting external agents:

1. Keep the useful mental model or decision sequence.
2. Delete runtime-specific frontmatter and tool catalog details.
3. Rewrite naming into the canonical `internal-*` contract.
4. Replace platform assumptions with repo-local files, prompts, skills, and validations.
5. Convert broad expertise claims into concrete routing or output rules.
6. Remove historical or marketing language that does not change selection behavior.

Load `references/example-transformations.md` if you need side-by-side conversion examples.

## Anti-Patterns

- Prestige-first descriptions that never say when the agent wins routing.
- Imported agents copied almost verbatim with platform-specific frontmatter.
- `## Declared Skills` as a dumping ground for unrelated capabilities.
- Starting from the selected agent file alone and skipping the directly relevant declared skills that define how that agent should be applied.
- Agent bodies that hide important constraints in long narrative prose.
- Specialist agents that are really just long procedures and should be skills.
- Command centers that own unrelated domains because splitting was deferred.
- Output sections that say nothing measurable about a successful response.

## Validation

- Confirm the agent filename stem, frontmatter `name:`, and command identifier are identical.
- Confirm the `description:` says when to use the agent instead of restating its workflow.
- Confirm the agent includes `## Declared Skills` and that the list matches the intended reusable procedures.
- Confirm any existing command-center agent used as a source or workflow anchor had its directly relevant declared skills loaded before final decisions were made.
- Confirm the agent has a meaningful routing boundary and is not just "expert at everything in X."
- Confirm reusable procedures live in skills, not in the agent body.
- Confirm the new or changed agent does not make an existing agent redundant.
- Use `references/review-checklist.md` for a final pass when the change broadens scope or imports external patterns.
- Run `python3 .github/scripts/validate-copilot-customizations.sh --scope root --mode strict` after changes that affect agent naming or inventory.
