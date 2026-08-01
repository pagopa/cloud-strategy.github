---
name: internal-gateway-codebase-improvement
description: Use when a repository-owned codebase needs evidence-backed architecture analysis, deep-module design, mandatory critical challenge, and a retained challenged Design Packet without executing changes.
---

# Internal Gateway Codebase Improvement

## Referenced skills

- `/mattpocock-codebase-design`: architecture vocabulary and design-method owner.
- `/internal-gateway-critical-master`: mandatory final challenge owner; call it
  as-is and consume its existing result.
- `/internal-gateway-writing-plans`: optional manual next owner after a separate user request.

## Invocation boundary

Run only when explicitly invoked. Own analysis through a retained challenged
Design Packet. Stop before any planning or execution owner and never own
implementation.

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
8. On a clear critical result, retain the challenged Design Packet, report its
   artifact path, and stop before `/internal-gateway-writing-plans`. A separate
   user request may select that owner later.

## Critical-master boundary

This gateway calls `/internal-gateway-critical-master` without changing its
skill, prompts, outcomes, or output contract. Consume the result it returns;
do not require a gateway-specific envelope or add producer-side metadata. The
existing `route-to-execution-owner` result is treated as challenge readiness
for this gateway only: retain the Design Packet and stop, without invoking an
execution or planning owner.

## Non-negotiable critical rule

Design readiness is illegal before a current-cycle critical pass has no material
objection, unresolved uncertainty, unanswered question, or accepted residual
risk. `accept-with-risk` is not clear and must reopen Analysis.

## Output

Keep one compact evidence ledger across loops. Use the schemas in
[`references/evidence-contract.md`](references/evidence-contract.md), retain a
Design Artifact under `tmp/codebase-improvement/designs/`, report its path, and
stop. `/internal-gateway-writing-plans` may be invoked only after a separate
user request that passes the retained artifact manually; this gateway never
invokes it.
