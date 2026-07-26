# Review Lenses

Use these optional vocabularies when evidence supports an actionable finding.

## Severity

Use severity only when an actionable finding exists:

- `critical`: severe harm, unsafe automation, or major loss of control.
- `high`: serious contract break or likely user-visible impact.
- `medium`: meaningful weakness or plausible regression.
- `low`: limited clarity, maintainability, or validation gap.

## Confidence

- `verified`: direct evidence proves the concern.
- `likely`: evidence strongly supports the concern.
- `plausible`: the concern is credible but needs verification.
- `speculative`: the concern lacks direct evidence and remains an evidence gap.

## Material finding

A material finding contains:

- `Evidence`: the observed fact or explicit gap.
- `Impact`: the consequence if the concern remains.
- `Recommendation`: the smallest useful follow-up.
- `Expected verification`: the check that would confirm resolution.

Keep speculative concerns as evidence gaps until verification provides stronger
support.
