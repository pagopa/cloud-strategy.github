---
name: internal-agent-development
description: Create, refine, split, or realign repository-owned Copilot agents with clear routing, optional skill guidance, reusable command-center patterns, and repo-local normalization of imported agent ideas. Use when adding or updating a `.github/agents/*.agent.md`, strengthening an agent's operating model, or deciding whether broad behavior belongs in an agent, skill, prompt, or instruction.
---

# Internal Agent Development

Use this skill when authoring or materially revising repository-owned agents in `.github/agents/`.

Use `openai-skill-creator` when the main output is a skill. Use `internal-skill-management` when deciding keep, refresh, replace, or retire outcomes across the catalog rather than improving one agent.

## Goals

- Build agents that are easy to route to.
- Keep one cohesive operating role per agent.
- Translate imported agent value into repo-local GitHub Copilot form.
- Move reusable procedures into skills instead of bloating agent bodies.
- Keep any skill guidance explicit and reviewable when it adds value, without implying platform-enforced execution order.
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

If the work is being routed through an existing agent and that agent includes a skill-guidance section such as `## Preferred/Optional Skills`, load the skill files that are directly relevant to the task before editing any target agent. Treat those lists as curated routing hints for which skills may matter, not as a platform-enforced requirement to use every listed skill or to prioritize `internal-*` skills by default.

Prefer role-based matching over identifier memorization:

- When the selected agent includes a skill-guidance section and is being used to create, revise, split, or normalize agents, load the listed skill that best governs agent authoring for the task before drafting or editing the target agent.
- When the selected agent includes a research or documentation-verification skill and the task depends on current vendor guidance, load that skill before finalizing routing or domain claims.
- When multiple listed skills are present, choose the ones whose trigger most directly constrains the artifact being changed; do not infer priority from origin alone.

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
- Repository-owned internal agents must have a `name:` that matches the filename stem exactly.
- Repository-owned agents that are intentionally non-internal may use a different `name:` when their route, origin, or compatibility contract requires it.
- Repository-owned internal agents must use the canonical pattern `internal-<agent-name>.agent.md`.
- `description:` is the routing contract and should start with `Use this agent when ...`.
- Skill-guidance sections such as `## Preferred/Optional Skills` are optional. Use them only when they materially improve routing clarity, discovery, or command-center usability.
- When present, a skill-list section is a curated routing and discovery list. List exact canonical skill identifiers, one per bullet, in backticks.
- Do not present a skill-list section as a native GitHub Copilot agent property or as a guarantee that every listed skill will be invoked automatically.
- Do not imply that repository-owned `internal-*` skills outrank imported skills by default. Any prioritization must come from concrete task fit, not origin.
- Every agent must explain both positive routing and at least one meaningful boundary.
- Every agent must define `## Output Expectations`.
- Add `## Skill Usage Contract` only when the agent is a broader command center whose listed skills are used conditionally.
- When `## Skill Usage Contract` is present, explain selection criteria and boundaries, not a blanket execution order.
- Keep long reusable workflows in skills, not in the agent body.
- Never use deprecated frontmatter such as `tools:`, `model:`, or `color:`.

## Authoring Workflow

1. Define the operating role in one sentence.
   Use behavioral scope, not prestige language.
2. If the work is routed through an existing agent and that agent has a skill-guidance section, read it and load the skills that directly govern the task.
   Treat those skills as the best candidate inputs for the task, not as an instruction to use every listed skill.
3. Scan neighboring agents and trigger overlap.
   Compare `description:` lines first. If two descriptions trigger on the same request, resolve the overlap before drafting.
4. Decide whether the behavior belongs in an agent, a skill, or both.
   Extract reusable procedure into a skill if the draft starts becoming a playbook.
5. Draft the `description:` before the body.
   If the routing sentence is vague, the rest of the agent will stay vague.
6. Translate capabilities into repo-local building blocks.
   Map tool lists, expertise claims, and workflows into declared skills, role language, routing rules, and output expectations.
