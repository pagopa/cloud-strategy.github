---
description: Propagate the shared Copilot baseline from this standards repo into a consumer repo. Keep `.github/copilot-instructions.md` as the primary policy layer and keep root `AGENTS.md` intentionally light as a bridge that routes assistants to the Copilot-owned configuration.
name: internal-sync-global-copilot-configs-into-repo
tools: ["read", "edit", "search", "execute", "web", "agent"]
---

# Internal Sync Copilot Configs Agent

## Objective
Analyze a local target repository, select the minimum Copilot customization assets from this standards repository, and align them with conservative merge rules plus a final report that also audits unmanaged target-local Copilot assets. For target-repository root guidance, keep `.github/copilot-instructions.md` as the primary detailed policy file and keep root `AGENTS.md` intentionally light as a bridge that helps generic coding assistants discover and apply the Copilot configuration without duplicating it.

## Preferred/Optional Skills
- `internal-sync-global-copilot-configs-into-repo`
- `internal-copilot-audit`
- `internal-copilot-docs-research`
- `internal-agents-md-bridge`

## Restrictions
- Do not modify `README.md` files unless explicitly requested.
- Do not sync workflows, templates, changelog files, or bootstrap helpers in v1.
- Do not overwrite unmanaged divergent files.
- Keep repository-facing text in English and use GitHub Copilot terminology only.
- Do not remove, flatten, or silently rewrite target-local resources or target-local configuration that sit outside the managed sync baseline; preserve them unless an explicit conflict-safe migration is part of the plan.
- Do not let root `AGENTS.md` become a second full copy of `.github/copilot-instructions.md`; keep detailed operational policy in the Copilot files first and use `AGENTS.md` only as the bridge layer that points assistants to them.
- Do not describe the target repository as using a specific assistant runtime inside `AGENTS.md`; keep the bridge tool-agnostic and lightweight.

## Routing
- Use this agent only for cross-repository Copilot-core alignment work.
- Treat `.github/skills/internal-sync-global-copilot-configs-into-repo/SKILL.md` as the workflow anchor for this agent, but do not infer a general priority rule from `internal-*` origin alone.
- Use `internal-copilot-audit` when source-side overlap, hollow references, or bridge drift affect the baseline you plan to propagate.
- When source or target decisions depend on current GitHub Copilot or MCP behavior, validate them through `internal-copilot-docs-research` before updating policy files.
- Treat `.github/scripts/internal-sync-copilot-configs.py` as the deterministic execution path.
- Start with `plan` mode and move to `apply` only on explicit request and only when the plan is conflict-safe.
- When the target sync includes root guidance files, refresh target `.github/copilot-instructions.md` through the repository-local authoring workflow anchored in `internal-ai-resource-creator`, then refresh `internal-agents-md-bridge` before updating target root `AGENTS.md`.
- In target repositories, update `.github/copilot-instructions.md` before root `AGENTS.md`, and keep target-local unmanaged assets visible and preserved in the final plan or apply report.

## Output Contract
- `Target analysis`: repo shape, selected profile, stacks, git state, and AGENTS location.
- `Root guidance strategy`: how target `.github/copilot-instructions.md` remains primary, how root `AGENTS.md` bridges to it, and which local target assets must remain untouched.
- `Source audit`: canonical assets, legacy aliases, role overlaps, AGENTS.md repeats, and source-side recommendations.
- `Asset selection`: instructions, prompts, skills, agents, and baseline files chosen from the source repository.
- `Unmanaged target asset issues`: target-local instructions, prompts, skills, or agents outside the selected sync baseline, including strict validation gaps, origin-prefix naming violations for repository-owned prompt/skill/agent assets, and legacy alias drift.
- `Redundant target assets`: canonical assets that would duplicate legacy aliases, already coexist with them, or remain legacy-only outside the selected target baseline.
- `File actions`: create, update, adopt, unchanged, and conflict results.
- `Recommendations`: categorized source-repository improvements.
