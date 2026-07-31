# Generic Architecture-Analysis Workflow

## State machine

```text
Preflight Gate
  -> Analysis Gate
  -> Candidate Gate
  -> Design Gate
  -> Feasibility Gate
  -> Structural Approval Gate
  -> Mandatory Critical Gate
       -> critical-clear: Plan Handoff
       -> open-point: Analysis Gate
       -> insufficient-evidence: Stop without plan
  -> Plan Handoff
  -> Stop before implementation
```

The gateway owns every transition. The referenced skills provide methods or
handoffs only; they do not replace a gate in this state machine.

## Gate contract

### Preflight Gate

Record the target, nearest owner, goal, anti-scope, repository policy, domain
vocabulary and ADRs when present, recent active decisions, validation
discovery, and a clean or known workspace baseline. Stop if ownership or the
validation path cannot be established safely. Record the immutable dependency
set used for the analysis and verify that referenced core bundles remain
unchanged.

### Analysis Gate

Record the current interface, whether the implementation is hidden or leaked,
callers, tests, dependency categories, real adapters, observable behavior, the
deletion test, and evidence gaps. Distinguish confirmed evidence, inference,
and estimate. Do not propose a new boundary until the current one is understood.

### Candidate Gate

Present one to three candidates. Each candidate separates value from confidence,
states blast radius and reversibility, and exposes overlap or conflict. Obtain
the user's selection before design. If the request is out of scope, stop without
plan writing.

### Design Gate

Use `/mattpocock-codebase-design` and its vocabulary: module, interface,
implementation, depth, seam, adapter, leverage, locality, deletion test,
dependency categories, and design-it-twice. For a material interface change,
design it twice and compare alternatives on depth, locality, seam placement,
caller cost, and hidden implementation. Record the selected deep module,
interface, invariants, ordering, errors, and protected behavior. Give the
packet a cycle number and stable packet ID.

### Feasibility Gate

Check that every interface field or method has a productive caller or an
explicit invariant. Complete the caller × invariant × test mapping. Check seam
propagation, anti-scope leakage, error modes, ordering, and validation commands.
Reject designs that add interface members solely for tests or that lack two real
adapters when introducing an injectable seam.

### Structural Approval Gate

Present the complete design packet, including alternatives rejected, migration
sequence, stop conditions, and validation commands. Continue only when the user
approves the design packet, not merely the candidate direction. Approval is
current-cycle state and is invalidated by any reopened analysis. Record an
approval receipt that names the exact cycle and packet ID.

### Mandatory Critical Gate

Run `/internal-gateway-critical-master` after every Structural Approval Gate.
Earlier discussion or an embedded critique does not satisfy this gate. Challenge
the current approved design for material objections, unresolved uncertainty,
unanswered questions, evidence gaps that affect interface or scope, and
accepted residual risk.

## Critical resolution loop

Any of the following is an open point and returns to Analysis: a material
objection; unresolved uncertainty; a decision-changing question; an evidence
gap affecting the interface or scope; defense `unanswered` or `accepts-risk`;
or canonical outcome `review-evidence`,
`continue-critical-with-new-evidence`, `reformulate-plan`, or
`accept-with-risk`. In every such case, invalidate the current design approval,
record the objection and required evidence in the Critical Resolution Ledger,
and do not invoke plan writing.

The only clear transition is canonical outcome `route-to-execution-owner`
combined with defense `none` or `resolves`, with no unresolved uncertainty or
material objection. The critical result must name the same current cycle and
packet ID as the approval receipt. A mismatch, missing receipt, or stale packet
is an open point and cannot reach plan writing. This challenge-readiness result
routes to `/internal-gateway-writing-plans`; the gateway does not invoke an
execution owner. `de-escalate-to-simple` stops out of scope without a plan.

On every reopened cycle, rerun Analysis, Feasibility, Structural Approval, and
Mandatory Critical. Rerun Candidate selection only when the new evidence
changes the candidate set; otherwise retain the selected candidate and record
why it remains valid. Always create a new current-cycle Design Packet and obtain
fresh approval before the next critical challenge.

## Plan Handoff and stop

Load `/internal-gateway-writing-plans` only after `critical-clear`, passing one
handoff package containing the current Design Packet, its approval receipt, the
matching critical result, compact evidence ledger, Critical Resolution Ledger,
and validation path. The writer must receive the exact packet and cycle ID
named by the clear critical result; do not reconstruct or substitute a design
between the Critical Gate and handoff. Wait for the retained plan to be
written, report its path, and stop before implementation. A missing or
incomplete plan is not a successful terminal state.
