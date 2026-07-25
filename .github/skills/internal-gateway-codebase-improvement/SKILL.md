---
name: internal-gateway-codebase-improvement
description: Use when manually improving codebase architecture and implementation clarity.
disable-model-invocation: true
---

# Internal Gateway Codebase Improvement

## Referenced skills

- `mattpocock-improve-codebase-architecture`: architecture discovery and
  candidate report owner.
- `addyosmani-code-simplification`: behavior-preserving implementation
  simplification owner.
- `internal-tdd`: executable or evaluable behavior-change gate.
- `superpowers-verification-before-completion`: final evidence owner.

## Manual invocation boundary

This skill runs only after the user invokes it explicitly. It is not a
canonical gateway, implicit fallback, peer-dispatch target, or subagent target.

## When to use

- The user explicitly requests codebase improvement and the evidence supports
  one of the three supported lanes.

## When not to use

- Feature development, performance optimization, security remediation, or
  dependency upgrades.
- Work that needs a canonical gateway or automatic routing.

## Lane selection

Select exactly one lane from repository evidence:

- `local-simplification`: readability, naming, nesting, duplication, dead code,
  or unnecessary implementation abstraction inside an already valid boundary.
- `architecture-improvement`: shallow modules, leaking seams, poor locality,
  cross-module coupling, or testability constrained by current interfaces.
- `combined`: an approved architecture refactor whose changed implementation
  also contains bounded simplification opportunities.

Do not run both source methods by default. No silent lane escalation: stop and
ask before changing from `local-simplification` to an architecture lane.

## Core workflow

1. Recover explicit target and anti-scope.
2. Inspect bounded evidence and choose one lane.
3. State the lane, reason, expected files, and validation path.
4. Establish a Passing behavior baseline.
5. For architecture lanes, run architecture discovery and stop at the
   Structural Approval Gate before any write.
6. For executable changes, load `/internal-tdd`.
7. Record the approved interfaces and seams as the Protected seam set.
8. Apply the executable refactor in the approved scope.
9. Apply behavior-preserving simplification only for
   `local-simplification` or the approved changed scope of `combined`.
10. Run the focused checks and the Final Evidence Gate.

Domain-model and ADR writes from the architecture method also require the
Structural Approval Gate.

## Structural Approval Gate

Before any architecture, domain-model, or ADR write, present the candidate
report and the expected file set. Stop and wait for explicit user approval.
Do not proceed without it.

## Protected seam set

Before any executable refactor, record the approved modules, interfaces,
adapters, side effects, error behavior, ordering, and test surfaces.
Simplification must not alter any protected seam.

## Final Evidence Gate

After all writes, load `/superpowers-verification-before-completion` and
present fresh passing evidence for the focused validation path before
claiming completion.
