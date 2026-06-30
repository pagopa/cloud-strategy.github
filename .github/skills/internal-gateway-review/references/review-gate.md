# Review Gate

Use this reference when `internal-gateway-review` needs to package findings before the final verdict.

## Required Fields

- Findings
- Severity
- Confidence
- Evidence gap
- Counter-validation
- Route or next owner
- Decision-usefulness check
- Review Gate outcome

## Decision-Usefulness Check

Before the final user-visible verdict, confirm that the review supports a clear
decision: accept, patch, investigate, plan, or accept with a named residual
risk.

The reader should understand:

- the verdict and confidence;
- the smallest evidence set that supports it;
- what was ruled out or not supported by evidence;
- why any finding, keep result, or no-finding result matters;
- the best next action;
- the most important residual risk.

If any material part is missing, use `review gate: reopen` until the missing
decision context is added. Strong findings may carry most of this context. No
findings and low-severity-only reviews need explicit coverage, decision trace,
and residual-risk context.

## Gate States

- `review gate: satisfied` when the findings are specific, routed, counter-validated, and ready for the user-visible verdict.
- `review gate: reopen` when material evidence is missing, counter-validation exposes a material flaw, the remediation choice needs more challenge, or the visible review is formally correct but too thin to support a clear user decision.

## Boundary

- Keep the gate visible before any fixes.
- Run counter-validation before the final user-visible verdict; challenge each finding for evidence, severity, route, and contrary proof.
- For large diffs, generated files, logs, or tabular exports, keep evidence compact: cite the smallest excerpt or path that proves the finding and summarize omitted raw volume.
- Report only material self-critique results: corrections, confidence changes, evidence gaps, or confirmation that no material issue was found.
- Use the gate to route each actionable finding to the smallest next owner.
