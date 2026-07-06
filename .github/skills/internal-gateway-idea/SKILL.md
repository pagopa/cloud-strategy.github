---
name: internal-gateway-idea
description: Use when a repository-owned idea needs brainstorming, assumption challenge, alternative discovery, and a spec-vs-plan recommendation before implementation planning.
---

# Internal Gateway Idea

## Referenced skills

- `superpowers-brainstorming`: core idea-to-design workflow.
- `internal-gateway-writing-plans`: retained spec or implementation-plan writing after the user approves the direction.

Lightweight repository-owned wrapper for idea shaping. Use `superpowers-brainstorming` as the core workflow and add the local gates below. This skill does not replace the core brainstorming process; it constrains it for repository-owned idea work.

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

- Load `superpowers-brainstorming` as the core workflow.
- Keep the `superpowers-brainstorming` hard gate: no implementation action before the user approves the design or direct-plan recommendation.
- Use this skill only to add repository-owned idea gates, not to fork the core brainstorming process.
- Keep collaborative questioning inside the core brainstorming workflow.
- Load `internal-gateway-writing-plans` only after the user approves retained spec or implementation-plan writing.

## Bounded context pass

Before asking the first question block:

- Identify the target, nearest owner, and likely validation path from the smallest useful repository evidence.
- For large files, generated output, logs, or tabular artifacts, inspect aggregate facts first: path, size, headers, counts, anomalies, and targeted slices.
- If platform semantics control feasibility or ownership, verify those semantics before converging.
- Separate original user intent from emerged requirements. Do not rewrite later constraints as the original request.

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

## Validation

- The skill loaded `superpowers-brainstorming` as core instead of copying its workflow.
- The skill challenged the user's initial assumption, not only corrected the proposed solution.
- The skill presented 2-3 approaches and explained why the recommendation beat the strongest rejected option.
- The skill used `Critical Challenge Gate` before spec or plan writing.
- The skill kept collaborative questioning inside the core brainstorming workflow.
- The skill loaded `internal-gateway-writing-plans` only for retained spec or implementation-plan writing.
- The old `internal-gateway-idea-brainstorming` bundle remained untouched.
