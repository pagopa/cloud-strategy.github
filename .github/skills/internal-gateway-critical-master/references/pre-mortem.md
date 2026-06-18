# Pre-mortem

Use this reference when a plan or decision has material execution risk and the selected challenge lenses do not explicitly cover failure modes.

## When to use

Trigger the pre-mortem when at least one of these is true:

- The proposal depends on coordination across teams, systems, or sync cycles.
- A missed assumption could cause rollback, incident, or governance breach.
- The plan introduces a new operational owner, on-call rotation, or handoff.
- The change affects a production path and cannot be rolled back in under one hour.
- The user asks for a pre-mortem, failure-mode analysis, or "what could go wrong" check.

## Four-step procedure

1. **Assume failure.** State one concrete failure: "It is three months from now and the plan has failed."
2. **Identify causes.** List the 2-3 most likely root causes. Classify each as technical, organizational, or temporal.
3. **Rate probability.** Label each cause as `high`, `medium`, or `low` probability based on repository evidence, not intuition.
4. **Define mitigation.** For `high` and `medium` causes, define the condition or action that must happen before execution resumes.

## Failure-mode checklist

Ask at least one question from each category.

- **Technical**: Which dependency, contract, or environment change could invalidate the plan?
- **Organizational**: Which owner, approval, or handoff is most likely to slip?
- **Temporal**: Which deadline, sync cycle, or consumer rollout could expose a hidden cost?

## Output format

- Stated failure scenario (one sentence).
- Top 2-3 root causes with classification and probability.
- Required mitigation or stop condition for each `high`/`medium` cause.

## Stop conditions

- Stop after 3 causes unless the user explicitly asks for deeper failure-mode mapping.
- If no cause exceeds `low` probability, record the residual risk and close.
- Do not turn the pre-mortem into an implementation plan; route mitigation work to the next owner from `SKILL.md`.
