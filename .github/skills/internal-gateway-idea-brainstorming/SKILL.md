---
name: internal-gateway-idea-brainstorming
description: Use when a repository-owned request starts with a vague idea, unclear goal, unresolved option set, or needs substantive definition, convergence, critical challenge, and retained planning in the same conversation.
---

# Internal Gateway Idea Brainstorming

## Referenced skills

Load these skills by name only when the active phase requires them. This list is
an on-demand dependency index. Do not preload them; load only the owner proved
by the active uncertainty or next checkpoint.

- `grill-me`: guided decision interview.
- `internal-gateway-simple-task`: direct execution owner after a confident handoff when retained planning is not recommended.
- `internal-gateway-review`: defect-first review owner.
- `internal-gateway-critical-master`: mandatory critical challenge owner.
- `internal-gateway-writing-plans`: retained-plan authoring after a confident critical outcome.
- `internal-gateway-execute-plans`: approved retained-plan execution owner.
- `internal-agent-support-next-step`: next-step package formatting.

Portable skill-first idea gateway. This skill now owns substantive idea work
through retained-plan creation. It stops before execution.

## When to use

- The user brings a vague idea, unclear goal, or unresolved option set.
- Brainstorming, clarification, or success criteria are needed before planning.

## When not to use

- The target state and validation path are already concrete; use `internal-gateway-simple-task`.
- The primary request is defect-first review; use `internal-gateway-review`.
- A retained plan folder is already approved for execution; route to `internal-gateway-execute-plans` for `compact` or `extended`.

## Core Invariants

- Same-conversation support-skill loading is not a lane change.
- Idea Gate 0 remains mandatory.
- Start with a bounded evidence pass ordered by risk. Read only the smallest local owner evidence needed to classify the request before asking questions.
- For large tabular files, generated reports, or long log exports, keep the bounded evidence pass aggregate-first: collect file sizes, schema or headers, counts, anomalies, and targeted slices before any deeper read.
- When authoritative platform semantics control feasibility or ownership, verify them early in the bounded evidence pass.
- This gateway is not a specialized execution owner. A concrete task may not be accepted for execution here until Idea Gate 0 is `grill-me satisfied` and `Critical Gate 2` is `confident`.
- For a direct concrete operation, emit `Specialization Checkpoint: gated`, explain that this owner cannot decide task ownership or execute yet, and continue with the bounded evidence pass plus mandatory `grill-me`.
- User insistence does not bypass Idea Gate 0 or Critical Gate 2.
- Only after `Critical Gate 2: confident` may this gateway present the direct execution vs retained plan recommendation; before that point, do not execute edits, commands, operational steps, or owner handoffs.
- After `Critical Gate 2: confident`, the recommendation must name the concrete consequence: specialized direct execution or retained-plan authoring.
- Do not run critical automatically after convergence; ask the user whether to continue.
- Do not create a retained plan automatically after a confident critical outcome; require explicit `go`/`ok`/`procedi` or equivalent approval.
- Use `internal-gateway-critical-master` before finalizing any substantive definition.
- Keep original intent and emerged requirements as separate tracks; do not rewrite emerged constraints as original user intent.
- After plan approval, load `internal-gateway-writing-plans`, create the retained plan, and stop before execution.

## State Machine

1. `Idea Gate 0`
2. `Interview Gate 1`
3. `Critical Gate 2`
4. `Plan Approval Gate 3`
5. `Handoff Gate 4`

State rules:

- If the incoming request is already concrete (file edit, command execution, validator run, or implementation step), start with `Specialization Checkpoint: gated` before Idea Gate 0.
- At `Specialization Checkpoint: gated`, name the recommended specialized owner (`internal-gateway-simple-task` by default, `internal-gateway-review` for defect-first review, `internal-gateway-critical-master` for pressure testing), but do not present the post-critical decision yet.
- Continue through the bounded evidence pass, mandatory `grill-me`, and critical gate before presenting the direct execution vs retained plan recommendation.
- Before the initial numbered block, keep large-file and large-log evidence compact: summarize counts, headers, anomalies, routes, and open gaps unless raw content is itself the missing evidence.
- After the evidence pass, load `grill-me` and ask one mandatory numbered bulk question block with recommendations and defaults.
- Before the initial numbered block, emit a compact facts/options summary derived from the bounded evidence pass.
- Ask further focused numbered bulk blocks only for unresolved, dependent, or reopened branches.
- Declare `Interview Gate 1: ready-for-critical` only when material branches are resolved, assumptions/defaults are visible and accepted, no ledger contradictions remain, and the validation path is identified.
- At `Interview Gate 1: ready-for-critical`, ask whether to continue before loading `internal-gateway-critical-master`.
- `Critical Gate 2` outcomes are: targeted reopen of affected branches, continue-critical, or confident completion.
- At `Critical Gate 2: confident`, emit the `Direct Execution vs Retained Plan Recommendation` before any handoff or plan approval question.
- Alias mapping is fixed: `mini-plan` means `compact` and `plan` means `extended`; retained-plan execution strategy is inferred by `internal-gateway-execute-plans`.
- At `Handoff Gate 4: plan-created`, set `Continuation: waiting` and do not execute.

## Direct Execution vs Retained Plan Recommendation

Use this recommendation only after `Critical Gate 2: confident`.

Recommend direct execution via `internal-gateway-simple-task` when the scoped
work is concrete, low-to-medium risk, one owner, one lane, one primary
validation path, no cross-turn dependency, and no material context-pressure
signal. Make clear that direct execution still belongs to the specialized
owner; this gateway does not execute it.

Recommend a retained plan when the user explicitly asked for a plan, the work
needs more than roughly 5-7 executable steps, touches more than roughly three
unrelated path families, has multiple independent validators, depends on
external approvals or pins, carries material context-pressure risk, or must stop
before execution. Recommend `compact` only when one owner, one lane, and one
validation path remain enough; otherwise recommend `extended`.

The user-facing message must use this shape:

1. `Recommendation:` direct execution via `internal-gateway-simple-task`, or a
   `compact`/`extended` retained plan.
2. `Why:` one evidence-based sentence naming the decisive signals.
3. `Tradeoff:` direct execution means same-chat specialized work after approval;
   retained plan means a durable handoff under `tmp/superpowers/` and no
   execution in this conversation.
4. `Decision:` ask the user to choose `execute`, `plan`, or an explicit
   override. If `plan` is chosen, require `go`/`ok`/`procedi` or equivalent
   approval before loading `internal-gateway-writing-plans`.

Avoid vague owner-retention phrasing. The message must name the concrete
consequence: direct execution handoff or retained-plan authoring.

## Flow

1. Specialization checkpoint
2. Discover
3. Converge
4. Ask before critical
5. Critical
6. Direct execution vs retained plan recommendation
7. Plan approval
8. Plan creation
9. Stop before execution

## Validation

- The gateway keeps `idea -> critical -> retained plan` in one conversation.
- Concrete execution requests trigger the specialization checkpoint and do not execute, transfer ownership, or present the post-critical recommendation until `grill-me` and critical both pass.
- User insistence does not bypass the `grill-me` or critical gates.
- `internal-gateway-writing-plans` owns profile selection.
- Execution stays a manual boundary after plan creation.
