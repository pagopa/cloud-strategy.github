---
name: internal-gcp-governance
description: Use when /internal-gcp selects governance for Google Cloud IAM, workload identity, service-account boundaries, Org Policy, inherited guardrails, or governed exceptions.
---

# Internal GCP Governance

Use this workflow to define Google Cloud identity, authorization, preventive
guardrails, workload trust, governed exceptions, and the verification needed
to apply them safely.

## When to use

Use when `/internal-gcp` selects the governance lane: a Google Cloud control
stack, identity boundary, or governed exception decision.

## Workflow

1. Establish the control objective, affected scope, principals, workloads,
   ownership boundaries, and blast radius.
2. Separate preventive guardrails, authorization, and workload trust into
   explicit decision areas.
3. Select the control stack across Org Policy, inheritance, IAM, workload
   identity federation, and service-account boundaries.
4. Define governed exceptions with an owner, reason, scope, compensating
   controls, review date, and closure condition.
5. Name staged control verification, rollback triggers, and the evidence
   required before widening a high-blast-radius change.

## Output

Return one governance control-stack decision for the requested Google Cloud
identity, authorization, guardrail, workload-trust, or exception change.

## References

- [`references/guardrail-map.md`](references/guardrail-map.md): load only
  when the control surface or exception pattern needs deeper comparison.

## Completion criteria

- The governance scope is explicit at org, folder, or project level.
- Each recommendation states whether it prevents, grants, or constrains
  access.
- Service-account, workload, and human-access boundaries are named when
  relevant.
- Exceptions have an owner, reason, scope, review date, and compensating
  evidence.
- High-blast-radius controls have staged validation and a rollback trigger.
