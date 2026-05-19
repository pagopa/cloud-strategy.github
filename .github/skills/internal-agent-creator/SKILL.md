---
name: internal-agent-creator
description: Use when creating or materially revising a repository-owned Copilot agent under `.github/agents/`, or when deciding whether behavior belongs in an agent, skill, prompt, or instruction.
metadata:
  short-description: Create, refine, or realign repository-owned Copilot agents
---

# Internal Agent Creator

## Referenced skills

This index lists every other skill that this file asks the agent to load, route to, compare against, or delegate to.

- `internal-skill-creator`: repository-owned skill authoring route when the main output is a skill.
- `openai-skill-creator`: bundle anatomy and structural validation after local skill boundaries are clear.
- `local-agent-sync-external-resources`: sync-managed catalog governance when the decision is keep, refresh, replace, or retire across managed assets.
- `internal-copilot-docs-research`: current GitHub Copilot or VS Code platform behavior verification.

Use this skill when authoring or materially revising repository-owned agents in `.github/agents/`.

Use `internal-skill-creator` first when the main output is a repository-owned skill under `.github/skills/`. It is the canonical local entrypoint for that work and should handle the repo-local decision gate itself. After that gate is clear, delegate only the remaining bundle anatomy, helper-script, `agents/openai.yaml`, or structural-validation work to `openai-skill-creator` instead of duplicating it. Use `local-agent-sync-external-resources` when deciding keep, refresh, replace, or retire outcomes across the sync-managed catalog rather than improving one agent.

Prefer a singular core-skill architecture for routers and broader command centers:

- keep routing contract, tool contract, positive boundaries, and output shape in the agent
- move reusable boundary-recommendation protocols, long decision matrices, threshold rules, ownership maps, and shared operating logic into one repo-owned core skill when the agent depends on that behavior
- when no one skill is core to the agent, do not add skill-list sections by default
- mention extra support skills only when the user explicitly asks or a durable local contract justifies the exception

## When to use

- Create or materially revise a repository-owned agent under `.github/agents/`.
- Decide whether a repository-owned behavior belongs in an agent, skill, prompt, or instruction.
- Normalize an imported or legacy agent into the repository-owned internal contract.

## Goals

- Build agents that are easy to route to.
- Keep one cohesive operating role per agent.
- Translate imported agent value into repo-local GitHub Copilot form.
- Move reusable procedures into skills instead of bloating agent bodies.
- Keep paired agent, skill, and reference bundles coherent by assigning one owner per detail layer instead of letting the same subtopic drift across files.
- Prefer zero skill references or one explicit core skill, and make delegation-completion, degraded-mode, and anti-stall behavior explicit for routers and coordinator-style agents.
- Keep any skill guidance explicit and reviewable when it adds value, without implying platform-enforced execution order or a hidden multi-skill toolchain.
- Preserve evidence-first guidance patterns for fast-moving vendor or platform domains without cargo-culting obsolete tool wiring.
- Use current GitHub Copilot custom-agent frontmatter deliberately instead of stripping supported properties by default.
- Make approval boundaries, auditability, and dangerous-operation gates explicit when an agent or nearby workflow needs them.

## Read First

Load these inputs before finalizing an internal agent:

- `AGENTS.md` for routing language and repository precedence
- `.github/INVENTORY.md` for the live catalog of managed assets
- `.github/copilot-instructions.md` for the non-negotiable behavior layer
- `references/agent-contract.md` when editing frontmatter, `tools:`, core-skill sections, or subagent controls
- `references/agent-template.md` when drafting a new agent from scratch
- `references/conversion-checklist.md` when normalizing an imported or legacy agent
- `references/design-patterns.md` when broadening, splitting, or strengthening an agent
- `references/example-transformations.md` when you need before-and-after conversion examples
- `references/official-source-map.md` when platform or OpenAI guidance affects the authoring rule
- `references/review-checklist.md` before final validation or when reviewing an existing agent
- `references/subagent-patterns.md` when the agent needs to invoke or be invoked as a subagent, or when designing coordinator/worker workflows
- `internal-copilot-docs-research` when the change depends on current GitHub Copilot or VS Code platform behavior

Use `scripts/audit_agent_contract.py` before material agent authoring or review when the existing `.github/agents` catalog should be used as a benchmark. Use `scripts/measure_skill_bundle_tokens.py` after material edits to this skill bundle so code and loaded-context token costs stay visible.

When the source agent already has legacy skill-guidance sections such as `## Mandatory Engine Skills`, `## Optional Support Skills`, or `## Preferred/Optional Skills`, treat them as benchmark evidence and migration input. Do not copy those sections into a new agent unless the user explicitly asks for a legacy-compatible edit.

When the target agent depends on a paired skill or local references for detailed workflow, load those assets before editing so route, reusable procedure, and deep reference detail stay aligned instead of drifting in parallel.

## Decision Gate

Pick the right artifact before drafting:

| Need | Prefer |
| --- | --- |
| Named operating role with routing responsibility | Agent |
| Front-door router or broad command center with reusable decision logic | Agent + one core skill |
| Reusable procedure, checklist, or domain workflow | Skill |
| Short repeatable drafting aid | Prompt |
| File-type or stack-wide coding rule | Instruction |

