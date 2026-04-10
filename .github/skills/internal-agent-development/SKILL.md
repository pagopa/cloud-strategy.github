---
name: internal-agent-development
description: Create, refine, split, or realign repository-owned Copilot agents with clear routing, deliberate tool contracts, mandatory engine skills where justified, optional support skills, reusable command-center patterns, and repo-local normalization of imported agent ideas. Use when adding or updating a `.github/agents/*.agent.md`, strengthening an agent's operating model, or deciding whether broad behavior belongs in an agent, skill, prompt, or instruction.
---

# Internal Agent Development

Use this skill when authoring or materially revising repository-owned agents in `.github/agents/`.

Use `openai-skill-creator` when the main output is a skill. Use `internal-skill-management` when deciding keep, refresh, replace, or retire outcomes across the catalog rather than improving one agent.

Prefer explicit engine-skill architecture for routers and broader command centers:

- keep routing contract, tool contract, boundaries, boundary recommendations, and output shape in the agent
- move long decision matrices, threshold rules, ownership maps, and reusable operating logic into repo-owned engine skills
- when that engine is required for the agent's core behavior, declare it explicitly instead of burying it in optional skill guidance

## Goals

- Build agents that are easy to route to.
- Keep one cohesive operating role per agent.
- Translate imported agent value into repo-local GitHub Copilot form.
- Move reusable procedures into skills instead of bloating agent bodies.
- Prefer explicit mandatory engine skills when an agent depends on reusable routing or decision logic.
- Keep any skill guidance explicit and reviewable when it adds value, without implying platform-enforced execution order.
- Preserve evidence-first guidance patterns for fast-moving vendor or platform domains without cargo-culting obsolete tool wiring.
- Use current GitHub Copilot custom-agent frontmatter deliberately instead of stripping supported properties by default.
- Make approval boundaries, auditability, and dangerous-operation gates explicit when an agent or nearby workflow needs them.

## Read First

Load these inputs before finalizing an internal agent:

- `AGENTS.md` for routing language and repository precedence
- `.github/INVENTORY.md` for the live catalog of managed assets
- `.github/copilot-instructions.md` for the non-negotiable behavior layer
- `references/agent-template.md` when drafting a new agent from scratch
- `references/conversion-checklist.md` when normalizing an imported or legacy agent
- `references/design-patterns.md` when broadening, splitting, or strengthening an agent
- `references/example-transformations.md` when you need before-and-after conversion examples
- `references/review-checklist.md` before final validation or when reviewing an existing agent

If the work is being routed through an existing agent and that agent includes a skill-guidance section such as `## Optional Support Skills` or `## Preferred/Optional Skills`, load the skill files that are directly relevant to the task before editing any target agent. Treat those lists as curated routing hints shaped by the repository layered contract, not as a platform-enforced requirement to use every listed skill.

Prefer role-based matching over identifier memorization:

- When the selected agent includes a skill-guidance section and is being used to create, revise, split, or normalize agents, load the listed skill that best governs agent authoring for the task before drafting or editing the target agent.
- When the selected agent includes a research or documentation-verification skill and the task depends on current vendor guidance, load that skill before finalizing routing or domain claims.
- When multiple listed skills are present, select according to the declared layered contract: `obra-*` for strategic framing, `internal-*` for repository-owned tactical ownership, and imported skills for support-only depth. If no internal owner exists for a capability, imported specialists may be used directly.

## Decision Gate

Pick the right artifact before drafting:

| Need | Prefer |
| --- | --- |
| Named operating role with routing responsibility | Agent |
| Front-door router or broad command center with reusable decision logic | Agent + mandatory engine skill |
| Reusable procedure, checklist, or domain workflow | Skill |
| Short repeatable drafting aid | Prompt |
| File-type or stack-wide coding rule | Instruction |

Choose an agent only when the repository benefits from a stable command center or specialist persona. If the draft is mostly procedure, move the procedure into a skill and keep the agent short.

## Non-Negotiable Agent Contract

