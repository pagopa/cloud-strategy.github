---
name: internal-gateway-codebase-improvement
description: Use when a repository-owned codebase needs evidence-backed architecture analysis, deep-module design, mandatory critical challenge, and an implementation plan without executing changes.
---

# Internal Gateway Codebase Improvement

## Referenced skills

- `/mattpocock-codebase-design`: architecture vocabulary and design-method owner.
- `/internal-gateway-critical-master`: mandatory final challenge owner.
- `/internal-gateway-writing-plans`: only successful terminal handoff.

## Invocation boundary

Run only when explicitly invoked. Own analysis through plan writing. Never own implementation.

## When to use

Use when repository evidence suggests a module boundary, interface, seam, or
locality problem requires architecture analysis before implementation.

## Scope

- Use for shallow modules, leaking seams, poor locality, low-leverage interfaces,
  cross-module coupling, or testability constrained by architecture.
- Do not use for local simplification, feature delivery, performance tuning,
  security remediation, dependency upgrades, or direct implementation.

## Contract

1. Run Preflight and Analysis Gates from [`references/workflow.md`](references/workflow.md).
2. Present evidence-backed candidates and obtain candidate selection.
3. Use `/mattpocock-codebase-design` to design the selected deepening.
4. Run Feasibility and Structural Approval Gates.
5. Run `/internal-gateway-critical-master` for every approved design.
6. If the critic leaves any open point, invalidate approval and return to Analysis.
7. Repeat analysis, design, feasibility, approval, and critical challenge until clear.
8. On a clear critical result, invoke `/internal-gateway-writing-plans` and stop
   after the retained plan is written. Never execute it.

## Non-negotiable critical rule

Plan writing is illegal before a current-cycle critical pass has no material
objection, unresolved uncertainty, unanswered question, or accepted residual risk.
`accept-with-risk` is not clear and must reopen Analysis.

## Output

Keep one compact evidence ledger across loops. Use the schemas in
[`references/evidence-contract.md`](references/evidence-contract.md), report the
retained plan path, and name `/internal-gateway-execute-plans` only as the plan
writer's next owner; do not invoke it.
