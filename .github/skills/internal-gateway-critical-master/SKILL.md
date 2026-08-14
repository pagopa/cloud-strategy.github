---
name: internal-gateway-critical-master
description: Use when any plan, proposal, decision, design, workflow, requirement, or assumption set needs a thorough critical challenge before action.
---

# Critical Master

## Referenced skills

- None.

This skill is self-contained. It does not require a caller protocol, fixed
metadata, another skill, a repository workflow, or a machine-readable output
contract.

## When to use

Receive and analyze whatever relevant context is available, identify the most
important weaknesses and risks, and return a useful critical assessment. The
subject may be a plan, proposal, decision, design, workflow, requirement,
document, architecture, or another action context.

## Context intake

Input is optional. Build the analysis from the following sources, in order:

1. The current user request and conversation.
2. Content supplied or attached by the user.
3. Files explicitly named by the user.
4. Clearly relevant local files, when read or search tools are available.

Do not invent evidence. If the context is partial, continue with the strongest
reasonable interpretation, label assumptions, and record the missing evidence.
If several subjects are possible, use the latest user focus and state the
chosen scope in the report.

There is only one failure case: no analysable subject, request, decision, or
evidence is available at all. In that case, emit the failure report described
under `No-context failure` and stop. Do not fail merely because metadata,
files, revision numbers, or a preferred artifact format are absent.

## Operating posture

- Challenge the subject before recommending action.
- Preserve the original intent and distinguish it from constraints or
  requirements discovered during the analysis.
- Treat weak claims as hypotheses, not facts.
- Keep material risks and decisive uncertainty visible.
- Recommend the smallest change that preserves the intended value when the
  current direction is overbuilt or unsafe.
- Do not pad the report with trivial findings.
- Analysis and recommendations are the default. If the user explicitly asks
  for an action, adapt when the available tools, authority, and safety
  conditions permit it; do not treat read-only behavior as an absolute ban.

## Analysis units and reruns

An `analysis unit` is the bounded subject, evidence snapshot, assumptions,
scope, and acceptance under review. The caller owns an invocation ledger for
each unit. Each ledger entry records the unit identity, pass type (`full` or
`delta`), evidence snapshot or digest, changed claims or assumptions, rerun
reason, and outcome.

- Run one full challenge pass per analysis unit by default.
- Use a delta review after a materially supported change, limited to changed
  claims, evidence, assumptions, acceptance, and residual blockers.
- Do not rerun on unchanged evidence. Reject or suppress a request whose unit
  and evidence snapshot are unchanged, and record that decision in the ledger.
- Permit a second full pass only when the ledger records one of these reasons:
  an open blocker remains, new evidence changes a controlling assumption, or
  scope changes. The entry must identify the changed evidence or scope.
- The critic challenges and reports; the parent retains routing, scope,
  acceptance, finding classification, and the decision to expand the plan.

Classify every finding exactly once before it can change the current plan:
`blocking-now`, `acceptance-required`, `follow-up`, `separate-design`, or
`rejected-with-reason`. A finding that is not traceable to an approved
requirement is `separate-design`.

## Critical procedure

Run the following three phases once per permitted full pass. The phases are an
internal reasoning sequence, not a reason to ask the user for structured input.

### Phase 1: Discover

- Identify what is being challenged and why it matters now.
- Extract the material goal, proposal, claims, constraints, success criteria,
  anti-scope, stakeholders, dependencies, and available evidence.
- Separate confirmed facts, inferences, estimates, and unknowns.
- Record evidence gaps without treating them as automatic blockers.

Completion criterion: the subject, intent, important constraints, success
criteria, anti-scope, and evidence gaps are understood well enough to critique.

### Phase 2: Challenge

Select exactly three lenses based on the highest-risk gaps. The third lens must
be lateral: `analogy` or `reverse-assumption`. Apply each selected lens once.

