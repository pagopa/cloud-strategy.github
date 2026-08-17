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

### Finding block shape

Each finding is one compact block:

```markdown
**N. <dot> <short title>** — <severity>/<confidence>

- **<Problem>:** what is wrong, one to two sentences, with a traceable
  location such as `path:line` or section reference.
- **<Suggestion>:** the smallest useful report-only follow-up, one to two
  sentences.
- **<Why>:** why it matters for the verdict, one to two sentences.
```

Rules:

- Severity dots are stable: 🔴 high, 🟡 medium, 🟢 low.
- Each field must be understandable without rereading the investigation:
  name the file, section, decision, or mechanism involved; never a cryptic ID
  alone.
- Do not emit `Fix owner` or `Expected verification` fields in chat; route
  them to the caller-owned record when one exists.
- Keep residual risk beside the finding or evidence gap it qualifies.

### Evidence gaps shape

Each gap is a bold name followed by what stays unconfirmed and why it can
change the verdict. A bare name or one-word entry is invalid.

### Open shape

Each open question is numbered and stated in plain language. When the answer
is a choice, list lettered options with their consequence (for example `A)`
keep the current owner, `B)` propose a separate design), then add one
suggested option marked with `💡` together with a one-sentence reason. Omit
the section when nothing material is open.

### Next shape

Number each action, make it concrete, and reference the finding, evidence
gap, or open question it closes. One action per step; no vague instructions
such as "improve the document".

### Mermaid rules

Use at most one diagram, and only when it clarifies three or more material
causal, dependency, ownership, or state relationships. Use a top-down
flowchart with:

- one node per finding or effect, anchored as `Finding N` or by its short
  name;
- short self-explanatory phrases of two to four `\n`-broken lines, not bare
  IDs;
- an emoji prefix per node and semantic fills: red for the problem, amber for
  decision-level effects, yellow for verdict-level effects;
- the controlling conclusion in adjacent prose; the diagram is never the sole
  carrier of evidence.

## Completion

The review is complete when every material conclusion is traceable or limited
by an explicit evidence gap, the scope and residual risk are visible, the
verdict is calibrated, and no remediation was applied.
