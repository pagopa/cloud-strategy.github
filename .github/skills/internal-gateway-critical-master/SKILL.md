---
name: internal-gateway-critical-master
description: Use when a plan, proposal, decision, design, workflow, requirement, or assumption set must be challenged before action, including requests to stress-test it, poke holes in it, play devil's advocate, or run a pre-mortem. Route report-only assurance reviews of existing artifacts to /internal-review-high-level and code or diff reviews to /internal-review-code.
metadata:
  revision: 2026-09-26
---

# Critical Master

## Referenced skills

This skill is self-contained. It needs no caller protocol, fixed metadata,
repository workflow, or machine-readable input. The entries below are
competing owners for routing only, not dependencies.

- `/internal-review-high-level`: independent, evidence-first, report-only
  assurance review of an existing non-code artifact or change.
- `/internal-review-code`: review of a branch, pull request, or code diff.

## When to use

- Challenge a plan, proposal, decision, design, workflow, requirement,
  document, architecture, or assumption set before someone acts on it.
- Serve as the critical-review step that a gateway or another caller invokes
  on one bounded subject.

Route away when the primary deliverable is:

- a report-only assurance review of an existing artifact: use
  `/internal-review-high-level`;
- a review of code, a diff, or a pull request: use `/internal-review-code`;
- the remedy itself, such as a redesign, plan, or implementation: this skill
  challenges and reports; the subject's owner builds the remedy.

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

## Authority

- Critical Master challenges and reports. It never acquires subject routing,
  scope, or acceptance authority.
- The subject's active primary owner, identified by current responsibility
  rather than by an upstream skill or producer, retains subject scope and
  decisions.
- A calling skill retains routing, final finding disposition, plan expansion,
  and lifecycle. On direct invocation, the user retains acceptance.

## Analysis units and reruns

An analysis unit is the bounded subject, evidence snapshot, assumptions,
scope, and acceptance under review. Track each pass with: unit identity, pass
type (`full` or `delta`), evidence snapshot or digest, changed claims or
assumptions, rerun reason, and outcome. When a caller owns a ledger, supply
these details to it and keep no competing record. On direct invocation, keep
an equivalent record in the conversation.

- Run one full pass per analysis unit by default.
- After a materially supported change, run a delta pass limited to changed
  claims, evidence, assumptions, acceptance, and residual blockers.
- Suppress a request whose unit and evidence snapshot are unchanged, and
  record the suppression.
- Allow a second full pass only for a recorded reason that names the changed
  evidence or scope: an open blocker remains, new evidence changes a
  controlling assumption, or the scope changed.

## Finding classification

Propose exactly one classification for every finding before it can change the
current plan. The caller owns the final disposition.

| Classification | Blocking | Meaning |
| --- | --- | --- |
| `blocking-now` | yes | The subject must not proceed until the finding is resolved. |
| `acceptance-required` | yes | Proceeding needs an explicit decision to accept the risk. |
| `follow-up` | no | Material, but safe to resolve after the current step. |
| `separate-design` | no | Valid, but not traceable to the approved requirement baseline. |
| `rejected-with-reason` | no | Examined and dismissed; the report states the reason. |

When the subject has no approved requirement baseline, classify by
consequence as `blocking-now`, `acceptance-required`, or `follow-up`; do not
use `separate-design` for missing traceability alone. Record the missing
baseline as an evidence gap.

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

Select at least three lenses based on the highest-risk gaps. When a caller
fixes the lens count, use exactly that count. The third lens must be lateral
(`analogy` or `reverse-assumption`). Add a lens beyond three only when it
covers a material gap the first three do not. Apply each selected lens once.

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
Identify at most one root question whose answer could change the critique.
Surface it under the report's open-questions section instead of pausing the
analysis. Treat mitigations as conditions for continuing, not as
implementation designs that silently rescue a weak proposal.

Completion criterion: at least three lenses were applied, the third is lateral,
all material findings are represented, and material failure modes appear in a
finding or residual risk.

### Phase 3: Synthesize

- Run a final consistency check and name the strongest supported objection.
- Classify material claims as `confirmed`, `inference`, or `estimate` and
  evidence quality as `strong`, `partial`, or `weak`.
- Test each material finding against the steelman defense, the strongest
  argument for the subject as proposed. Classify the defense as `none`,
  `resolves`, `narrows`, `accepts-risk`, or `unanswered`. Drop a finding the
  defense `resolves`; otherwise keep its remaining vulnerability.
- Select one conclusion. A blocking finding is one classified `blocking-now`
  or `acceptance-required`.
  - `accepted`: no blocking finding remains;
  - `reopen-analysis`: a blocking finding reopens assumptions or scope;
  - `needs-clarification`: a blocking finding depends on an unresolved user
    decision, including every open `acceptance-required` finding;
  - `revise-design`: a blocking finding requires a design or proposal remedy.
  When several apply, select the first in this order: `reopen-analysis`,
  `needs-clarification`, `revise-design`.
- Use `failure-no-context` only when the sole failure condition applies.

Do not conceal a material risk just to reach `accepted`. Do not use a numeric
precision that the available evidence cannot support.

## Readable report

Return one compact chat-first Markdown review, not a transcript. The report
must fit one mental screen: every section is brief but self-contained, and no
item may be reduced to a bare phrase the reader cannot interpret without the
conversation.

The report language must always follow the language of the current chat, in
headings, findings, residuals, open questions, and next actions alike. Keep
the three finding field names stable per language (English: `Problem` /
`Suggestion` / `Why`; Italian: `Problema` / `Suggerimento` / `Perché`); add a
stable equivalent when a new language first appears.

### Fixed layout

Use exactly this order and these anchors:

1. `# 🔍 Critical Analysis` — title.
2. `🎯` conclusion line — the exact outcome plus a blocking/non-blocking count,
   then the strongest supported objection as a one-sentence blockquote.
3. Optional single Mermaid diagram (rules below).
4. `## 🧾 Findings` — numbered finding blocks (shape below).
5. `## ⚠️ Residuals` — only when material (shape below).
6. `## ❓ Open` — only when a material open question remains (shape below).
7. `## ✅ Next` — numbered concrete actions.

Omit empty sections; never pad. Do not repeat the same fact in the conclusion
line, a finding, and `Next`.

### Section shapes

Before rendering any report, load
[`references/report-formats.md`](references/report-formats.md). It owns the
finding, residual, open-question, next-action, Mermaid, and no-context shapes,
and the severity and confidence vocabularies.

### Delta passes

A delta pass keeps the same layout and emits only changed evidence, findings,
classifications, conclusion, and residual blockers. Preserve every material
finding, compacting by grouping rather than deleting. A full pass includes the
scope only when it changes interpretation.

## No-context failure

When no subject or evidence can be recovered, emit the no-context projection
in [`references/report-formats.md`](references/report-formats.md) and stop.
