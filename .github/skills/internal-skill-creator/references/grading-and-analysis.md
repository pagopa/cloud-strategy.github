# Grading and Analysis

Keep grading criteria independent from the outputs under review. When the
evidence is weak or ambiguous, the assertion fails.

## Grading

- Inspect the produced files and state, not only the transcript describing
  them. Verify factual claims, required process, and output quality.
- Treat superficial or coincidental matches as failures. Ask whether the cited
  evidence proves the assertion and whether the assertion separates correct
  work from a plausible mistake.
- Challenge assertions that cannot be observed or reproduced. Replace them
  with a testable behavior or a specific human-review question before a run.
- Give no partial credit within a critical assertion. Report whether each
  frozen assertion passes and link the evidence used to decide.
- If a result passes while a critical assertion fails, classify the run as
  failed. Do not let an overall score conceal that failure.

## Comparing outcomes

Interpret paired configurations one assertion at a time:

- Passing in both configurations does not show that the skill made a
  difference. The task may not need the skill, or the assertion may be too
  easy.
- Failing in both configurations points to a broken case, an unavailable
  capability, or a task beyond the tested system. Diagnose before claiming a
  skill effect.
- High variation across repeats indicates instability. Keep the individual
  outcomes visible instead of averaging the variation away.
- Report time, token use, and tool-call tradeoffs with task outcomes. A faster
  or shorter response is not an improvement when it drops required work.

Order the comparison by critical correctness and contract violations first,
then output quality, then latency, calls, tokens, and cost per accepted
outcome. Include failed attempts and retries in the resource totals. No average
may hide a critical failure.

## Human judgment and blind review

Ask a human reviewer to resolve material disagreement between a grader and the
observed artifact. Preserve both the disagreement and its resolution. An
optional blind A/B review can reduce preference bias: remove condition labels,
reorder the outputs, and ask reviewers to compare the same frozen criteria.
Blind review supplements evidence; it does not prove facts that the artifacts
do not show.

Read the transcripts and inspect output artifacts before recording a result.
When repeat runs are needed, bundle a helper that invokes the same native
runner with fixed inputs and records each run separately. A fallback that
cannot use subagents or the intended host has narrower evidence; label it less
rigorous and do not treat it as baseline-grade.
