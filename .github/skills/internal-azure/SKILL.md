---
name: internal-azure
description: Use only when an Azure task cannot be routed confidently to a specific Azure skill because the request is materially ambiguous, has multiple Azure domains with no clear primary owner, or requires clarification before selecting the correct specialist. Do not use for clearly scoped organization structure, governance or identity, operations or validation, or Azure DevOps pipeline tasks.
---

# Internal Azure

## Referenced skills

- `internal-azure-organization-structure`: tenant, management-group, subscription, landing-zone, and platform-topology owner.
- `internal-azure-governance`: RBAC, managed identity, PIM, Policy, tagging, and guardrail owner.
- `internal-azure-operations`: monitoring, validation, backup, Site Recovery, reporting, and evidence owner.
- `internal-azure-devops`: Azure DevOps pipeline and project-automation owner.
- `awesome-copilot-azure-pricing`: Azure-specific pricing depth when cost data is the primary problem.

Use this skill only as a fallback under material routing uncertainty. Do not activate only because the task concerns Azure. Do not activate when one specialist clearly owns the next step.

## When to use

- Use this fallback when material ambiguity prevents selecting one primary Azure specialist.
- Use it when multiple Azure domains are material and no primary owner can be identified safely.
- Use it when the user explicitly invokes `$internal-azure`.

## Routing threshold

Activate only when at least one condition holds:

- the request is materially ambiguous and clarification is required before an Azure owner can be selected;
- multiple Azure domains are material and no primary owner can be identified safely;
- the task asks which Azure problem-solving lane should own the work before requesting a domain solution.

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

## Use of current documentation

Use current Microsoft documentation only when freshness materially affects the answer, especially for Azure service support, landing-zone guidance updates, Policy behavior, RBAC semantics, regional capability, or service limits.

Do not invoke current-doc research by default for stable, generic reasoning.

## Anti-patterns

- forcing a full multi-lens analysis for a small question
- treating BC/DR as mandatory for every answer
- recommending a direction without current-source verification when freshness matters
- activating this fallback when one specialist clearly owns the next step
- expanding into tool selection when the user did not ask for it
- giving generic best-practice advice without context, tradeoff, or cost implication
