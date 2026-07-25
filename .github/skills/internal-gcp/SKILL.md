---
name: internal-gcp
description: Use when a Google Cloud task cannot be routed confidently to a specific GCP skill because the request is materially ambiguous, has multiple GCP domains with no clear primary owner, or requires clarification before selecting the correct specialist, or when the user needs high-level Google Cloud platform decision support or tradeoff framing before implementation. Do not use for clearly scoped organization structure, governance or IAM, or operations or validation tasks.
---

# Internal GCP

Fallback router for Google Cloud tasks that cannot be assigned confidently to one specialist, and strategic support skill for high-level GCP decision framing. Do not activate only because the task concerns Google Cloud; activate only when material routing uncertainty blocks owner selection or when the user needs decision support before the next step is structure, governance, operations, or delivery.

## When to use

- Material ambiguity prevents selecting one primary GCP specialist.
- Multiple GCP domains are material and no primary owner can be identified safely.
- The user explicitly invokes `$internal-gcp`.
- The task asks which GCP lane should own the work before requesting a domain solution.
- The user needs high-level GCP decision support or tradeoff framing before implementation.

## When not to use

- The task is already a clear implementation change.
- The user only needs detailed IAM, Org Policy, monitoring, backup, or automation implementation.
- The task is purely post-rollout validation or evidence gathering.
- The request is narrow and operational with no real decision to frame.

## Routing threshold

Activate only when at least one holds:

- the request is materially ambiguous and clarification is required before a GCP owner can be selected;
- multiple GCP domains are material and no primary owner can be identified safely;
- the task asks which GCP problem-solving lane should own the work;
- the user needs strategic decision framing and the next step is not yet structure, governance, operations, or delivery.

Do not activate when one specialist clearly owns the next step; route directly to that specialist instead. Explicit `$internal-gcp` invocation remains valid.

## Handoffs

| To | Owns |
|---|---|
| `internal-gcp-organization-structure` | org, folder, project, billing-account, Shared VPC, and platform topology layout |
| `internal-gcp-governance` | IAM, workload identity, service account, Org Policy, and guardrail design |
| `internal-gcp-operations` | monitoring, validation, backup, recovery, inventory, reporting, evidence |

## Dispatch contract

1. State the routing uncertainty.
2. Identify candidate GCP owners.
3. Select the minimum specialist set.
4. Keep strategic comparison here only while needed to choose the owner.
5. Hand the resolved task to the primary specialist instead of retaining ownership.

Load `references/routing-matrix.md` for the routing decision tree. Load `references/lens-playbook.md` when the fallback trigger fires and the choice of GCP owner or lens needs structured comparison, or when the user wants a deeper decision-framing aid.

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

## Optional BC/DR lens

BC/DR is optional.

Activate it only when:

- the user asks about resilience, backup, recovery, failover, RTO, RPO, or regional continuity
- the decision has clear continuity implications
- the recommendation would be materially incomplete without it

If BC/DR seems relevant but is not requested, suggest it as an optional lens instead of forcing it.

## Use of current documentation

Use current Google Cloud documentation only when freshness materially affects the answer, especially for Architecture Framework guidance, Org Policy behavior, IAM or workload identity semantics, service support, regional capability, or service limits.

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

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Forcing a full multi-lens analysis for a small question | The answer becomes heavier than the decision requires | Start with the smallest useful lens set and widen only if risk or ambiguity justifies it |
| Treating BC/DR as mandatory for every answer | Continuity language crowds out the actual GCP tradeoff | Activate BC/DR only when regional continuity or recovery posture changes the recommendation |
| Recommending a direction without current-source verification when freshness matters | Product limits, Org Policy behavior, or regional support may have changed | Call out the freshness dependency and say which Google Cloud facts still need current verification |
| Confusing decision support with implementation guidance | The user loses the strategic framing they asked for | Keep the answer at decision level and hand off only after the direction is chosen |
| Expanding into tool or automation selection when the user did not ask for it | The response drifts from platform tradeoffs into delivery detail | Keep the recommendation centered on the GCP choice, not the tooling |
| Activating the fallback when one specialist clearly owns the next step | The router delays work a direct specialist should own | Route directly to the specialist and keep the fallback for genuine uncertainty |

## Validation

- State why the request could not be assigned to one primary GCP specialist, or name the decision being framed.
- Confirm the selected specialist set is the minimum needed to resolve the uncertainty.
- Confirm the decision statement is explicit and narrow enough that the next owner is obvious.
- Confirm assumptions, active lenses, and the main tradeoff are named instead of implied.
- Confirm the recommendation includes reversibility or blast-radius guidance when the choice is hard to unwind.
- Confirm cost-value or operational impact is called out when it materially changes the recommendation.
- Confirm the answer states when freshness matters and which current Google Cloud fact still needs validation.