7. If a skill-list section will help the agent, build a cohesive one.
   Keep skills that reinforce the same operating role. Delete kitchen-sink additions and avoid ordering that implies origin-based priority.
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
- Translate framework pillars or evaluation matrices into a compact but explicit decision lens. Keep the named dimensions when they help users reason, compare options, or understand tradeoffs quickly.
- Translate long clarification question banks into a compact list of critical requirements that must be confirmed before strong recommendations.
- Preserve ordered execution flow when the upstream agent is genuinely easier to use because it sequences the work well. A clear `## Execution Workflow` is often worth keeping for architecture, governance, investigation, or rollout agents.
- Translate exhaustive question banks into a few high-value discovery priorities unless the branching logic is unique and reusable.
- Translate platform-specific setup or deployment details into repo-local references only if this repository actually needs them.
- Preserve strong response organization when it improves operator usability. If an upstream agent is effective because it has a clear requirement gate, decision lens, and response structure, keep those advantages in repo-local form instead of compressing them away.
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

Many strong specialist agents also benefit from:

- an explicit decision lens that names the evaluation dimensions
- a compact requirement gate that prevents weak assumptions
- an execution workflow when ordered reasoning materially improves answer quality
- a response shape that makes evidence, tradeoffs, and next steps easy to scan

Load `references/design-patterns.md` when deciding how much workflow, discovery, or governance logic belongs in the agent body.

## Imported Pattern Normalization

When adapting external agents:

1. Keep the useful mental model or decision sequence.
2. Delete runtime-specific frontmatter and tool catalog details.
3. Rewrite naming into the canonical `internal-*` contract.
4. Replace platform assumptions with repo-local files, prompts, skills, and validations.
5. Convert broad expertise claims into concrete routing or output rules.
6. Remove historical or marketing language that does not change selection behavior.

Do not over-compress a well-structured upstream agent. If its strength comes from a clear requirement gate, decision lens, execution order, or response structure, preserve those patterns in repo-local form instead of reducing everything to flat bullets.

Load `references/example-transformations.md` if you need side-by-side conversion examples.

## Anti-Patterns

- Prestige-first descriptions that never say when the agent wins routing.
- Imported agents copied almost verbatim with platform-specific frontmatter.
- A skill-list section as a dumping ground for unrelated capabilities.
- Starting from the selected agent file alone and skipping the directly relevant preferred or optional skills that define how that agent should be applied.
- Treating preferred or optional skills as a fake platform-enforced toolchain or as an origin-based priority ladder.
- Preserving the route but throwing away the upstream agent's best structure, leaving a compliant internal agent that is harder to use and less decisive.
- Agent bodies that hide important constraints in long narrative prose.
- Specialist agents that are really just long procedures and should be skills.
- Command centers that own unrelated domains because splitting was deferred.
- Output sections that say nothing measurable about a successful response.

## Validation

- Confirm the agent filename stem, frontmatter `name:`, and command identifier are identical.
- Confirm internal agents keep filename stem, frontmatter `name:`, and command identifier identical.
- Confirm any intentionally non-internal agent has an explicit reason to keep a different external-facing `name:`.
- Confirm the `description:` says when to use the agent instead of restating its workflow.
- If the agent includes a skill-list section, confirm the list matches the intended reusable procedures.
- If the agent includes a skill-list section, confirm the wording does not imply that `internal-*` skills automatically outrank imported skills.
- Confirm any existing command-center agent used as a source or workflow anchor had its directly relevant declared skills loaded before final decisions were made.
- Confirm the agent has a meaningful routing boundary and is not just "expert at everything in X."
- Confirm the final internal agent preserved the strongest usable structure from the source pattern when that structure improved requirement discovery, tradeoff analysis, or response quality.
- Confirm reusable procedures live in skills, not in the agent body.
- Confirm the new or changed agent does not make an existing agent redundant.
- Use `references/review-checklist.md` for a final pass when the change broadens scope or imports external patterns.
- Run `python3 .github/scripts/validate-copilot-customizations.sh --scope root --mode strict` after changes that affect agent naming or inventory.