- GitHub Copilot custom agents currently support `name`, `description`, `target`, `tools`, `model`, `disable-model-invocation`, `user-invocable`, `mcp-servers`, and `metadata` in frontmatter.
- Repository-owned internal agents must have a `name:` that matches the filename stem exactly.
- Repository-owned agents that are intentionally non-internal may use a different `name:` when their route, origin, or compatibility contract requires it.
- Repository-owned internal agents must use the canonical pattern `internal-<agent-name>.agent.md`.
- `description:` is the routing contract and should start with `Use this agent when ...`.
- Keep `name:` and `description:` in every repository-owned internal agent even though GitHub Copilot treats `name:` as optional.
- Repository-owned internal agents must declare `tools:` explicitly. Do not rely on GitHub Copilot's implicit all-tools behavior for internal agents in this repository.
- Add other optional frontmatter only when it materially changes environment behavior, selection behavior, or execution model.
- When `tools:` is present, prefer canonical aliases such as `read`, `edit`, `search`, `execute`, `agent`, and `web`, plus explicit MCP namespaces such as `github/*`, `playwright/*`, `server/tool`, or `server/*`.
- Keep `tools:` short and role-shaped. Prefer one deliberate contract per agent family instead of copied kitchen-sink catalogs.
- Do not cargo-cult legacy product-specific tool ids such as `terminalCommand`, `search/codebase`, `search/searchResults`, `search/usages`, `edit/editFiles`, `execute/runInTerminal`, `web/fetch`, or `read/problems` into repository-owned internal agents.
- Use `target:` only when the agent should behave differently between GitHub Copilot on GitHub.com and IDE environments.
- Use `mcp-servers:` only when the agent truly needs agent-local MCP server configuration; do not add it as decoration.
- Prefer `disable-model-invocation` and `user-invocable` over the retired `infer:` property.
- Never use `color:`.
- When an internal agent depends on one or more repo-owned skills as its required operating engine, add a dedicated `## Mandatory Engine Skills` section.
- `## Mandatory Engine Skills` is a repository-owned contract for the skill or skills that must be loaded before the agent's core routing or decision logic runs.
- Keep `## Mandatory Engine Skills` short and role-defining. One shared engine or one shared plus one existing tactical engine is normal; kitchen-sink engine lists are not.
- Skill-guidance sections such as `## Optional Support Skills` are optional. Use them only when they materially improve routing clarity, discovery, or command-center usability.
- Prefer `## Optional Support Skills` as the canonical heading for conditional support skills. Keep `## Preferred/Optional Skills` only for legacy agent contracts that have not yet been migrated.
- Use `## Optional Support Skills` only for conditional support skills, not for the agent's required engine.
- When present, a skill-list section is a curated routing and discovery list. List exact canonical skill identifiers, one per bullet, in backticks.
- Do not present a skill-list section as a native GitHub Copilot agent property or as a guarantee that every listed skill will be invoked automatically.
- When a skill-list section expresses the repository layered model, make `obra-*` the strategic lane, `internal-*` the tactical owner, and imported skills the support-only lane. If no internal owner exists for a capability, it is valid to use imported specialists directly.
- Do not create a 1:1 dedicated skill per agent just for symmetry. Create an engine skill only when it owns real reusable logic that would otherwise bloat the agent or drift across multiple agents.
- Router agents are the strongest default candidate for a dedicated engine skill because their classification matrix, fallback rules, and old-to-new ownership mapping are procedural, reusable, and easy to let drift.
- Only router agents should own active delegation logic. Canonical non-router agents should define boundaries and recommend a better owner to the user instead of routing on the user's behalf.
- Every agent must explain both positive routing and at least one meaningful boundary.
- Every agent must define `## Output Expectations`.
- Add `## Skill Usage Contract` only when the agent is a broader command center whose listed skills are used conditionally.
- When `## Skill Usage Contract` is present, explain selection criteria and boundaries, not a blanket execution order.
- When an agent can influence external actions, call out where human approval or review gates apply.
- Keep long reusable workflows in skills, not in the agent body.
- Do not depend on `argument-hint` or `handoffs` for GitHub.com compatibility; those properties are ignored there.

## Engine-Skill Pattern

Use this split when authoring command-center agents:

- Agent body:
  - routing sentence
  - role and stance
  - boundary with neighboring agents
  - tool contract
  - boundary definition and user-facing recommendation pattern
  - output expectations
- Engine skill:
  - decision matrix
  - threshold rules for medium or ambiguous tasks
  - old-to-new ownership mapping
  - anti-overlap checklist
  - shared workflow steps that would otherwise be duplicated

Good candidates for a dedicated or shared engine skill:

- front-door routers
- planning leaders
- any command center whose main value is ordered classification or procedural reasoning

Weak candidates for a dedicated engine skill:

- small local executors whose behavior is already well covered by OBRA plus domain skills
- lightweight challengers that do not yet have a real reusable framework
- agents where the proposed skill would mostly restate the agent body

An agent may legitimately use:

- no dedicated engine skill
- one shared engine skill
- one shared engine skill plus one existing tactical engine skill

That asymmetry is a feature, not a defect, when it reduces drift.

## Authoring Workflow

