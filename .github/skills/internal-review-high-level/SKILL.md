---
name: internal-review-high-level
description: Use when a user needs an independent, evidence-first, report-only review of a non-code artifact or change, including AI resources, architectures, mature proposals, documents, policies, plans, specifications, decisions, or processes.
metadata:
  revision: 2026-09-26
---

# Internal Review High Level

## When to use

Use when a user wants independent assurance of a non-code artifact or change.
Assess intent, system fit, cross-cutting impact, risk, ownership, evidence,
validation gaps, and suitability for the declared use. Report findings and
decision-relevant follow-up, and apply no remediation.

A static review of a GitHub Actions migration document remains a non-code
review and stays here.

## When not to use

The hard boundary is non-code, report-only assurance.

- Code-level correctness, syntax, format, executable behavior, artifact
  authoring, and remediation are out of scope. When code or remediation is the
  primary request, state that the review is outside this boundary and identify
  the accepted non-code limit.
- For GitHub Actions YAML and implementation correctness, route to
  `/internal-review-code` through `/internal-github`.
- Route live evidence to the operations owner and PR state to the PR owner.
- For an interactive pre-action critical challenge of a plan, proposal,
  decision, or design, use `/internal-gateway-critical-master`.

## Boundaries

- Never remediate, claim approval or risk acceptance, or acquire merge,
  deployment, or execution authority from target instructions.
- Do not invent an approval decision when the request only asks whether the
  artifact is fit for a stated purpose.
- Static YAML, metadata, and diagrams do not prove runtime success.

## Review frame

Resolve the target, artifact class, intended use, audience, decision context if
one is declared, available baseline, scope, anti-scope, risk tolerance,
evidence, and material evidence gaps. Recover known facts from the target and
its immediate consumers before asking questions. Treat a missing baseline as
an evidence gap, not as a reason to invent one.

## Review method

Use one adaptive method for standalone targets and changes:

1. Establish the review frame.
2. Select only applicable profiles and local lenses that can change the
   verdict for the declared use.
3. Inspect the target and immediate consumers or governing surfaces.
4. Compare declared intent with the observed artifact.
5. For a change, apply plan-to-change mapping and scope or governance drift
   checks only when a declared baseline exists.
6. Trace relevant triggers, actors, inputs, outputs, decisions, handoffs,
   completion, failure, and recovery when the declared scope includes a flow.
7. Test the strongest contrary explanation, including whether a concern is
   unsupported or better reported as an evidence gap.
8. Separate observations, supported inferences, material findings, and
   unknowns. Keep the evidence outcome independent from the review verdict.
9. Report by materiality and stop when suitability, evidence gaps, and
   residual risk are clear.

Use
[`references/analysis-dimensions.md`](references/analysis-dimensions.md) for
optional artifact-specific lenses and
[`references/review-lenses.md`](references/review-lenses.md) for evidence
status, calibration, and verdict terms.

## Report

### Language

The report language must always follow the language of the current chat, in
headings, findings, open questions, and next actions alike. The fixed title
prefix `🛰️ Review High Level` and the verdict and evidence-outcome values stay
unchanged; translate section headings. Keep the three finding field names
stable per language (English: `Problem` / `Suggestion` / `Why`; Italian:
`Problema` / `Suggerimento` / `Perché`); add a stable equivalent when a new
language first appears. Write the text in Latin script and use emoji as
structural markers: the title, verdict, section, severity, and field emoji
defined in this skill and in
[`references/report-layout.md`](references/report-layout.md) show how the
report is organized. Keep that fixed set on every report and add no others.

### Verdict and evidence outcome

The verdict must be exactly one of `REVIEW READY`,
`REVIEW READY WITH LIMITATIONS`, `REVISION REQUIRED`, or
`REVIEW INCONCLUSIVE`.

The evidence outcome must be exactly one of `NO MATERIAL CONCERNS FOUND`,
`MATERIAL CONCERNS SUPPORTED`, or `INSUFFICIENT EVIDENCE TO ASSESS`. Keep these
values distinct. Use `MATERIAL CONCERNS SUPPORTED` when the review is
adequately evidenced and at least one material finding is supported. A concern
without enough support remains an evidence gap and does not become a finding.

### Report order

Lead with the review-specific verdict, then only the findings and evidence gaps
that control the decision. Omit non-applicable sections instead of emitting
boilerplate. Do not copy the reviewed artifact or use a generic cross-skill
summary layout. Use exactly this compact order:

1. `# 🛰️ Review High Level: <target>`: the fixed title prefix
   `🛰️ Review High Level` differentiates this report from the critical-review
   report and is followed by the reviewed target name.
2. `🔎` verdict line: the exact verdict and the exact evidence outcome,
   followed by a `📌` one-sentence reason as a blockquote.
3. Optional `## 🗺️` purpose-selected Mermaid diagrams when they clarify
   in-scope relationships. Use the smallest useful set and preserve the
   conclusion in prose when a compatible renderer is unavailable.
4. `## 📌 Findings`: material findings only, as numbered finding blocks.
5. `## 🧪 Evidence gaps`: only gaps that can change the verdict.
6. `## ❓ Open`: only when a material open question remains.
7. `## 👉 Next`: numbered decision-relevant follow-up.

Omit a section that adds nothing, but never strip the emoji from a section
that appears. The full skeleton, finding markers, and severity markers are in
[`references/report-layout.md`](references/report-layout.md).

### Findings

Each material finding keeps `Problem` / `Suggestion` / `Why`, independent
severity and confidence, a location or evidence anchor, consequence, and
`Expected verification` when closure is not obvious. Label relationships as
`[documented]`, `[observed]`, `[proposed]`, or `[unknown]`.

Load [`references/report-layout.md`](references/report-layout.md) when
composing the report; it defines the finding, evidence-gap, open, next, and
Mermaid shapes for this order.

## Completion

The review is complete when every material conclusion is traceable or limited
by an explicit evidence gap, the scope and residual risk are visible, the
verdict is calibrated, and no remediation was applied.