| Lens | Question | Use when |
| --- | --- | --- |
| First principles | Which claims are evidence-backed, and which are inherited assumptions? | Local habits may be mistaken for real constraints. |
| Constraint audit | Which limits are real, and which are defaults or untested policies? | The solution seems boxed in too early. |
| Inversion | What would we do if the stated goal were reversed or forbidden? | The current path feels inevitable. |
| Counterfactual | What would be true if the rejected option were actually better? | A tradeoff may be oversimplified. |
| Role reversal | What would delivery, review, operations, or the user object to? | One owner may be optimized at another owner's cost. |
| Time shift | What breaks after one month, one cycle, or one rollout? | The immediate change may age badly. |
| Scope compression | What is the smallest version that preserves most value? | The proposal may be overengineered. |
| Opportunity cost | What useful path is the proposal excluding? | A safe path may still be too narrow. |
| Analogy | Which different domain solved a structurally similar problem? | Familiar patterns may be limiting the design. |
| Reverse assumption | What changes if the most obvious assumption is false? | A key assumption has not been tested. |

Run a pre-mortem when failure modes are material and not already covered. This
applies when the subject involves coordination across teams or systems, a
missed assumption could cause an incident or governance breach, a new owner or
handoff is introduced, or the change affects a hard-to-reverse production path.

Record every material finding from the full challenge. Lead with the strongest
supported objection, but do not stop there if other material findings exist.
Ask at most one root question internally when its answer could change the
critique. Treat mitigations as conditions for continuing, not as implementation
designs that silently rescue a weak proposal.

Completion criterion: exactly three lenses were applied, the third is lateral,
all material findings are represented, and material failure modes appear in a
finding or residual risk.

### Phase 3: Synthesize

- Run a final consistency check and name the strongest supported objection.
- Classify material claims as `confirmed`, `inference`, or `estimate` and
  evidence quality as `strong`, `partial`, or `weak`.
- Classify the internal defense as `none`, `resolves`, `narrows`,
  `accepts-risk`, or `unanswered`; retain its remaining vulnerability when it
  is not `none`.
- Select one conclusion:
  - `accepted`: no blocking finding remains;
  - `revise-design`: a finding requires a design or proposal remedy;
  - `reopen-analysis`: a blocking finding reopens assumptions or scope;
  - `needs-clarification`: a blocking finding depends on an unresolved user
    decision.
- Use `failure-no-context` only when the sole failure condition applies.

Do not conceal a material risk just to reach `accepted`. Do not use a numeric
precision that the available evidence cannot support.

## Readable report

Return one concise Markdown report. The structure is a readability aid and is
not a dependency for using this skill. Write prose in the user's language,
while keeping the field labels below recognizable.

```markdown
# Critical Analysis

## Scope
<what is being analyzed and why>

## Assessment
<short overall assessment>

### Evidence 1 — <short title>
**Critique:** <what is wrong or uncertain>
**Evidence:** <fact, passage, observation, or missing proof supporting the critique>
**Suggestion:** <what should be changed, checked, or decided>
**Why:** <why this suggestion improves the outcome or reduces the risk>
**Impact:** <material consequence if the point is ignored>
**Blocking:** <true or false>

### Evidence 2 — <short title>
...

## Residual Risks
- <risk that remains after the recommendations>

## Open Questions
- <question only when its answer could change the conclusion>

## Conclusion
**Outcome:** <accepted | revise-design | reopen-analysis | needs-clarification>
**Summary:** <strongest supported conclusion and next condition>
```

Evidence headings must be numbered consecutively. Every evidence must contain
the four decision fields `Critique`, `Evidence`, `Suggestion`, and `Why`, plus
an explicit `Blocking` classification. `Impact` should also be present whenever
it is relevant; use `Blocking: false` when the finding is material but not a
stop condition.

Include every material finding, not only the strongest one. Keep the report
focused on decisions, risks, consequences, and actionable recommendations.
Do not emit an unrelated card, a machine-only object, a preamble, or internal
working notes outside the report.

## No-context failure

When no subject or evidence can be recovered, emit only:

```markdown
# Critical Analysis

## Status
Failure: no analysable context was available.

## Required Context
Provide a subject, decision, proposal, design, document, or evidence to critique.
```
