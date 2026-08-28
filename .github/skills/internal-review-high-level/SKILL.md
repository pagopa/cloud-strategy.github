---
name: internal-review-high-level
description: Use when a user needs an independent, evidence-first, report-only review of a non-code artifact or change, including AI resources, architectures, mature proposals, documents, policies, plans, specifications, decisions, or processes.
metadata:
  revision: 2026-08-17
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
For an interactive pre-action critical challenge of a plan, proposal, decision,
or design, use `internal-gateway-critical-master` instead; use this skill for
independent, report-only assurance.

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

Lead with the review-specific verdict, then only the findings and evidence gaps
that control the decision. Omit non-applicable sections instead of emitting
boilerplate. Do not copy the reviewed artifact or use a generic cross-skill
summary layout.

The report language must always follow the language of the current chat, in
headings, findings, open questions, and next actions alike. Keep the three
finding field names stable per language (English: `Problem` / `Suggestion` /
`Why`; Italian: `Problema` / `Suggerimento` / `Perché`); add a stable
equivalent when a new language first appears. Use only Latin characters.

Keep `NO MATERIAL CONCERNS FOUND` distinct from `MATERIAL CONCERNS SUPPORTED`
and `INSUFFICIENT EVIDENCE TO ASSESS`. Use `MATERIAL CONCERNS SUPPORTED` when
the review is adequately evidenced and at least one material finding is
supported. A concern without enough support remains an evidence gap and does
not become a finding.

## Public projection

Use `🔎` for the review result, `📌` for the reason, `🧪` for evidence or an
evidence gap, and `👉` for the next decision-relevant follow-up. The verdict
must be exactly one of `DECISION READY`, `DECISION READY WITH KNOWN RISK`,
`DECISION BLOCKED`, or `REVIEW INCONCLUSIVE`. Use exactly
`NO MATERIAL CONCERNS FOUND`, `MATERIAL CONCERNS SUPPORTED`, or
`INSUFFICIENT EVIDENCE TO ASSESS` for the evidence outcome. Omit an anchor when
it adds no information.

Use exactly this compact review-specific order:

1. `# 🛰️ Review High Level: <target>` — fixed title prefix `🛰️ Review High
   Level` to differentiate this report from the critical-review report,
   followed by the reviewed target name.
2. Verdict line — the exact verdict and the exact evidence outcome, followed
   by a one-sentence reason as a blockquote.
3. Optional single Mermaid diagram when it clarifies three or more material
   causal, dependency, ownership, or state relationships (rules below).
4. `## 📌 Findings` — material findings only, as numbered finding blocks.
5. `## 🧪 Evidence gaps` — only gaps that can change the verdict.
6. `## ❓ Open` — only when a material open question remains.
7. `## 👉 Next` — numbered decision-relevant follow-up.

Load `references/report-layout.md` when composing the report; it defines the finding, evidence-gap, open, next, and Mermaid shapes for the compact review-specific report above.

## Completion

The review is complete when every material conclusion is traceable or limited
by an explicit evidence gap, the scope and residual risk are visible, the
verdict is calibrated, and no remediation was applied.
