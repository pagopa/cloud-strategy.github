---
name: internal-gateway-idea
description: Use when a repository-owned idea needs brainstorming, assumption challenge, alternative discovery, critical resolution, and an automatic handoff to implementation planning.
---

# Internal Gateway Idea

## Referenced skills

- `/superpowers-brainstorming`: core idea-to-design workflow before the local critical-resolution override.
- `/grill-me`: repeatable clarification sessions for material points the critic cannot resolve unanimously.
- `/internal-gateway-writing-plans`: implementation-plan writing immediately after the critic emits `accepted`.
- `/mattpocock-research`: on-demand owner for decision-relevant external research after local evidence is exhausted; this reference does not preload the skill.

## Local references

- `references/workflow.md`: authoritative state machine, Mermaid workflow,
  approval rules, routing stability, and scoped local validation lane for this bundle.
- `scripts/audit_workflow.py`: marker-consistency validator; run via `python3 .github/skills/internal-gateway-idea/scripts/audit_workflow.py`.
- Script output contract: `text` for short operator summaries (default), `json` for nested or machine-consumed output, `tsv`/`csv` only for large flat tables; data on stdout, diagnostics on stderr; keep output bounded.

Lightweight repository-owned wrapper for idea shaping. Use `/superpowers-brainstorming` as the core workflow and add the local gates below. Loading `/superpowers-brainstorming` is an intentional, globally-resolvable exception to the bundle self-containment rule. This skill does not replace the core brainstorming process; it constrains it for repository-owned idea work.

## When to use

- A repository-owned request starts as an idea, option set, proposed direction, or unclear goal.
- The user asks to brainstorm, shape, challenge, or decide before implementation.
- The work needs a validated design direction before implementation planning.

## Core contract

- Follow the mandatory gate sequence: `Specialization Checkpoint: gated`, `Idea Gate 0`, `External Research Checkpoint`, `Assumption Challenge Gate`, `Alternative discovery`, `Critical Challenge Gate`, `Critical resolution loop`, `Automatic plan handoff`, `Stop before implementation execution`.
- Load `/superpowers-brainstorming` as the core workflow.
- Read `references/workflow.md` before presenting the final design direction.
- Keep the `/superpowers-brainstorming` hard gate: no implementation action before the user approves the design.
- Treat approval as gate-local. `procedi`, `ok`, `go`, or similar approval advances only the active visible gate.
- If approval wording is ambiguous, ask whether it means design approval, critical review, or implementation execution.
- After the bounded evidence pass, run `Idea Gate 0` as one numbered bulk question block; evidence cannot replace Idea Gate 0.
- Do not proceed to `External Research Checkpoint`, assumption challenge,
  alternative discovery, design direction, critical resolution, or plan writing
  until `Idea Gate 0` is accepted or the user explicitly overrides its defaults.
- Run `Critical Challenge Gate` as its own visible gate after the user approves the design direction and before plan writing; an embedded critique does not satisfy Critical Challenge Gate.
- The only critical outcomes are `accepted`, `revise-design`, `reopen-analysis`, and `needs-clarification`.
- `accepted` is legal only when every material objection raised during the current `Critical Challenge Gate` is closed or explicitly routed; continue to `Automatic plan handoff`.
- Every material objection raised during the current critical pass is closed or explicitly routed before `accepted`.
- every material objection raised during the current critical pass is closed or explicitly routed.
- `revise-design` returns to design presentation and approval, then reruns `Critical Challenge Gate`.
- `reopen-analysis` returns to `Idea Gate 0` so the assumption, scope decision, or alternative can be reconsidered.
- `needs-clarification` means load `/grill-me` for one or more numbered clarification sessions over the critic's newly surfaced elements.
- After clarification, return to the relevant earlier approval gate when a material change occurred; otherwise rerun `Critical Challenge Gate` directly. Repeat until the critic emits one conclusive routing outcome.
- If any mandatory gate was skipped, stop, name the missed gate, mark any downstream artifact as draft-only, and resume at the first skipped mandatory gate.
- Use this skill only to add repository-owned idea gates, not to fork the core brainstorming process.
- Keep collaborative questioning inside the core brainstorming workflow.
- Load `/internal-gateway-writing-plans` automatically after `accepted`; no additional artifact-choice or plan-writing approval is required.
- Stop after the delegated writing outcome. Do not implement, invoke execution owners, or run execution commands from this skill.
- Keep the agent filename, frontmatter name, and workflow aligned.

## User-facing communication

Keep mandatory gates, research decisions, assumption checks, approval state,
and recovery state as internal workflow state. Project only decision-relevant
information into chat through one compact user-facing decision card for status,
approval, routing, material risk, blocker, and requested user action.

Use at most four content lines:

- `🧭` names one unresolved decision.
- `✅` gives the recommendation or result.
- `💡` gives one short reason when it changes the decision.
- `✈️` states the exact user action and what acceptance advances.

Use `🎯` for a goal, `🛠️` for a proposed change, `🧪` for validation, and
`⚠️` for a material risk or blocker when one of those facts is the decision.

