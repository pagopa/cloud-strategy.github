---
name: internal-gateway-idea
description: Use when a repository-owned idea needs brainstorming, assumption challenge, alternative discovery, critical resolution, and one final whole-analysis approval before implementation planning.
---

# Internal Gateway Idea

## Referenced skills

- `/superpowers-brainstorming`: core idea-to-design workflow before the local critical-resolution override.
- `/grill-me`: repeatable clarification sessions for material points the critic cannot resolve unanimously.
- `/internal-gateway-writing-plans`: implementation-plan writing only after the current whole analysis receives explicit approval.
- `/mattpocock-research`: on-demand owner for decision-relevant external research after local evidence is exhausted; this reference does not preload the skill.

## Local references

- `references/design-template.md`: the only living-spec template and exact YAML
    header/section contract.
- `scripts/idea_state.py`: strict state parser, transitions, packet consumer,
    finding consolidation, and public projection.
- `internal-gateway-critical-master`: owns the `full-analysis-v1` producer
    packet and its contract; consume only validated packets at that boundary.
- Script output contract: `text` for short operator summaries (default), `json` for nested or machine-consumed output, `tsv`/`csv` only for large flat tables; data on stdout, diagnostics on stderr; keep output bounded.

Lightweight repository-owned wrapper for idea shaping. Use `/superpowers-brainstorming` as the core workflow and add the local gates below. Loading `/superpowers-brainstorming` is an intentional, globally-resolvable exception to the bundle self-containment rule. This skill does not replace the core brainstorming process; it constrains it for repository-owned idea work.

## When to use

- A repository-owned request starts as an idea, option set, proposed direction, or unclear goal.
- The user asks to brainstorm, shape, challenge, or decide before implementation.
- The work needs a validated design direction before implementation planning.

## Core contract

- Load `/superpowers-brainstorming` as the core workflow.
- Persist exactly one artifact: `tmp/idea/<slug>/design.md`. Its YAML header
    is the resumable state; it is not a transcript, authorization, or duplicate
    specification. Read `references/design-template.md` before creating it.
- Inspect the nearest owner, consumer, validation path, original intent, and
    emerged requirements before asking questions. Run `Idea Gate 0` as one
    numbered block with `Question`, `Recommendation`, `Why`, and `Default if
    accepted`; evidence cannot replace it.
- Obtain controlling primary-source platform evidence before architecture
    defaults. Compare `no-new-artifact`, `existing-owner`, and
    `new-abstraction`; a selected abstraction needs an invariant, maintenance
    rationale, and exit criterion.
- Map every deliverable before design presentation and final approval. Each row
    has requirement ID, deliverable, owner/design element, conditional interface,
    independent decision, consumer, validation, and status or anti-scope. Three
    or more owners or runtime surfaces require separate interface,
    independent-decision, and consumer columns.
- Recompose the complete design before critique. Use one full-scope standard
    packet and one independent packet when assurance is high. The critic owns
    packet production and this gateway owns validation, consolidation, F IDs,
    public rendering, and state transitions. Invalid or unavailable required
    review fails closed.
- A material change to requirements, scope, ownership, platform assumptions,
    alternatives, coverage, validation, anti-scope, or material risk increments
    the revision and invalidates review and approval. Open non-blocking findings
    may persist; open blockers and conflicts prevent review completion.
- High assurance applies to destructive or hard-to-reverse production changes;
    security, authorization, permission, or sensitive-data impact; an unknown
    controlling platform claim; three or more independent owners with material
    interfaces; feasibility-critical unknowns after evidence; or an explicit
    user request. Run one isolated full review, not a second workflow.
- After the bounded critic pass, use one consolidated revision. `needs-clarification`
    may load `/grill-me` with one block and one legal follow-up; the only automatic
    return is `CRITIQUE -> QUESTION -> ANALYZE` for a newly exposed blocking
    user-owned ambiguity. Silence never accepts that decision.
- Final approval is current-revision only. `approvo` stops; `approvo e scrivi il
    piano` or a later current `scrivi il piano` routes only to
    `/internal-gateway-writing-plans`. Neither phrase authorizes implementation.
- If a mandatory gate or current state is missing or stale, reconstruct the
    draft, clear claimed review/approval, and resume at the first unresolved
    state. Do not invoke the execution gateway from this skill.

## User-facing communication

Keep gate, research, approval, and recovery bookkeeping internal. Project only
decision-relevant status, routing, risk, blocker, validation, and user action in
one compact card of at most four content lines. Use `🎯` for a goal, `🧭` for an
unresolved decision, `🛠️` for a proposal, `🧪` for validation, `⚠️` for a risk,
`✅` for a result, `💡` for its reason, and `✈️` for the exact next action.
Content-bearing questions, alternatives, design sections, and critique packets
use their owning schemas and are outside the card limit. Do not announce
skipped checkpoints or print internal ledgers; match the user's language.

## Bounded context pass

Before asking the first question block:

- Identify the target, nearest owner, and likely validation path from the smallest useful repository evidence.
- For large files, generated output, logs, or tabular artifacts, inspect aggregate facts first: path, size, headers, counts, anomalies, and targeted slices.
- If platform semantics control feasibility or ownership, verify those semantics before converging.
- Separate original user intent from emerged requirements. Do not rewrite later constraints as the original request.

At the bounded evidence and external-research checkpoints, the parent may
invoke `internal-luna-executor` with the evidence question, relevant sources,
expected output, and validation. Keep Idea Gate 0, synthesis, alternatives,
critical resolution, and approval with this skill's parent.

## State machine

The canonical flow is:

