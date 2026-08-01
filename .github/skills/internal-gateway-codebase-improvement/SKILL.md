---
name: internal-gateway-codebase-improvement
description: Use when explicitly invoked to run the core codebase-architecture improvement workflow, challenge its completed report, and stop at the report-only boundary.
---

# Internal Gateway Codebase Improvement

## Referenced skills

- `/mattpocock-improve-codebase-architecture`: owns the complete architecture-improvement workflow.
- `/internal-gateway-critical-master`: challenges the completed report analysis before the gateway returns the report.

## Invocation boundary

Run only when explicitly invoked. This skill is a repository-owned wrapper; it does not replace, copy, or extend the core workflow beyond the critical gate defined below.

## When to use

Use when the core architecture-improvement workflow must produce a completed report that receives a critical challenge before the gateway returns it.

## Contract

1. Load `/mattpocock-improve-codebase-architecture` unchanged and let it complete `Explore` and HTML report generation.
2. In the same agent orchestration context, intercept before the core presents its candidate-selection question and challenge the completed report analysis with `/internal-gateway-critical-master`. Consume the critic's internal Defense, canonical routing outcome, strongest objection, and unresolved uncertainty as working state. Do not add those internal fields to the critic's public card.
3. Treat the pass as clear only when the canonical outcome is `route-to-execution-owner`, Defense is `none` or `resolves`, and no material objection or unresolved uncertainty remains.
4. For every non-clear pass, rerun the core's report flow with the strongest objection and the smallest new evidence, then challenge the newly completed report in the same orchestration context.
5. If safe rerun evidence or same-context critic state is unavailable, or if required evidence is unavailable, unsafe, outside scope, declined, or needs a user decision, stop with a blocker and a concrete resume condition.
6. After a clear pass, return the core report path and stop. Preserve its HTML report format and `./tmp/codebase-improve/` workspace contract. Do not enter the core's post-report candidate-selection or grilling loop.

## Boundaries

- Call only the two referenced skills directly. Skills used transitively by the core remain the core's responsibility.
- Do not modify or reinterpret either referenced skill, and do not add fields or outcomes to the critic.
- Do not create a second workflow, separate design artifact, evidence contract, transition resolver, gateway-specific artifact, planning handoff, or additional approval gate.
- Preserve the core's report format and workspace contract.
- The gateway owns the terminal stop immediately after report generation.
- Do not invoke candidate selection, grilling, domain modeling, ADR work, design-it-twice, planning, implementation, or another downstream owner.
- If the report-only handoff cannot be honored, stop with a blocker and resume condition; never continue into the core's post-report workflow.

## Validation

- The wrapper directly references only the core and the critic.
- The critical challenge occurs after completed report generation and before report-only return.
- The report fingerprint and critic-input fingerprint identify the same completed report analysis.
- The critic's internal outcome and Defense stay in the same orchestration context and do not alter its public card.
- A non-clear result triggers a fresh report flow or stops with a visible resume condition.
- A clear pass writes exactly the core report, returns its path, and stops before grilling or any downstream owner.