Choose an agent only when the repository benefits from a stable command center or specialist persona. If the draft is mostly procedure, move the procedure into a skill and keep the agent short.

## Agent Contract

Read `references/agent-contract.md` before changing frontmatter, tool scope, core-skill sections, or subagent controls.

Keep these rules visible while drafting:

- Internal agents keep filename stem, frontmatter `name:`, and command identifier aligned.
- `description:` is the route and should start with `Use this agent when ...`.
- Internal agents declare `tools:` explicitly with a short, role-shaped contract.
- Use `## Core Skill` only when exactly one skill is required for the agent's core behavior.
- If an agent has no core skill, omit skill-list sections.
- Do not add `## Optional Support Skills` or `## Mandatory Engine Skills` to new agents by default.
- When a paired skill or reference is the detailed contract owner, keep the agent boundary-focused and do not re-list the same operational subtopics.
- Keep delegation controls explicit with `agents:`, `user-invocable`, and `disable-model-invocation` only when they materially enforce the boundary.
- Keep long procedures in skills, not in the agent body.

## Platform Verification Gate

Before changing claims about frontmatter support, tool aliases, MCP behavior, or subagent invocation:

- load `internal-copilot-docs-research` to identify the authoritative source map
- verify the authoritative documentation for the exact surface involved
- mark the claim as unverified if the docs are unreachable

## Core-Skill Pattern

Use this split when authoring command-center agents: keep route, stance,
tool contract, boundaries, and output expectations in the agent; keep shared
decision matrices, threshold rules, owner maps, degraded-mode behavior, and
long procedures in one core skill. Front-door routers and planning leaders are
good candidates. Small executors and lightweight challengers often need no
core skill.

## Authoring Workflow

1. Define the operating role in one sentence.
   Use behavioral scope, not prestige language.
2. Scan neighboring agents and trigger overlap.
   Compare `description:` lines first and resolve collisions before drafting.
3. Decide whether the behavior belongs in an agent, a skill, or both.
   Extract reusable procedure into a skill if the draft starts becoming a playbook.
4. If the behavior belongs in both, define the split explicitly.
   Keep route, stance, tool contract, and output shape in the agent; keep reusable procedure in the skill; keep deep tables, templates, and long checklists in references.
5. Draft the `description:` before the body.
   If the routing sentence is vague, the rest of the agent will stay vague.
6. Choose the frontmatter and core-skill strategy intentionally.
   Keep `tools:` explicit, core skills rare, and support-skill references out of the agent unless explicitly requested.
7. Normalize imported patterns and remove stale baggage.
   Preserve the decision model while deleting obsolete runtime-specific scaffolding.
8. Add real boundaries and measurable output expectations.
   Non-router agents recommend the better owner when the boundary breaks instead of routing automatically.
9. Validate, de-duplicate, and re-check paired assets.
   Run repository validation and re-check whether the new agent makes another one redundant or leaves the paired bundle out of sync.

## Capability Translation Rules

When learning from richer upstream agents, keep the signal and drop the
scaffolding. Translate tool catalogs to short canonical `tools:` lists,
expertise catalogs to route or output rules, governance patterns to approval
boundaries, and helper-skill lists to zero skill references or one core skill.
Use `references/design-patterns.md` for the detailed translation map.

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

## Imported Pattern Normalization

When adapting external agents:

1. Keep the useful mental model or decision sequence.
2. Delete stale runtime-specific frontmatter and copied tool catalog details that do not belong in the internal contract.
3. Rewrite naming into the canonical `internal-*` contract.
4. Replace platform assumptions with repo-local files, skills, and validations.
5. Convert broad expertise claims into concrete routing or output rules.

Do not over-compress a well-structured upstream agent. If its strength comes from a clear requirement gate, decision lens, execution order, or response structure, preserve those patterns in repo-local form instead of reducing everything to flat bullets.

Load `references/design-patterns.md` for command-center structure questions and `references/example-transformations.md` for side-by-side conversion examples.

## Anti-Patterns

- Prestige-first descriptions that never say when the agent wins routing.
- Imported agents copied with stale frontmatter, obsolete tool ids, or UI-only scaffolding.
- A skill-list section as a dumping ground for unrelated capabilities.
- A `## Core Skill` section with more than one skill.
- New `## Mandatory Engine Skills`, `## Optional Support Skills`, or `## Preferred/Optional Skills` sections without explicit legacy-compatibility scope.
- Routers or coordinators that classify only and do not produce a delegated result or blocking explanation.
- Agent bodies that hide constraints in long narrative prose or duplicate paired skill detail.

## Validation

- Run `scripts/audit_agent_contract.py --root .` when comparing against the live agent catalog.
- Run `scripts/measure_skill_bundle_tokens.py --skill-dir .github/skills/internal-agent-creator` after editing this bundle.
- Confirm name, route, `tools:`, subagent controls, and output expectations with `references/review-checklist.md`.
- Confirm `## Core Skill`, when present, has exactly one existing skill; otherwise confirm no skill-list section exists.
- Confirm new agents do not introduce legacy skill headings unless the user explicitly requested legacy compatibility.
- Confirm paired skills and references stay aligned, and run the closest repository validation after changes that affect agent naming or inventory.
