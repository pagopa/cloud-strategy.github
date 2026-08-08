---
schema: internal-gateway-idea/v1
slug: sample
status: awaiting-final-approval
revision: 2
target: Simplify the idea gateway without losing decision coverage.
source_baseline: Current idea gateway and critical-master contracts.
lane: shape-idea
assurance: standard
assurance_reason: No high-assurance trigger applies.
platform_semantics_controlling: false
reviewed_revision: 2
approved_revision: null
next_actor: user
next_action: Approve the current design or request a revision.
---

## Context and Goal

The gateway needs one living design document and a compact state machine.

## Decisions and Rationale

The design keeps discovery, critique, approval, and plan writing separate.

## Scope and Coverage

| ID | Deliverable | Owner/design element | Interface | Independent decision | Consumer | Validation | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | Living design document | idea-state | YAML header | State invariants | idea gateway | focused tests | covered |
| D-002 | Full analysis packet | critical-master | JSON packet | Finding schema | idea consumer | protocol tests | covered |
| D-003 | Plan handoff | writing-plans | approval route | Execution boundary | execution gateway | route tests | covered |

## Design

The idea gateway owns state, consolidation, rendering, and transitions.

## Validation and Handoff

- Target: The approved gateway bundles only.
- Source baseline: Current checkout and focused tests.
- Anti-scope: Imported skills, root contracts, and Git mutation.
- Nearest owner: internal-gateway-idea.
- Validation path: Focused pytest and strict skill validators.
- Stop conditions: Scope drift, unknown failure, or protected-skill finding.
- Observable acceptance: Current revision is reviewed and approval is explicit.
- Authority: Execution approval remains separate from design approval.

## Review Ledger

| ID | Source | Critique | Recommendation | Reason | Blocking | Evidence | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-001 | standard | No blocker remains. | Keep the compact contract. | Coverage is explicit. | false | design-valid.md#L50 | closed |

## Risks and Open Questions

No unresolved material risk remains for this revision.

## Continuation

Load this document in a clean chat and resume at the recorded actor/action.
