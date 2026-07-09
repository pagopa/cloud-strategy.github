---
name: internal-gateway-idea
description: Use when a repository-owned idea needs brainstorming, assumption challenge, alternative discovery, and a spec-vs-plan recommendation before implementation planning.
---

# Internal Gateway Idea

## Referenced skills

- `superpowers-brainstorming`: core idea-to-design workflow.
- `internal-gateway-writing-plans`: retained spec or implementation-plan writing after the user approves the direction.

## Local references

- `references/workflow.md`: authoritative state machine, Mermaid workflow,
  approval rules, routing stability, and scoped local validation lane for this bundle.
- `scripts/audit_workflow.py`: marker-consistency validator; run via `python3 scripts/audit_workflow.py`.
- `make internal-gateway-idea-fast-check`: scoped local validation entrypoint for this bundle.

Lightweight repository-owned wrapper for idea shaping. Use `superpowers-brainstorming` as the core workflow and add the local gates below. Loading `superpowers-brainstorming` is an intentional, globally-resolvable exception to the bundle self-containment rule. This skill does not replace the core brainstorming process; it constrains it for repository-owned idea work.

## When to use

- A repository-owned request starts as an idea, option set, proposed direction, or unclear goal.
- The user asks to brainstorm, shape, challenge, or decide before implementation.
- The work may become a retained spec or implementation plan, but the right artifact is not yet confirmed.

## When not to use

- The request is already a concrete low-risk edit with a known owner and validation path.
- The primary task is defect-first review.
- The user has already approved a retained plan for execution.
- The request is only to maintain imported `superpowers-*` assets.

## Core contract

- Follow the mandatory gate sequence: `Specialization Checkpoint: gated`, `Idea Gate 0`, `Assumption Challenge Gate`, `Alternative discovery`, `Critical Challenge Gate`, `Spec vs plan decision`, `Stop before implementation execution`.
- Load `superpowers-brainstorming` as the core workflow.
- Read `references/workflow.md` before presenting the final design direction.
- Keep the `superpowers-brainstorming` hard gate: no implementation action before the user approves the design or direct-plan recommendation.
- Treat approval as gate-local. `procedi`, `ok`, `go`, or similar approval advances only the active visible gate.
- If approval wording is ambiguous, ask whether it means critical review, retained spec or plan writing, or implementation execution.
- After the bounded evidence pass, run `Idea Gate 0` as a visible numbered question block with `Question`, `Recommendation`, `Why`, and `Default if accepted`; evidence cannot replace Idea Gate 0.
- Do not proceed to assumption challenge, alternative discovery, design direction, critical challenge, or spec-vs-plan decision until `Idea Gate 0` is accepted or the user explicitly overrides its defaults.
- Run `Critical Challenge Gate` as its own visible gate after the user approves the design direction and before the spec-vs-plan decision; an embedded critique does not satisfy Critical Challenge Gate.
- If any mandatory gate was skipped, stop, name the missed gate, mark any downstream artifact as draft-only, and resume at the first skipped mandatory gate.
- Use this skill only to add repository-owned idea gates, not to fork the core brainstorming process.
- Keep collaborative questioning inside the core brainstorming workflow.
- Load `internal-gateway-writing-plans` only after the user approves retained spec or implementation-plan writing.
- Stop after the delegated writing outcome. Do not implement, invoke execution owners, or run execution commands from this skill.
- Keep the agent filename, frontmatter name, and workflow aligned.

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
4. `Assumption Challenge Gate`
5. `Alternative discovery`
6. `Present design direction`
7. `Critical Challenge Gate`
8. `Spec vs plan decision`
9. `Approved writing handoff`
10. `Stop before implementation execution`

If a later step happened before an earlier mandatory gate, use `Skipped-gate
recovery`: stop the current lane, identify the first skipped mandatory gate,
and resume there before producing or revising a retained artifact.

Do not skip from evidence, design approval, or `Decision: direct plan` to
implementation. The only post-brainstorming owner this skill may load is
`internal-gateway-writing-plans`, and only after explicit approval for the
selected writing path.

## Idea Gate 0

Run this gate after bounded evidence and before any challenge or alternative
recommendation.

Use one visible numbered question block. Each question must include:

- `Question`
- `Recommendation`
- `Why`
- `Default if accepted`

Questions should focus only on decisions repository evidence cannot safely
answer: intent, accepted defaults, constraints, success criteria, validation
path, and anti-scope. A bounded evidence pass may prepare recommended defaults,
but evidence cannot replace Idea Gate 0.

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

If the alternative path is better, reopen the relevant brainstorming branch instead of forcing the original proposal through refinement.

## Alternative discovery

Before presenting the final design, propose 2-3 approaches. Lead with the recommended approach.

Each approach must include:

- `Approach:` short name.
- `Best when:` one sentence.
- `Tradeoff:` one sentence.

The recommendation must explain why the chosen approach beats the strongest rejected option.

## Critical Challenge Gate

Before moving to a retained spec or implementation plan:

- Challenge the chosen direction with first principles, opportunity cost, or reverse-assumption reasoning.
- Name the strongest objection.
- Decide whether to continue, reopen a branch, or narrow scope.

Use this visible shape:

1. `Challenge:` the strongest objection.
2. `Resolution:` continue, reopen, or narrow.
3. `Reason:` one evidence-based sentence.

Keep this gate inside the local idea wrapper and the core brainstorming workflow.

## Spec vs plan decision

After the user approves the design direction, decide whether to go straight to an implementation plan or write a retained spec first.

Choose `Decision: direct plan` when target, owner, scope, constraints, rejected alternatives, and validation path are clear enough that a retained spec would mostly duplicate the implementation plan.

Choose `Decision: spec first` when product, architecture, data flow, rollout, ownership, or risk decisions are still material enough that a retained spec would reduce the chance of building the wrong thing.

Always explain the choice:

- `Decision: direct plan` or `Decision: spec first`
- `Why:` one evidence-based sentence.
- `Rejected option:` the other path and why it is weaker.
- `Next owner:` `internal-gateway-writing-plans` after user approval.
- `Approval request:` ask the user to approve the selected writing path before loading the next owner.

Approval of `Decision: direct plan` skips a retained spec only. It does not
authorize implementation execution.

## Validation

- The skill read `references/workflow.md` before finalizing the design direction.
- The skill used `Specialization Checkpoint: gated` for execution-shaped requests.
- The skill loaded `superpowers-brainstorming` as core instead of copying its workflow.
- The skill challenged the user's initial assumption, not only corrected the proposed solution.
- The skill presented 2-3 approaches and explained why the recommendation beat the strongest rejected option.
- The skill used `Critical Challenge Gate` before spec or plan writing.
- The skill treated ambiguous approval words as gate-local and clarified the active gate when needed.
- The skill kept collaborative questioning inside the core brainstorming workflow.
- The skill loaded `internal-gateway-writing-plans` only for retained spec or implementation-plan writing.
- The skill stopped after `internal-gateway-writing-plans` produced a writing outcome.
- The Mermaid workflow and runtime prompt contain the same mandatory gate names.
- The phrase `agent filename, frontmatter name, and workflow aligned` appears in the skill, workflow, and runtime prompt.
