---
name: internal-azure
description: Use when an Azure task cannot be routed confidently to a specific Azure skill because the request is materially ambiguous, has multiple Azure domains with no clear primary owner, or requires clarification before selecting the correct specialist, or when the user needs high-level Azure platform decision support or tradeoff framing before implementation. Do not use for clearly scoped organization structure, governance or identity, operations or validation, or Azure DevOps pipeline tasks.
---

# Internal Azure

## Referenced skills

- `internal-azure-organization-structure`: tenant, management-group, subscription, landing-zone, and platform-topology owner.
- `internal-azure-governance`: RBAC, managed identity, PIM, Policy, tagging, and guardrail owner.
- `internal-azure-operations`: monitoring, validation, backup, Site Recovery, reporting, and evidence owner.
- `internal-azure-devops`: Azure DevOps pipeline and project-automation owner.
- `awesome-copilot-azure-pricing`: Azure-specific pricing depth when cost data is the primary problem.

Fallback router for Azure tasks that cannot be assigned confidently to one specialist, and strategic support skill for high-level Azure decision framing. Do not activate only because the task concerns Azure; activate only when material routing uncertainty blocks owner selection or when the user needs decision support before the next step is structure, governance, operations, or delivery. Do not activate when one specialist clearly owns the next step.

## When to use

- Use this fallback when material ambiguity prevents selecting one primary Azure specialist.
- Use it when multiple Azure domains are material and no primary owner can be identified safely.
- Use it when the user explicitly invokes `$internal-azure`.
- Use it when the user needs high-level Azure decision support or tradeoff framing before implementation.

## When not to use

- The task is already a clear implementation change.
- The user only needs detailed RBAC, Policy, monitoring, backup, or pipeline implementation detail.
- The task is purely post-rollout validation or evidence gathering.
- The request is narrow and operational with no real decision to frame.

## Routing threshold

Activate only when at least one condition holds:

- the request is materially ambiguous and clarification is required before an Azure owner can be selected;
- multiple Azure domains are material and no primary owner can be identified safely;
- the task asks which Azure problem-solving lane should own the work before requesting a domain solution;
- the user needs strategic decision framing and the next step is not yet structure, governance, operations, or delivery.

Explicit `$internal-azure` invocation remains valid.

## Dispatch contract

1. State the routing uncertainty.
2. Identify the candidate Azure owners.
3. Select the minimum specialist set.
4. Keep strategic comparison here only while it is needed to choose the owner.
5. Hand the resolved task to the primary specialist instead of retaining ownership.

## Optional lens activation

Do not load every lens by default.

Use only the minimum set of lenses needed for the request. If the user explicitly names one or more lenses, prioritize only those. If the user does not name lenses, infer the smallest useful set.

Available lenses include:

- security
- identity and access
- organization-structure
- governance
- operations
- monitoring and observability
- BC/DR
- FinOps
- compliance
- rollout and rollback
- blast radius
- maintainability

Rules:

- Start narrow.
- Expand only when the request is broad, risky, or ambiguous.
- If another lens would materially improve the recommendation, suggest it briefly instead of forcing it.
- Keep the active lenses explicit when more than one is in play.

Load `references/lens-playbook.md` when the user wants a deeper framing aid or when the choice of lenses is not obvious.

## Optional BC/DR lens

BC/DR is optional.

Activate it only when:

- the user asks about resilience, backup, recovery, failover, RTO, RPO, Site Recovery, or regional continuity
- the decision has clear continuity implications
- the recommendation would be materially incomplete without it

If BC/DR seems relevant but is not requested, suggest it as an optional lens instead of forcing it.

## Use of current documentation

Use current Microsoft documentation only when freshness materially affects the answer, especially for Azure service support, landing-zone guidance updates, Policy behavior, RBAC semantics, regional capability, or service limits.

Do not invoke current-doc research by default for stable, generic reasoning.

## Mandatory behavior

- Identify the decision first, not the implementation tool.
- Make assumptions explicit.
- Compare realistic options, not strawmen.
- Keep tradeoffs concrete.
- Surface material risk, blast radius, and reversibility when relevant.
- Include cost-value considerations when they matter to the decision.
- Stay proportional to the size of the question.

## Adaptive output modes

Choose the lightest output that fits the request.

### Quick answer

Use for narrow asks.

Include:

- direct recommendation
- short rationale
- optional risk or follow-up note

### Decision note

Use for normal strategic support.

Include:

- decision statement
- key options or tradeoff
- recommended direction
- main risk or validation note

### Deep analysis

Use only for broad, ambiguous, high-risk, or explicitly detailed requests.

Include:

- context and assumptions
- options considered
- active lenses used
- recommendation and why it wins
- main risks and blast radius
- validation or follow-up path

## Anti-patterns

- forcing a full multi-lens analysis for a small question
- treating BC/DR as mandatory for every answer
- recommending a direction without current-source verification when freshness matters
- activating this fallback when one specialist clearly owns the next step
- expanding into tool selection when the user did not ask for it
- giving generic best-practice advice without context, tradeoff, or cost implication

## Validation

- State why the request could not be assigned to one primary Azure specialist, or name the decision being framed.
- Confirm the selected specialist set is the minimum needed to resolve the uncertainty.
- Confirm the decision statement is explicit and narrow enough that the next owner is obvious.
- Confirm assumptions, active lenses, and the main tradeoff are named instead of implied.
- Confirm the recommendation includes reversibility or blast-radius guidance when the choice is hard to unwind.
- Confirm cost-value or operational impact is called out when it materially changes the recommendation.
- Confirm the answer states when freshness matters and which current Microsoft fact still needs validation.
- Confirm the resolved task is handed to a primary specialist.
