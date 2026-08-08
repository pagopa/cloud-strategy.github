---
schema: internal-gateway-idea/v1
slug: "<slug>"
status: discovering
revision: 1
target: "<one-sentence goal>"
source_baseline: null
lane: shape-idea
assurance: standard
assurance_reason: "<why standard or high assurance applies>"
platform_semantics_controlling: false
reviewed_revision: null
approved_revision: null
next_actor: agent
next_action: "Identify the nearest owner, consumer, and validation path."
---

# Living Design Document

## Context and Goal

Record the original request, the intended outcome, and any execution-shaped
request that is being held at the design boundary.

## Decisions and Rationale

Record accepted defaults, unresolved user decisions, controlling evidence, and
why the selected direction beats the strongest rejected alternative.

## Scope and Coverage

Use one row for every explicit deliverable. Add `Interface`, `Independent
decision`, and `Consumer` when three or more owners or runtime surfaces are
involved.

| ID | Deliverable | Owner/design element | Interface | Independent decision | Consumer | Validation | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | TBD deliverable | TBD owner or design element | TBD interface or approved anti-scope | TBD independent decision | TBD consumer | TBD focused check | TBD covered or blocked |

## Design

Describe the current design direction, alternatives, invariants, maintenance
footprint, exit criterion, and any bounded exception.

## Validation and Handoff

- Target: TBD approved target path or scope.
- Source baseline: TBD baseline or source document.
- Anti-scope: TBD explicitly excluded work.
- Nearest owner: TBD next owner.
- Validation path: TBD commands or human review.
- Stop conditions: TBD scope, state, evidence, or approval blockers.
- Observable acceptance: TBD proof that the current revision is complete.
- Authority: Design approval, plan writing, and implementation execution remain separate.

## Review Ledger

Persist only validated, decision-relevant findings. Keep IDs monotonic and
never reuse an ID. Use semicolons to separate evidence references.

| ID | Source | Critique | Recommendation | Reason | Blocking | Evidence | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-001 | standard | TBD finding | TBD recommended remedy | TBD why it matters | false | TBD path#L1 | open |

## Risks and Open Questions

List named residual risks, unresolved user decisions, missing platform evidence,
and approved anti-scope. Silence does not resolve a user-owned decision.

## Continuation

Load this document in a clean chat. Validate the header and required sections,
then resume at `next_actor` and `next_action` for the current revision.
