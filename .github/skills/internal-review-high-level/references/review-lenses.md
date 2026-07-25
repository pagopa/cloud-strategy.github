# Review Lenses

Use this reference when systems-fit review needs tiered lenses without creating
new persona agents. Cross-owner routes are recommendation-only.

## Severity

Use one severity scale:

| Severity | Meaning |
| --- | --- |
| `critical` | Security flaw, data loss, severe correctness failure, or unsafe automation. |
| `high` | Likely user-visible break, broken owner contract, or serious validation gap. |
| `medium` | Plausible regression, contract weakness, or missing validation. |
| `low` | Low-risk maintainability, clarity, or test gap. |
| `info` | Non-blocking context or evidence note. |

## Confidence

Use one confidence scale:

| Confidence | Meaning | Reporting rule |
| --- | --- | --- |
| `verified` | File, line, diff, or validator evidence proves the concern. | Include and prioritize by severity. |
| `likely` | Evidence strongly supports the concern. | Include as a normal finding. |
| `plausible` | The pattern is credible but needs verification. | Include with a caveat and route to verification. |
| `speculative` | The concern lacks direct evidence. | Report only as an evidence gap, not an actionable finding. |

`critical` findings require `likely` or `verified` confidence and concrete file,
line, diff, or validator evidence.

## Finding shape

```text
[severity=<critical|high|medium|low|info>] [confidence=<verified|likely|plausible|speculative>]
Evidence: <file, line, diff, command, or explicit gap>
Issue: <what is wrong>
Causal layer: <why it happens>
Route: <recommendation-only owner or defer>
```

Do not use an unpromoted security review owner as active. Route
security-specific gaps through the closest existing owner and state the
promotion gap.
