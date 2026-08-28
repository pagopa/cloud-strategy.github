---
name: internal-gateway-critical-master
description: Use when any plan, proposal, decision, design, workflow, requirement, or assumption set needs a thorough critical challenge before action.
metadata:
  revision: 2026-08-17
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
For an independent, evidence-first, report-only assurance review of an existing
non-code artifact or change, use `internal-review-high-level` instead; use this
skill for an interactive critical challenge before action.

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

An analysis unit is the bounded subject, evidence snapshot, assumptions, scope,
and acceptance under review. The caller owns one invocation ledger for each
unit. Each entry records the unit identity, pass type (`full` or `delta`),
evidence snapshot or digest, changed claims or assumptions, rerun reason, and
outcome. Critical Master supplies those pass details and does not create a
competing ledger.

When no caller-owned ledger exists because the user invoked this skill directly,
the critic maintains an equivalent in-conversation unit record for the current
analysis unit: unit identity, pass type, evidence snapshot digest, rerun reason,
and outcome. The same rerun rules apply against that record.

- Run one full challenge pass per analysis unit by default.
- Use a delta review after a materially supported change, limited to changed
  claims, evidence, assumptions, acceptance, and residual blockers.
- Do not rerun on unchanged evidence. Reject or suppress a request whose unit
  and evidence snapshot are unchanged, and record that decision in the ledger.
- Permit a second full pass only when the ledger records one of these reasons:
  an open blocker remains, new evidence changes a controlling assumption, or
  scope changes. The entry must identify the changed evidence or scope.
- The critic challenges and reports. The subject's active primary owner is
  identified by current responsibility, not by an upstream skill or producer;
  that owner retains subject scope and decisions. A caller retains routing,
  finding classification, plan-expansion, and lifecycle responsibilities
  outside the review, and the user retains acceptance on direct invocation.
  Critical Master does not acquire subject routing or acceptance authority.

Classify every finding exactly once before it can change the current plan:
`blocking-now`, `acceptance-required`, `follow-up`, `separate-design`, or
`rejected-with-reason`. A finding that is not traceable to an approved
requirement is `separate-design`. When the subject has no approved requirement
baseline, do not deflect a finding to `separate-design` merely for missing
traceability; classify it by consequence as `blocking-now`,
`acceptance-required`, or `follow-up`, and record the missing baseline as an
evidence gap.

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

Select at least three lenses based on the highest-risk gaps. The third lens must
still be lateral (`analogy` or `reverse-assumption`). Each additional lens
beyond three is permitted only when it covers a material gap the first three do
not. Apply each selected lens once.

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

Completion criterion: at least three lenses were applied, the third is lateral,
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

### Finding block shape

Each finding is one compact block:

```markdown
**N. <dot> <short title>** — <classification> · <severity>/<confidence>

- **<Problem>:** what is wrong, one to two sentences, concrete.
- **<Suggestion>:** the smallest change that fixes it, one to two sentences.
- **<Why>:** why it matters, one to two sentences.
```

Rules:

- Severity dots are stable: 🔴 high, 🟡 medium, 🟢 low.
- Each of the three fields must be understandable without rereading the
  investigation: name the file, decision, or mechanism involved; never a
  cryptic ID alone.
- A defense of the subject is not a finding. Do not record it as one;
  defenses belong in the subject's own rationale.
- Deeper bookkeeping fields (`Fix owner`, `Expected verification`) go to the
  caller-owned ledger when one exists; they do not appear in chat.

### Residuals shape

Each residual risk is a bold name followed by an explanation of what stays
open and why it matters. A bare name or one-word entry is invalid. A deferral
is acceptable to report only with its consequence stated.

### Open shape

Each open question is numbered and stated in plain language. When the answer
is a choice, list lettered options with their consequence (for example `A)`
keep the current owner, `B)` propose a separate design), then add one
suggested option marked with `💡` together with a one-sentence reason. Omit
the section when nothing material is open.

### Next shape

Number each action, make it concrete, and reference the finding or residual it
closes. One action per step; no vague instructions such as "improve the spec".

### Mermaid rules

Use at most one diagram, and only when it clarifies three or more material
causal, dependency, ownership, or state relationships. Use a top-down
flowchart with:

- one node per finding or effect, anchored as `Finding N` or by its short
  name;
- short self-explanatory phrases of two to four `\n`-broken lines, not bare
  IDs;
- an emoji prefix per node and semantic fills: red for the problem, amber for
  decision-level effects, yellow for recommendation-level effects;
- the controlling conclusion in adjacent prose; the diagram is never the sole
  carrier of evidence.

Do not emit an unrelated card, machine-only object, preamble, or internal
working notes.

### Delta passes

A delta pass keeps the same layout and emits only changed evidence, findings,
classifications, conclusion, and residual blockers. Preserve every material
finding, compacting by grouping rather than deleting. A full pass includes the
scope only when it changes interpretation.

## No-context failure

When no subject or evidence can be recovered, emit only:

```markdown
# Critical Analysis

## Status
Failure: no analysable context was available.

## Required Context
Provide a subject, decision, proposal, design, document, or evidence to critique.
```
