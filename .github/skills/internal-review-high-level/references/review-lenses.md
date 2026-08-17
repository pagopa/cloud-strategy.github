# Review Lenses

Use this vocabulary to calibrate evidence, materiality, confidence, and the
verdict. Keep observations, inferences, findings, and unknowns distinct.

## Evidence status

- `direct observation`: the target or governing surface directly shows the
  relevant fact.
- `supported inference`: the fact is not stated directly, but the available
  evidence supports the conclusion.
- `evidence gap`: the available evidence cannot establish or rule out the
  concern. Keep the concern qualified until verification provides support.

## Severity

Severity describes the consequence if a supported concern remains unresolved:

- `critical`: severe harm, unsafe control, or major loss of accountability.
- `high`: serious contract break or likely user-visible or decision-impacting
  consequence.
- `medium`: meaningful weakness or plausible regression.
- `low`: limited clarity, maintainability, or validation weakness.

Do not assign severity to a purely speculative concern.

## Confidence

Confidence describes evidence strength and is separate from severity:

- `verified`: direct evidence proves the concern.
- `likely`: evidence strongly supports the concern.
- `plausible`: the concern is credible but needs verification.
- `speculative`: the concern lacks direct evidence and remains an evidence gap.

## Verdict

- `DECISION READY`: the available evidence supports the declared decision with no material unresolved concern.
- `DECISION READY WITH KNOWN RISK`: the decision is supportable, but a visible, bounded risk remains.
- `DECISION BLOCKED`: a material, supported concern blocks the declared decision.
- `REVIEW INCONCLUSIVE`: evidence gaps prevent a reliable decision.

Use `NO MATERIAL CONCERNS FOUND` when the review is adequately evidenced and no
material concern is supported. Use `MATERIAL CONCERNS SUPPORTED` when the
review is adequately evidenced and at least one material finding is supported.
Use `INSUFFICIENT EVIDENCE TO ASSESS` when evidence gaps prevent either
conclusion; these outcomes are not interchangeable.

## Material finding

Each finding is one compact block with stable field names per language:

- English: `Problem` / `Suggestion` / `Why`.
- Italian: `Problema` / `Suggerimento` / `Perché`.

Severity and confidence appear in the block header. Deeper bookkeeping fields
such as `Fix owner` and `Expected verification` go to the caller-owned record
when one exists; they do not appear in chat.

Recommendations describe the decision-relevant outcome and expected
verification. They do not provide replacement artifact content or perform the
follow-up. A speculative concern stays an evidence gap until its evidence
status improves.
