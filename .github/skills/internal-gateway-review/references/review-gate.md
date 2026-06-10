# Review Gate

Use this reference when `internal-gateway-review` needs to package findings before the final verdict.

## Required Fields

- Findings
- Severity
- Confidence
- Evidence gap
- Route or next owner
- Review Gate outcome

## Gate States

- `review gate: satisfied` when the findings are specific, routed, and ready for the user-visible verdict.
- `review gate: reopen` when material evidence is missing or the remediation choice needs more challenge.

## Boundary

- Keep the gate visible before any fixes.
- Use the gate to route each actionable finding to the smallest next owner.
