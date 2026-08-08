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

- `references/workflow.md`: authoritative state machine, Mermaid workflow,
  approval rules, and routing stability for this bundle.
- Script output contract: `text` for short operator summaries (default), `json` for nested or machine-consumed output, `tsv`/`csv` only for large flat tables; data on stdout, diagnostics on stderr; keep output bounded.

Lightweight repository-owned wrapper for idea shaping. Use `/superpowers-brainstorming` as the core workflow and add the local gates below. Loading `/superpowers-brainstorming` is an intentional, globally-resolvable exception to the bundle self-containment rule. This skill does not replace the core brainstorming process; it constrains it for repository-owned idea work.

## When to use

- A repository-owned request starts as an idea, option set, proposed direction, or unclear goal.
- The user asks to brainstorm, shape, challenge, or decide before implementation.
- The work needs a validated design direction before implementation planning.

## Core contract

- Follow the mandatory gate sequence: `Specialization Checkpoint: gated`, `Idea Gate 0`, `External Research Checkpoint`, `Controlling platform evidence`, `Assumption Challenge Gate`, `Alternative discovery`, `Coverage + minimality`, `Present design direction`, `Full-analysis consolidation`, `Independent full-scope critical`, `Full-loop revision when material`, `Whole-analysis user approval`, `Writing-plans`, `Stop before implementation execution`.
- Load `/superpowers-brainstorming` as the core workflow.
- Read `references/workflow.md` before presenting the final design direction.
- Keep the `/superpowers-brainstorming` hard gate: no implementation action before the user approves the design.
- Treat approval as gate-local. `procedi`, `ok`, `go`, or similar approval advances only the active visible gate.
- If approval wording is ambiguous, ask whether it means design approval, critical review, or implementation execution.
- After the bounded evidence pass, run `Idea Gate 0` as one numbered bulk question block; evidence cannot replace Idea Gate 0.
- Do not proceed to the next mandatory gate until `Idea Gate 0` is accepted or the user explicitly overrides its defaults.
- Before design presentation and before final approval, build one coverage map for every explicit deliverable. Each row must contain `requirement ID | user deliverable | nearest owner/design element | consumer | validation | status or approved anti-scope`; add interface and independent-decision columns when three or more owners or runtime surfaces are involved. A missing deliverable or unexplained anti-scope blocks advancement.
- If platform semantics control feasibility or ownership, obtain controlling primary-source evidence before architecture defaults; adapter-only evidence routes back to analysis.
- Compare `no-new-artifact`, `existing-owner`, and `new-abstraction` before selecting a new abstraction. A selected new abstraction needs an invariant, footprint/maintenance rationale, and exit criterion.
- Keep multi-turn continuity to exactly `tmp/idea/<slug>/state.yaml` and `tmp/idea/<slug>/design.md`. They are lightweight, best-effort artifacts, not durable storage, a security boundary, or planning authorization. `design.md` is the single living spec and coverage artifact; do not append a transcript or create a duplicate spec.
- Before the critical pass, recompose the complete current `design.md`. Require at least one independent full-scope critique; same-context self-review, delta-only critique, or unavailable review without a fail-closed fallback cannot authorize planning.
- A material revision to requirements, scope, ownership, platform assumptions, alternative, coverage, validation, anti-scope, or material risk invalidates the prior critique and requires recomposition plus a new full pass.
- Run `Critical Challenge Gate` as its own visible gate after design presentation and full-analysis consolidation; an embedded critique does not satisfy it.
- The only critical outcomes are `accepted`, `revise-design`, `reopen-analysis`, and `needs-clarification`.
- `accepted` is legal only when every material objection raised during the current `Critical Challenge Gate` is closed or explicitly routed; continue to `Whole-analysis user approval`.
- Every material objection raised during the current critical pass is closed or explicitly routed before `accepted`.
- `revise-design` returns to design presentation and approval, then reruns full-analysis consolidation and the independent full-scope critical pass.
- `reopen-analysis` returns to `Idea Gate 0` so the assumption, scope decision, or alternative can be reconsidered.
- `needs-clarification` means load `/grill-me` for one or more numbered clarification sessions over the critic's newly surfaced elements.
- After clarification, return to the relevant earlier approval gate when a material change occurred; otherwise rerun the independent full-scope critical pass directly. Repeat until the critic emits one conclusive routing outcome.
- If any mandatory gate was skipped, stop, name the missed gate, mark any downstream artifact as draft-only, and resume at the first skipped mandatory gate.
- Use this skill only to add repository-owned idea gates, not to fork the core brainstorming process.
- Keep collaborative questioning inside the core brainstorming workflow.
- After objections are closed, routed, or exposed as named residual risks, present the entire current analysis and independent outcome. Ask one explicit current-conversation question authorizing plan writing; a generic approval is sufficient only when no residual risk remains, otherwise name the risk being accepted. Only this approval may load `/internal-gateway-writing-plans`.
- Stop after the delegated writing outcome. Do not implement, invoke execution owners, or run execution commands from this skill.

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

Follow `references/workflow.md` in this order:

1. `Bounded evidence pass`
2. `Specialization Checkpoint: gated` when the incoming ask is execution-shaped.
3. `Idea Gate 0`
4. `External Research Checkpoint`
5. `Controlling platform evidence`
6. `Assumption Challenge Gate`
7. `Alternative discovery`
8. `Coverage + minimality`
9. `Present design direction`
10. `Full-analysis consolidation`
11. `Independent full-scope critical`
12. `Critical resolution loop`
13. `Whole-analysis user approval`
14. `Writing-plans`
15. `Stop before implementation execution`

If a later step happened before an earlier mandatory gate, use `Skipped-gate
recovery`: stop the current lane, identify the first skipped mandatory gate,
and resume there before producing or revising a retained artifact.

Do not skip from evidence or design approval to implementation. The only
post-brainstorming owner this skill may load is
`/internal-gateway-writing-plans`, and only after whole-analysis approval.

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

- The skill read `references/workflow.md` before finalizing the design direction.
- The skill used `Specialization Checkpoint: gated` for execution-shaped requests.
- The skill loaded `/superpowers-brainstorming` as core instead of copying its workflow.
- The skill verified controlling platform semantics before architecture defaults when they governed feasibility or ownership.
- The skill produced coverage and minimality evidence before design presentation and final approval.
- The skill kept exactly `state.yaml` and `design.md` as lightweight, best-effort state and single living spec.
- The skill challenged the user's initial assumption, not only corrected the proposed solution.
- The skill presented 2-3 approaches and explained why the recommendation beat the strongest rejected option.
- The skill recomposed the complete current analysis before an independent full-scope critical pass.
- The skill used `Critical Challenge Gate` only after full-analysis consolidation and before plan writing.
- Every material objection raised during the current critical pass was closed or explicitly routed before `accepted`.
- A material revision invalidated the prior critical result and triggered a new full pass.
- A `needs-clarification` result ran one or more `/grill-me` sessions over the critic's newly surfaced elements and returned to the relevant earlier approval gate after a material change or reran the critic otherwise.
- An `accepted` result waited for one explicit current-conversation approval of the entire analysis before implementation-plan writing and emitted only the exact transition notification.
- The skill treated ambiguous approval words as gate-local and clarified the active gate when needed.
- The skill kept collaborative questioning inside the core brainstorming workflow.
- The skill loaded `/internal-gateway-writing-plans` only for implementation-plan writing after `accepted`.
- The skill stopped after `/internal-gateway-writing-plans` produced a writing outcome.
- The Mermaid workflow and runtime prompt contain the same mandatory gate names.