1. Define the operating role in one sentence.
   Use behavioral scope, not prestige language.
2. If the work is routed through an existing agent and that agent has a skill-guidance section, read it and load the skills that directly govern the task.
   Treat those skills as the best candidate inputs for the task, not as an instruction to use every listed skill.
3. Scan neighboring agents and trigger overlap.
   Compare `description:` lines first. If two descriptions trigger on the same request, resolve the overlap before drafting.
4. Decide whether the behavior belongs in an agent, a skill, or both.
   Extract reusable procedure into a skill if the draft starts becoming a playbook.
5. If the behavior belongs in both, define the split explicitly.
   Decide what stays in the agent body and what becomes the engine skill before drafting sections.
6. Decide whether the agent needs `## Mandatory Engine Skills`, `## Optional Support Skills`, or both.
   Mandatory engines own required decision logic; optional support skills add conditional help without redefining the route.
7. Draft the `description:` before the body.
   If the routing sentence is vague, the rest of the agent will stay vague.
8. Choose the frontmatter strategy intentionally.
   Define the explicit `tools:` contract first using canonical aliases and the smallest role-shaped set. Add `target:`, `mcp-servers:`, or model-selection properties only when they change real behavior.
9. Translate capabilities into repo-local building blocks.
   Map expertise claims, workflow logic, and any remaining tool dependencies into declared skills, role language, routing rules, output expectations, and a deliberate frontmatter contract.
10. If the agent needs engine skills, keep them explicit and small.
   Prefer one dedicated engine for routers and one shared engine for cross-agent operating logic before inventing parallel skill mirrors.
11. If a support-skill section will help the agent, build a cohesive one.
   Keep skills that reinforce the same operating role. Delete kitchen-sink additions and avoid ordering that implies origin-based priority.
12. Write routing rules with a real boundary.
    State when to use the agent, when not to use it, and which neighboring agent should win ambiguous cases. If the agent is not a router, recommend that neighboring owner to the user instead of actively handing off.
13. Add output expectations that match the role.
   Ask what a successful response from this command center should reliably contain.
14. Normalize imported patterns and remove stale baggage.
   Preserve the decision model; remove retired frontmatter, obsolete tool ids, irrelevant command syntax, and UI-only metadata.
15. Validate and de-duplicate.
    Run repository validation and re-check whether the new agent makes another one redundant.

## Capability Translation Rules

When learning from richer upstream agents, keep the signal and drop the scaffolding.

- Translate copied legacy tool catalogs into a short modern `tools:` contract with canonical aliases.
- Translate vendor documentation tools or MCP endpoints into docs-first routing rules, dedicated research skills, or explicit MCP namespaces only when the agent truly depends on those tools.
- Keep `tools:` explicit and least-privilege for every repository-owned internal agent.
- Translate governance or trust patterns into concrete approval rules, audit expectations, and routing boundaries instead of framework-specific policy code.
- Translate expertise lists into routing rules, role focus, or output expectations.
- Translate framework pillars or evaluation matrices into a compact but explicit decision lens. Keep the named dimensions when they help users reason, compare options, or understand tradeoffs quickly.
- Translate long clarification question banks into a compact list of critical requirements that must be confirmed before strong recommendations.
- Preserve ordered execution flow when the upstream agent is genuinely easier to use because it sequences the work well. A clear `## Execution Workflow` is often worth keeping for architecture, governance, investigation, or rollout agents.
- Translate exhaustive question banks into a few high-value discovery priorities unless the branching logic is unique and reusable.
- Translate platform-specific setup or deployment details into repo-local references only if this repository actually needs them.
- Preserve strong response organization when it improves operator usability. If an upstream agent is effective because it has a clear requirement gate, decision lens, and response structure, keep those advantages in repo-local form instead of compressing them away.
- Keep only examples that clarify routing or output shape; move broader examples into references.

## Governance And Trust Boundaries

When the agent being authored can influence risky actions:

- Separate routing scope from execution permissions.
- Prefer explicit allow, deny, or approval boundaries for destructive, privileged, or externally connected actions.
- State when auditability matters, especially for production changes, data access, credentials, or multi-agent delegation.
- Call out the neighboring command center or human review step when the agent should stop before execution.

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

Many strong command-center agents also benefit from:

- one explicit mandatory engine skill
- one non-kitchen-sink optional support section when conditional support really improves routing
- a clear split between core routing prose and reusable operating logic
- a validation rule that confirms the engine exists and is not decorative

Load `references/design-patterns.md` when deciding how much workflow, discovery, or governance logic belongs in the agent body.

## Imported Pattern Normalization

When adapting external agents:

