---
name: internal-gateway-codebase-improvement
description: Use when explicitly invoked to run the core codebase-architecture improvement workflow with a mandatory critical challenge after analysis and before report writing.
---

# Internal Gateway Codebase Improvement

## Referenced skills

- `/mattpocock-improve-codebase-architecture`: owns the complete architecture-improvement workflow.
- `/internal-gateway-critical-master`: challenges the completed draft analysis before the core writes its report.

## Invocation boundary

Run only when explicitly invoked. This skill is a repository-owned wrapper; it does not replace, copy, or extend the core workflow beyond the critical gate defined below.

## When to use

Use when the core architecture-improvement workflow must produce a draft analysis that receives a critical challenge before report writing.

## Contract

1. Load `/mattpocock-improve-codebase-architecture` and follow it unchanged through completion of `Explore`.
2. Keep the resulting evidence, candidates, recommendation, assumptions, and evidence gaps as the current draft analysis. Do not write or present the HTML report yet.
3. Run `/internal-gateway-critical-master` against that current draft analysis.
4. Treat the pass as clear only when the critic returns `route-to-execution-owner`, Defense is `none` or `resolves`, and no material objection or unresolved uncertainty remains.
5. For every non-clear pass, return to the core's `Explore` step with the objection and smallest required evidence. Revise the analysis, then run a fresh critical challenge before report writing.
6. Repeat only when the analysis materially changes or new evidence appears. If required evidence is unavailable, unsafe, outside scope, declined, or needs a user decision, stop and report the blocker and resume condition.
7. After a clear pass, resume `/mattpocock-improve-codebase-architecture` at report generation and let it own every remaining step.

## Boundaries

- Call only the two referenced skills directly. Skills used transitively by the core remain the core's responsibility.
- Do not modify or reinterpret either referenced skill, and do not add fields or outcomes to the critic.
- Do not create a second workflow, separate design artifact, evidence contract, transition resolver, gateway-specific artifact, planning handoff, or additional approval gate.
- Preserve the core's workspace, report, candidate-selection, grilling, domain-modeling, and stop behavior.

## Validation

- The wrapper directly references only the core and the critic.
- The critical challenge occurs after `Explore` and before report generation.
- No report is written from an analysis with a material objection or unresolved uncertainty.
- Every retry uses changed analysis or new evidence; terminal evidence gaps stop with a visible resume condition.
- The core resumes unchanged after a clear critical result.
