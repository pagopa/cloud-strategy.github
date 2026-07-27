---
name: internal-review-high-level
description: Use when a user needs an independent, evidence-first, report-only review of a non-code artifact or change, including AI resources, architectures, mature proposals, documents, policies, plans, specifications, decisions, or processes.
---

# Internal Review High Level

## Purpose

Provide an independent, evidence-first review of non-code artifacts and
changes. Report findings and decision-relevant follow-up; apply no remediation.

## Scope

Review AI resources, architectures, mature proposals, documents, policies,
plans, specifications, decisions, and processes for intent, system fit,
cross-cutting impact, risk, ownership, evidence, validation gaps, and decision
readiness.

The hard boundary is non-code, report-only assurance. Exclude code-level
correctness, syntax, format, executable behavior, artifact authoring, and
remediation. When code or remediation is the primary request, state that the
review is outside this boundary and identify the accepted non-code limit.

## When to use

Use this skill when a user wants system-level assurance of a non-code artifact
or change, including its intent, boundaries, evidence, risk, ownership, or
decision readiness.

## Review frame

Resolve the target, artifact class, declared intent, audience, decision,
available baseline, scope, anti-scope, risk tolerance, evidence, and material
evidence gaps. Recover known facts from the target and its immediate consumers
before asking questions. Treat a missing baseline as an evidence gap, not as a
reason to invent one.

## Review method

Use one adaptive method for standalone targets and changes:

1. Establish the review frame.
2. Select only applicable local lenses that can change the verdict.
3. Inspect the target and immediate consumers or governing surfaces.
4. Compare declared intent with the observed artifact.
5. For a change, apply plan-to-change mapping and scope or governance drift
   checks only when a declared baseline exists.
6. Test the strongest contrary explanation.
7. Separate observations, supported inferences, material findings, and unknowns.
8. Report by materiality and stop when the decision, evidence gaps, and
   residual risk are clear.

Use `references/analysis-dimensions.md` for optional artifact-specific lenses.
Use `references/review-lenses.md` for evidence status, calibration, and
verdict terms. Select only questions that can change the verdict.

## Output

Lead with material findings, then decision-relevant evidence gaps, verdict, and
residual risk. Omit non-applicable sections instead of emitting empty
boilerplate.

Each material finding contains:

- `Evidence`: the observed fact or explicit gap, with a traceable location.
- `Impact`: the consequence if the concern remains unresolved.
- `Severity`: consequence-based materiality.
- `Confidence`: evidence strength, separate from severity.
- `Recommendation`: the smallest useful report-only follow-up.
- `Fix owner`: the accountable role or team, when known.
- `Expected verification`: the check that would confirm resolution.

Keep `no material findings` distinct from `insufficient evidence`. A concern
without enough support remains an evidence gap and does not become a finding.

## Public projection

Use `🔎` for the review result, `📌` for the reason, `🧪` for evidence or an
evidence gap, and `👉` for the next decision-relevant follow-up. Omit an anchor
when it adds no information.

## Completion

The review is complete when every material conclusion is traceable or limited
by an explicit evidence gap, the scope and residual risk are visible, the
verdict is calibrated, and no remediation was applied.