1. Keep the useful mental model or decision sequence.
2. Delete stale runtime-specific frontmatter and copied tool catalog details that do not belong in the internal contract.
3. Rewrite naming into the canonical `internal-*` contract.
4. Replace platform assumptions with repo-local files, prompts, skills, and validations.
5. Convert broad expertise claims into concrete routing or output rules.
6. Remove historical or marketing language that does not change selection behavior.

Do not over-compress a well-structured upstream agent. If its strength comes from a clear requirement gate, decision lens, execution order, or response structure, preserve those patterns in repo-local form instead of reducing everything to flat bullets.

Load `references/example-transformations.md` if you need side-by-side conversion examples.

## Anti-Patterns

- Prestige-first descriptions that never say when the agent wins routing.
- Imported agents copied almost verbatim with stale platform-specific frontmatter or obsolete tool ids.
- A skill-list section as a dumping ground for unrelated capabilities.
- A `## Mandatory Engine Skills` section that merely mirrors the agent body without owning real reusable logic.
- Creating one dedicated skill per agent for visual symmetry even when shared or existing engines already solve the problem.
- Starting from the selected agent file alone and skipping the directly relevant optional support or preferred skills that define how that agent should be applied.
- Treating preferred or optional skills as a fake platform-enforced toolchain or as an origin-based priority ladder.
- Treating optional support skills as if they were the required engine.
- Creating a dedicated mirror skill for `internal-fast-executor` or `internal-critical-challenger` when the shared operating-model engine already carries the reusable logic.
- Preserving the route but throwing away the upstream agent's best structure, leaving a compliant internal agent that is harder to use and less decisive.
- Treating `tools:` or `model:` as deprecated in current GitHub Copilot custom agents.
- Copying multi-screen tool lists from older examples instead of normalizing them to canonical aliases and an explicit minimal contract.
- Relying on implicit all-tools access instead of declaring the internal agent's actual tool contract.
- Using retired frontmatter such as `infer:` or unsupported decoration such as `color:`.
- Agent bodies that hide important constraints in long narrative prose.
- Specialist agents that are really just long procedures and should be skills.
- Command centers that own unrelated domains because splitting was deferred.
- Output sections that say nothing measurable about a successful response.

## Validation

- Confirm the agent filename stem, frontmatter `name:`, and command identifier are identical.
- Confirm internal agents keep filename stem, frontmatter `name:`, and command identifier identical.
- Confirm any intentionally non-internal agent has an explicit reason to keep a different external-facing `name:`.
- Confirm the `description:` says when to use the agent instead of restating its workflow.
- Confirm `tools:` exists in every repository-owned internal agent.
- Confirm any explicit `tools:` list uses canonical aliases or MCP namespaces and that the scope is intentional.
- Confirm the `tools:` list is role-shaped and does not rely on implicit all-tools access.
- Confirm retired `infer:` is absent and that `disable-model-invocation` or `user-invocable` is used when selection behavior needs control.
- If the agent includes `## Mandatory Engine Skills`, confirm every listed skill exists on disk and is truly required for the agent's core behavior.
- If the agent includes `## Mandatory Engine Skills`, confirm the engine owns reusable logic that would otherwise bloat the agent or drift across multiple agents.
- Confirm `## Optional Support Skills` does not duplicate `## Mandatory Engine Skills`.
- For canonical operational agents, confirm `## Optional Support Skills` is used instead of `## Preferred/Optional Skills`.
- If the agent includes a skill-list section, confirm the list matches the intended reusable procedures.
- If the agent includes a skill-list section, confirm the wording does not imply that `internal-*` skills automatically outrank imported skills.
- Confirm any existing command-center agent used as a source or workflow anchor had its directly relevant declared skills loaded before final decisions were made.
- Confirm the agent has a meaningful routing boundary and is not just "expert at everything in X."
- Confirm routers keep classification matrices, fallback rules, and old-to-new ownership mapping in an engine skill instead of long body prose when that logic is substantial.
- Confirm routers are treated as the strongest case for a dedicated engine and that shared operational logic for the four canonical owners stays in a shared engine instead of branching into decorative mirrors.
- Confirm the final internal agent preserved the strongest usable structure from the source pattern when that structure improved requirement discovery, tradeoff analysis, or response quality.
- Confirm reusable procedures live in skills, not in the agent body.
- Confirm the new or changed agent does not make an existing agent redundant.
- Use `references/review-checklist.md` for a final pass when the change broadens scope or imports external patterns.
- Run the repository validation entrypoints that currently exist after changes that affect agent naming or inventory, and report the gap explicitly when no dedicated validator is present.
