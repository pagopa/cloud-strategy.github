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

## Evidence outcome

Report one evidence outcome separately from the review verdict:

- `MATERIAL CONCERNS SUPPORTED`: the review has adequate support for at least
  one material finding.
- `NO MATERIAL CONCERNS FOUND`: the review has adequate evidence for the
  declared scope and supports no material concern.
- `INSUFFICIENT EVIDENCE TO ASSESS`: one or more decisive questions remain
  unassessed. This does not erase a supported finding; when both occur, retain
  `MATERIAL CONCERNS SUPPORTED` and list the unassessed question as an evidence
  gap.

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

Do not emit a speculative concern as a material finding.

## Verdict

- `REVIEW READY`: the available evidence supports suitability for the declared
  use with no material unresolved concern.
- `REVIEW READY WITH LIMITATIONS`: the artifact is suitable for the declared
  use, but a visible, bounded limitation or non-decisive evidence gap remains.
- `REVISION REQUIRED`: a supported material concern prevents suitability for
  the declared use or breaks a material contract. This is a review finding,
  not authorization to remediate.
- `REVIEW INCONCLUSIVE`: evidence gaps prevent a reliable suitability
  assessment and no supported finding already determines that revision is
  required.

Verdict and evidence outcome are independently reportable. When a supported
blocking defect and a decisive evidence gap coexist, use `REVISION REQUIRED`
when the defect blocks the declared use, retain `MATERIAL CONCERNS SUPPORTED`,
and list the gap separately. These outcomes are not interchangeable.

## Recommendations

The finding fields are defined in `SKILL.md` and shaped in
[`report-layout.md`](report-layout.md). Recommendations describe the
decision-relevant outcome and expected verification. They do not provide
replacement artifact content or perform the follow-up. A speculative concern
stays an evidence gap until its evidence status improves.
