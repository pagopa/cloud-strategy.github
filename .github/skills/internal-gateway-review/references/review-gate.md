# Review Gate

Use this reference when `internal-gateway-review` needs to package findings before the final verdict.

## Required Fields

- Findings
- Severity
- Confidence
- Evidence gap
- Counter-validation
- Route or next owner
- Review Gate outcome

## Gate States

- `review gate: satisfied` when the findings are specific, routed, counter-validated, and ready for the user-visible verdict.
- `review gate: reopen` when material evidence is missing, counter-validation exposes a material flaw, or the remediation choice needs more challenge.

## Boundary

- Keep the gate visible before any fixes.
- Run counter-validation before the final user-visible verdict; challenge each finding for evidence, severity, route, and contrary proof.
- For large diffs, generated files, logs, or tabular exports, keep evidence compact: cite the smallest excerpt or path that proves the finding and summarize omitted raw volume.
- Report only material self-critique results: corrections, confidence changes, evidence gaps, or confirmation that no material issue was found.
- Use the gate to route each actionable finding to the smallest next owner.
