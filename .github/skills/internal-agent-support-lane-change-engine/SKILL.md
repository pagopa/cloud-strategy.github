---
name: internal-agent-support-lane-change-engine
description: Use when a repository-owned internal agent needs a consistent user-visible lane-change response after the selected lane no longer fits.
---

# Internal Agent Support Lane Change Engine

Use this skill as the shared lane-mismatch engine for repository-owned internal agents that must stop, explain the mismatch, and recommend the better next option without hidden delegation.

## When to use

- A repository-owned internal agent was selected for a request it is not optimized to own.
- New information changes the winning lane after the current agent already started.
- Several related agents need the same stop-and-recommend behavior and that logic should not be duplicated in every agent body.

## Goals

- Stop before doing off-lane work.
- Explain the concrete mismatch in plain language.
- Recommend exactly one better owner when the next lane is clear.
- Fail safe to `internal-gateway-operational-flow` when more than one plausible owner remains.
- Keep the recommendation user-visible and recommendation-only.

## Shared Stop Protocol

1. State that the current lane is not the best fit.
2. Name the concrete reason the boundary broke.
3. Recommend one better owner and give one reason.
4. If the next owner is still ambiguous, recommend `internal-gateway-operational-flow` instead of offering multiple half-confident options.
5. Do not open a hidden second lane and do not continue with off-lane work.

## Recommendation Matrix

| Current agent | When the boundary breaks | Recommend |
| --- | --- | --- |
| `internal-gateway-operational-flow` | The work has become a concrete low-to-medium-risk single-lane task | `internal-gateway-simple-task` |
| `internal-gateway-operational-flow` | Assumption stress-testing becomes the main need | `internal-gateway-critical-master` |
| `internal-gateway-simple-task` | Planning, retained-plan execution, review, governance, or rollout becomes dominant | `internal-gateway-operational-flow` |
| `internal-gateway-simple-task` | Assumption stress-testing becomes the main need | `internal-gateway-critical-master` |
| `internal-gateway-critical-master` | The next step is planning, execution, apply-plan, or evidence review | `internal-gateway-operational-flow` |
| `internal-gateway-critical-master` | The critique leaves only a concrete low-to-medium-risk local task | `internal-gateway-simple-task` |
| `local-sync-external-resources` | The source-side catalog direction is still ambiguous or needs repo-owned authoring decisions first | `internal-gateway-operational-flow` |
| `local-sync-external-resources` | The real job is consumer-repository baseline propagation | `local-sync-global-copilot-configs-into-repo` |
| `local-sync-external-resources` | The work reduced to a clear local edit outside catalog-governance scope | `internal-gateway-simple-task` |
| `local-sync-global-copilot-configs-into-repo` | The real job is source-side catalog governance in this repository | `local-sync-external-resources` |
| `local-sync-global-copilot-configs-into-repo` | The request is source-side redesign, agent authoring, or governance restructuring | `internal-gateway-operational-flow` |
| `local-sync-global-copilot-configs-into-repo` | Only a clear target-local execution step remains after the sync contract is settled | `internal-gateway-simple-task` |

## Agent-Specific Notes

- `internal-gateway-critical-master` may need to ask whether the current analysis should be saved before recommending another owner.
- Repo-only sync agents may name the mode or scope mismatch before giving the shared recommendation.
- Do not recommend returning to the same agent.
- Do not recommend multiple alternatives unless the user explicitly asks for options.

## Validation

- The recommendation names an exact next owner unless ambiguity still remains.
- The response stops before off-lane execution starts.
- The mismatch reason is concrete, not prestige-based.
- The recommendation stays user-visible and does not rely on hidden agent dispatch.