Content-bearing output uses its owning schema and is outside the four-line
card limit. Guided questions, alternatives, design sections, and required
critique schemas are content-bearing output.

Do not announce skipped checkpoints. Do not print the internal gate ledger,
bounded-evidence notes, anti-scope inventory, research checkpoint, or routing
bookkeeping unless the user asks for details or one item blocks progress.
Match the user's language.

## Bounded context pass

Before asking the first question block:

- Identify the target, nearest owner, and likely validation path from the smallest useful repository evidence.
- For large files, generated output, logs, or tabular artifacts, inspect aggregate facts first: path, size, headers, counts, anomalies, and targeted slices.
- If platform semantics control feasibility or ownership, verify those semantics before converging.
- Separate original user intent from emerged requirements. Do not rewrite later constraints as the original request.

## State machine

Follow `references/workflow.md` in this order:

1. `Bounded evidence pass`
2. `Specialization Checkpoint: gated` when the incoming ask is execution-shaped.
3. `Idea Gate 0`
4. `External Research Checkpoint`
5. `Assumption Challenge Gate`
6. `Alternative discovery`
7. `Present design direction`
8. `Critical Challenge Gate`
9. `Critical resolution loop`
10. `Automatic plan handoff`
11. `Stop before implementation execution`

If a later step happened before an earlier mandatory gate, use `Skipped-gate
recovery`: stop the current lane, identify the first skipped mandatory gate,
and resume there before producing or revising a retained artifact.

Do not skip from evidence or design approval to implementation. The only
post-brainstorming owner this skill may load is
`/internal-gateway-writing-plans`, automatically after the critic emits
`accepted`.

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

Run this checkpoint after `Idea Gate 0` is accepted and before `Assumption
Challenge Gate`. Local evidence remains the default.

Skip external research unless all of these are true:

- the unresolved question is owned by an external primary source;
- local evidence is insufficient;
- the answer could change feasibility, approach, constraints, or risk.

When all conditions hold:

1. Define one bounded research question.
2. load `/mattpocock-research` on-demand and write one Markdown report under
   `tmp/research/YYYY-MM-DD-<slug>.md`.
3. Bring only the report path and decision-relevant conclusions back into the
   brainstorming flow.
4. Continue to `Assumption Challenge Gate`, or return to `Idea Gate 0` when the
   evidence changes an accepted constraint or default.

`internal-gateway-idea` owns when research is warranted.
`/mattpocock-research` owns how the research is performed. Do not copy its
research procedure here, and do not start a second research pass automatically.

Validation must keep this checkpoint on-demand, bounded to one question and one
report, preceded by local evidence, and routed to `tmp/research/`.

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

- `accepted` continues to `Automatic plan handoff`.
- `revise-design` returns to design presentation and approval before another critical pass.
- `reopen-analysis` returns to `Idea Gate 0`.
- `needs-clarification` loads `/grill-me` and runs one or more numbered clarification sessions over the critic's newly surfaced elements.

After `/grill-me`, return to the relevant earlier approval gate when a material change occurred; otherwise rerun `Critical Challenge Gate` directly. Repeat until the critic emits one conclusive routing outcome.

## Automatic plan handoff

For `accepted`, start implementation-plan writing immediately by loading
`/internal-gateway-writing-plans`. The transition notification is exactly:

```text
🚀 **Scrittura del piano avviata**
✅ La critica si è conclusa senza obiezioni materiali aperte.
🛠️ `/internal-gateway-writing-plans` sta preparando il piano di implementazione.
```

This is the only transition notification. The subsequently produced
implementation plan remains normal content-bearing output. Do not ask for
another approval or write a retained spec.

This automatic handoff authorizes plan writing only. It does not authorize
implementation execution.

## Validation

- The skill read `references/workflow.md` before finalizing the design direction.
- The skill used `Specialization Checkpoint: gated` for execution-shaped requests.
- The skill loaded `/superpowers-brainstorming` as core instead of copying its workflow.
- The skill challenged the user's initial assumption, not only corrected the proposed solution.
- The skill presented 2-3 approaches and explained why the recommendation beat the strongest rejected option.
- The skill used `Critical Challenge Gate` before plan writing.
- Every material objection raised during the current critical pass was closed or explicitly routed before `accepted`.
- A `needs-clarification` result ran one or more `/grill-me` sessions over the critic's newly surfaced elements and returned to the relevant earlier approval gate after a material change or reran the critic otherwise.
- An `accepted` result started implementation-plan writing immediately and emitted only the exact transition notification.
- The skill treated ambiguous approval words as gate-local and clarified the active gate when needed.
- The skill kept collaborative questioning inside the core brainstorming workflow.
- The skill loaded `/internal-gateway-writing-plans` only for implementation-plan writing after `accepted`.
- The skill stopped after `/internal-gateway-writing-plans` produced a writing outcome.
- The Mermaid workflow and runtime prompt contain the same mandatory gate names.
- The phrase `agent filename, frontmatter name, and workflow aligned` appears in the skill, workflow, and runtime prompt.