`SCOPE -> DISCOVER -> QUESTION? -> ANALYZE/WRITE DRAFT -> PRE-CRITIQUE CHECK -> CRITIQUE -> USER_DECISION -> REVISE -> VERIFY -> FINAL_APPROVAL -> APPROVED -> HANDOFF/STOP`

`QUESTION?` is optional. A new blocking user-owned ambiguity permits exactly
one `CRITIQUE -> QUESTION -> ANALYZE` return; all other material changes restart
the current revision's analysis and critique. The persisted header records the
current status, revision, reviewed revision, approved revision, next actor, and
next action. The template owns literal enums; `scripts/idea_state.py` owns
parser and transition invariants.

The two lanes are `shape-idea` and `review-existing`. An execution-shaped
request records a gated specialization consequence and remains in design until
the final approval boundary. `accepted`, `revise-design`, `reopen-analysis`,
`needs-clarification`, `invalid-target`, and `request-separate-review` are
critic outcomes; only current, complete, non-blocked review can reach final
approval.

## Idea Gate 0

Run this gate after bounded evidence and before any challenge or alternative
recommendation.

Render all currently known unresolved questions in one numbered bulk question
block. Each question must include:

- `Question:` the unresolved decision.
- `Recommendation:` the evidence-based default.
- `Why:` one evidence-based sentence.
- `Default if accepted:` the concrete consequence of acceptance.

Capture the question, recommendation, reason, and accepted default internally.
Evidence-based defaults require explicit acceptance. Questions should focus
only on decisions repository evidence cannot safely answer: intent, accepted
defaults, constraints, success criteria, validation path, and anti-scope. A
bounded evidence pass may prepare recommended defaults, but evidence cannot
replace Idea Gate 0.

## External Research Checkpoint

After `Idea Gate 0`, skip research unless one unresolved question is owned by
an external primary source, local evidence is insufficient, and the answer can
change feasibility, approach, constraints, or risk. When needed, load
`/mattpocock-research` on-demand for one bounded question and one report under
`tmp/.research/`; return only decision-relevant conclusions. Reopen `Idea Gate
0` if the result changes an accepted default.

## Assumption Challenge Gate

Run this gate before finalizing the design direction.

Test whether the user's proposed direction is actually necessary:

- What problem is the proposal trying to solve?
- What would we do if the named target, path, skill, tool, or implementation idea did not exist?
- Which assumption would make the proposed direction wrong if false?
- Is there a smaller reversible move that preserves most of the value?
- Is there a non-obvious alternative that avoids the proposed change entirely?

The output must include:

1. `Original direction:` one sentence.
2. `Hidden assumption:` one sentence.
3. `Alternative path:` one sentence.
4. `Why not chosen:` one sentence, or `Chosen instead:` when the alternative is better.

If the alternative path is better, return to the relevant brainstorming branch instead of forcing the original proposal through refinement.

## Alternative discovery

Before presenting the final design, propose 2-3 approaches. Lead with the recommended approach.

Each approach must include:

- `Approach:` short name.
- `Best when:` one sentence.
- `Tradeoff:` one sentence.

The recommendation must explain why the chosen approach beats the strongest rejected option.

## Critical Challenge Gate

Before moving to an implementation plan:

- Challenge the chosen direction with first principles, opportunity cost, or reverse-assumption reasoning.
- Name the strongest objection.
- Close or explicitly route every material objection raised during the current critical pass.

Use this visible shape:

1. `Challenge:` the strongest objection.
2. `Resolution:` accepted, revise-design, reopen-analysis, or needs-clarification.
3. `Reason:` one evidence-based sentence.

`accepted` is legal only when every material objection raised during the current `Critical Challenge Gate` is closed or explicitly routed.

Keep this gate inside the local idea wrapper and the core brainstorming workflow.

## Critical resolution loop

- `accepted` continues to `Whole-analysis user approval`, then `Writing-plans` only after that approval.
- `revise-design` returns to design presentation and approval before another critical pass.
- `reopen-analysis` returns to `Idea Gate 0`.
- `needs-clarification` loads `/grill-me` and runs one or more numbered clarification sessions over the critic's newly surfaced elements.

After `/grill-me`, return to the relevant earlier approval gate when a material change occurred; otherwise rerun `Critical Challenge Gate` directly. Repeat until the critic emits one conclusive routing outcome.

## Whole-analysis approval and plan handoff

After `accepted`, present the complete current analysis, coverage map, residual
risk decisions, and independent critical outcome. Ask one explicit
current-conversation question authorizing plan writing. Only a current approval
of that whole analysis may load `/internal-gateway-writing-plans`; do not infer
it from gate-local approvals, stale state, or `accepted` alone. The transition
notification after that approval is exactly:

```text
🚀 **Scrittura del piano avviata**
✅ La critica si è conclusa senza obiezioni materiali aperte.
🛠️ `/internal-gateway-writing-plans` sta preparando il piano di implementazione.
```

This is the only transition notification. The subsequently produced
implementation plan remains normal content-bearing output. Do not ask for a
second artifact-choice approval or write a retained spec.

This approval authorizes plan writing only. It does not authorize
implementation execution.

## Validation

- Parse `design.md` with the strict YAML/state helper and reject duplicate or
    unknown header keys, stale revisions, invalid actors, missing sections,
    incomplete coverage, missing handoff controls, and unsafe ledger IDs.
- Require the focused state/consumer tests, strict skill validation, routing
    cases, token-risk checks, and the home-sync contract suite. Use human review
    for subjective prose, proportionality, discovery retention, and semantic
    regression; do not turn prose into a synthetic wording test.
- Validate the critic packet through the critical-master producer contract,
    persist the required packet sources, consolidate equivalent findings, keep
    conflicts open, and render only localized public fields.
