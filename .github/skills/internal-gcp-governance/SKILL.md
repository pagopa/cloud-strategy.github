---
name: internal-gcp-governance
description: Use when /internal-gcp selects governance for Google Cloud IAM, workload identity, service-account boundaries, Org Policy, inherited guardrails, or governed exceptions.
---

# Internal GCP Governance

## Purpose

Define Google Cloud identity, authorization, preventive guardrails, workload trust, governed exceptions, and the verification needed to apply them safely.

## When to use

Use this skill when the requested deliverable is a Google Cloud control stack, identity boundary, or governed exception decision.

## Process

1. Establish the control objective, affected scope, principals, workloads, ownership boundaries, and blast radius.
2. Separate preventive guardrails, authorization, and workload trust into explicit decision areas.
3. Select the control stack across Org Policy, inheritance, IAM, workload identity federation, and service-account boundaries.
4. Define governed exceptions with an owner, reason, scope, compensating controls, review date, and closure condition.
5. Name staged control verification, rollback triggers, and the evidence required before widening a high-blast-radius change.

Load `references/guardrail-map.md` only when the control surface or exception pattern needs deeper comparison.

## Output

- A governance control-stack decision artifact for the requested Google Cloud identity, authorization, guardrail, workload-trust, or exception change.

## Completion

- The governance scope is explicit at org, folder, or project level.
- Each recommendation states whether it prevents, grants, or constrains access.
- Service-account, workload, and human-access boundaries are named when relevant.
- Exceptions have an owner, reason, scope, review date, and compensating evidence.
- High-blast-radius controls have staged validation and a rollback trigger.
