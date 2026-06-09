---
name: internal-gateway-idea-brainstorming
description: Use when a repository-owned request starts with a vague idea, unclear goal, unresolved option set, or needs substantive definition, convergence, or validated handoff before operational planning or simple execution.
---

# Internal Gateway Idea Brainstorming

## Referenced skills

Load these skills by name only when the active phase requires them. This list is an index, not a bundle to preload.
Treat every referenced skill as an on-demand dependency. Do not preload them
just because the request is still undecided; load only the owner proved by the
active uncertainty or next visible checkpoint.

- `grill-me`: branch-discovery and mandatory Idea Gate 0 interview method; load after every evidence pass before convergence or handoff.
- `superpowers-brainstorming`: optional support for design or spec approval workflows; load only when creative exploration is needed.
- `internal-gateway-critical-master`: mandatory critical challenge owner; load before finalizing any substantive definition.
- `internal-gateway-simple-task`: candidate next owner when the idea resolves to one quick concrete lane.
- `internal-gateway-operational-flow`: candidate next owner when the idea resolves to a validated Definition Brief that needs operational planning.
- `internal-agent-support-next-step`: handoff package formatting; load when a transition is ready.
- `internal-agent-support-lane-change-engine`: lane-change when the selected mode no longer fits.
- `internal-lesson-codification`: lesson routing before `LESSONS_LEARNED.md` changes.
- `superpowers-verification-before-completion`: final evidence gate.

Portable skill-first idea gateway. Copilot agents may wrap it; reusable idea-definition semantics live here.
This skill owns substantive idea work: evidence pass, guided decision interview, convergence, Definition Brief,
mandatory critical pass, and visible next-owner recommendation.

## When to use

- The user brings a vague idea, unclear goal, or unresolved option set.
- The user asks to compare owners, skills, agents, workflows, or AI assets before choosing a direction.
- The request has pre-action uncertainty about validation, anti-scope, rollout fit, or whether the work is overkill.
- The request may collapse to `internal-gateway-simple-task`, but that fit still needs to be proven through ideation.
- Brainstorming, clarification, or success criteria are needed before operational planning.

## When not to use

- The target state, scope, owner, and validation path are already concrete; recommend `internal-gateway-simple-task` or the already-selected path.
- The user explicitly asks for `execute`, `apply-plan`, defect-first `review`, or critical challenge and the lane is already settled.
- A retained plan folder is already approved for execution; route to `internal-gateway-operational-flow` `apply-plan`.
- The request is catalog governance, consumer propagation, or broad sync maintenance rather than a pre-action fit decision.
- Purely operational mode ambiguity with no substantive ideation need; route to `internal-gateway-operational-flow`.

## Entry Points

| Entrypoint | Use when | First active phase |
| --- | --- | --- |
| `idea-define` | Substantive idea needs definition, convergence, or handoff. | `discover` |
| `brainstorm` | Open-ended exploration with several credible directions. | `discover` |
| `clarify-first` | Success criteria or constraints are not yet confirmed. | `discover` |

## Phase State Machine

One active phase at a time. Each phase declares owner, scope, anti-scope, action, validation, risk, and checkpoint.

| Phase | Enters when | May do | Must not do | Delegates | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| `discover` | Idea, goal, or options are vague or unresolved. | Evidence pass, decision-ledger build, guided decision interview. | Skip evidence, ask unstructured questions, or apply silent defaults. | `grill-me`, `superpowers-brainstorming` | Idea Gate 0 (`grill-me required` or `grill-me satisfied`), decision ledger, resolved branches, checkpoint state. |
| `converge` | Material branches are resolved and Idea Gate 0 is `grill-me satisfied`. | Summary, Definition Brief draft, `Interview Gate 1: ready-for-critical`. | Emit plan, apply changes, recommend simple-task, recommend planning, or imply execute approval. | `internal-gateway-critical-master` | Definition Brief, checkpoint state. |
| `critical` | Definition Brief is ready and needs mandatory challenge. | `confident` or `reopen`, visible next-owner candidate. | Implement, routine-review, or recommend a next owner before the critical outcome is `confident`. | `internal-gateway-critical-master` | Critical Gate 2 outcome, `Handoff Gate 3: ready-for-owner-change` when applicable. |
| `handoff` | Critical Gate 2 is `confident` and next owner is clear. | `Recommended next owner`, manual transition package, explicit confirmation request. | Auto-dispatch, internal next-owner execution, hidden router behavior, simple-task execution, planning output, or file edits from implied consent. | `internal-agent-support-next-step` | Next-step package with owner, scope, action, validation, risk, `Continuation: waiting`, and active handoff lock. |

## Core Invariants

- One active phase at a time.
- Idea Gate 0 is mandatory after the evidence pass for every idea-gateway run. Declare `grill-me required` or `grill-me satisfied` before convergence, simple-task recommendation, operational-planning recommendation, or any next-owner handoff.
- Load `grill-me` for Idea Gate 0 after the evidence pass even when repository evidence seems complete; load `superpowers-brainstorming` only when its distinct positive trigger is met.
- Return from any optional exploration support to this gateway before convergence, critical pass, or handoff.
- Keep direct entry and manual transitions visible. Do not create hidden front-door routers or hidden peer dispatch.
- Stop and ask for explicit user confirmation before any next-owner transition. The user invokes `internal-gateway-simple-task` or `internal-gateway-operational-flow` manually in a separate turn.
- Treat `Continuation: waiting` as an active handoff lock. While locked, do not edit files, run delivery validation, invoke the next owner, or treat a user proposal as approval.
- Clear the handoff lock only when the user explicitly invokes the recommended owner or gives an unambiguous imperative approval for the named action and scope, such as "use `internal-gateway-simple-task` and modify X", "confermo, procedi con quella modifica", or "esegui/applica il next step".
- If the user's next message is a suggestion, alternative, preference, or design discussion, stay in this gateway, update the decision ledger or brief if needed, and ask for confirmation again before any delivery work.
- Use `internal-agent-support-next-step` at every phase-ending transition.
- Non-terminal stops: start with `State:` and `Continuation:`; add `User action required:` when `Continuation` is `waiting`.
- Require an explicit checkpoint before moving into `plan`, `execute`, or peer transitions.
- Use `internal-gateway-critical-master` before finalizing any substantive definition.
- Missed work: compare request, ledger, diff, and evidence before closing.

## Named Gates

| Gate | Blocks | Opens when | Required output |
| --- | --- | --- | --- |
| `Idea Gate 0` | Convergence, simple-task recommendation, planning recommendation, and next-owner handoff. | The user answers or explicitly accepts the `grill-me` question block for the current request, scope, context, and evidence. | `grill-me required` or `grill-me satisfied`. |
| `Interview Gate 1` | Critical challenge. | Idea Gate 0 is `grill-me satisfied` and all material branches are resolved. | `Interview Gate 1: ready-for-critical` or `Interview Gate 1: reopen`. |
| `Critical Gate 2` | Next-owner recommendation. | `internal-gateway-critical-master` returns a confident outcome against the Definition Brief. | `Critical Gate 2: confident` or `Critical Gate 2: reopen`. |
| `Handoff Gate 3` | Planning, simple-task execution, delivery validation, and file edits by the next owner. | Critical Gate 2 is `confident` and the next owner package is ready. The lock clears only after explicit user invocation or unambiguous approval for the named owner, action, and scope. | `Handoff Gate 3: ready-for-owner-change`, `Continuation: waiting`, and `User action required`. |

## Guided Decision Interview

This gateway uses `grill-me` for a guided decision interview in iterative numbered question blocks.

Contract markers preserved in core: `Interview checkpoint: ready-for-critical`, `Interview checkpoint: reopen`, and `Handoff checkpoint: ready-for-owner-change` remain the portable checkpoint aliases for the gate states below.

**Core pacing**: Inspect repository evidence first. Build a compact decision ledger ordered by dependency. Load `grill-me`, then immediately ask one numbered Idea Gate 0 question block. Include unresolved material decisions and at least one human confirmation question when the evidence appears complete. Each question includes a recommendation, rationale, and default when useful. Treat visible recommendations as accepted unless the user overrides them by question number or gives different direction. After the user's bulk response, ask another numbered question block when unresolved ambiguity, dependent follow-up decisions, or reopened branches remain. Do not treat branch confirmations as phase-transition checkpoints.

After all material branches resolve and Idea Gate 0 is `grill-me satisfied`, emit `Interview Gate 1: ready-for-critical`. The portable alias is `Interview checkpoint: ready-for-critical`. After `Critical Gate 2: confident`, emit `Handoff Gate 3: ready-for-owner-change` only when recommending a peer transition. The portable alias is `Handoff checkpoint: ready-for-owner-change`. When the critical pass or realignment reopens definition, resume only the affected branches unless impact is broad, and declare `Interview Gate 1: reopen`. The portable alias is `Interview checkpoint: reopen`.

Interview depth is proportional after the mandatory gate exists: simple cases may close after one block, but no case may skip Idea Gate 0. Unresolved dependent branches continue in focused follow-up blocks. Do not fall back to one-question-per-turn pacing.

See `references/guided-decision-interview.md` for full pacing rules, decision-ledger fields, and checkpoint state definitions.

## Phase Rules

### Discover

Run the smallest evidence pass that can recover target, candidate owner, nearby validation, and anti-scope.
Build the decision ledger. Use the guided decision interview to resolve material branches.

- Use `grill-me` for mandatory Idea Gate 0 after the evidence pass. Ask unresolved user-only decisions, and ask for human confirmation when the recovered evidence seems complete.
- When several credible concept directions remain, read `references/idea-shaping-frameworks.md` and `references/idea-evaluation-criteria.md` selectively before convergence.
- Use `superpowers-brainstorming` only when a design or spec approval workflow is needed.
- Return from any optional exploration support to this gateway before convergence.

#### Material Evidence Completeness

Before convergence or recommending a next owner, confirm that material evidence axes proved relevant by the prompt, path, cross-boundary claim, or repository evidence have been inspected. Relevant axes include runtime, data or freshness, routing, propagation, and validation when the claim depends on them.

- Treat the axes as a decision aid, not a mandatory universal checklist. Small local ideas are not forced through irrelevant axes.
- Record unresolved material evidence gaps explicitly in the decision ledger or Definition Brief before finalizing.
- Stop exploration when material axes are resolved or explicitly recorded as gaps, the next decision is identified, and one validation path exists.

### Converge

When material branches are resolved and Idea Gate 0 is `grill-me satisfied`, produce a Definition Brief with these fields: `Intent`, `Recovered evidence`, `Resolved decisions`, `Open decisions`, `Direction or options`, `Anti-scope`, `Validation path or gap`, `Risk`, and `Stop & checkpoint`. See `references/brief-contract.md` for the full field contract.

### Critical

After `Interview Gate 1: ready-for-critical`, automatically load `internal-gateway-critical-master` and run a critical challenge against the Definition Brief. Mandatory. Do not skip it.

Declare `Critical Gate 2: confident` or `Critical Gate 2: reopen`. When `reopen`, return to `discover` and resume affected branches.

- **Confident**: declare `Critical Gate 2: confident`, prepare handoff.
- **Reopen**: declare `Critical Gate 2: reopen`, present objection, re-enter `discover`. Resume only affected branches unless impact is broad.

Do not loop more than twice without explicit user decision.

### Handoff

When findings leave material remediation decisions open, run a new Idea Gate 0 `grill-me` interview before recommending planning or delivery. Repository evidence never waives this gate; it only narrows the question set.

When `Critical Gate 2: confident`, recommend exactly one next owner:

- `internal-gateway-simple-task` when the idea resolved to one quick concrete lane.
- `internal-gateway-operational-flow` `plan` when a validated Definition Brief needs operational planning.
- `internal-gateway-critical-master` when assumptions need deeper pressure-testing.
- Continue idea definition when unresolved branches remain.

Emit `Handoff Gate 3: ready-for-owner-change` and `Recommended next owner` with reason and a manual handoff. Include `Owner`, `Scope`, `Action`, `Validation`, `Risk`, `Continuation: waiting`, and `User action required`. Stop after the recommendation. Do not invoke, simulate, or execute the next owner internally. The user must confirm the next gate and invoke `internal-gateway-simple-task` or `internal-gateway-operational-flow` manually in a separate turn. See `references/brief-contract.md` for the field contract.

After stopping, keep the handoff lock active across the next user turn. A message that proposes content, wording, scope, or implementation detail is not confirmation by itself. If confirmation is missing or ambiguous, respond with the current state, the recommended owner, and one direct confirmation question; do not perform edits in that turn.

## Simple Task Brief

When the idea resolves to one quick concrete lane, keep simple-task handoff blocked until Idea Gate 0 is `grill-me satisfied` and Critical Gate 2 is `confident`. Then emit a chat-only `Simple Task Brief` with `Target`, `Action`, `Validation`, `Risk`, and `Next owner`: `internal-gateway-simple-task`. Do not create a retained mini-plan for simple tasks. See `references/brief-contract.md` for the field contract.

## Routing Fallback Rules

- Substantive idea, goal, or option ambiguity selects this gateway.
- Operational mode ambiguity selects `internal-gateway-operational-flow`.
- Mixed unclassifiable ambiguity selects `internal-gateway-operational-flow` conservatively, which may then recommend this gateway visibly.

## Compatibility Matrix

See `references/compatibility-matrix.md` for the full matrix covering `direct execute`, `apply-plan`, `review`, `plan-only`, `full-cycle`, validated Definition Brief intake, and operational versus substantive realignment.

## References

Read on demand, not as a default bundle.

- `references/guided-decision-interview.md`: interview pacing, ledger fields, checkpoint states.
- `references/compatibility-matrix.md`: routing matrix for all entrypoints and realignment cases.
- `references/brief-contract.md`: Definition Brief, Simple Task Brief, and recommended-next-owner field contracts.
- `references/idea-shaping-frameworks.md`: optional divergent lenses for concept-heavy exploration.
- `references/idea-evaluation-criteria.md`: optional evaluation rubric for narrowing credible concept directions.
- Load `internal-high-level-review` for plan-completion audit and scope-drift analysis.

## Validation

- Entry point and phase are explicit, or workflow falls back to `discover`.
- Every phase includes owner, scope, anti-scope, action, validation, risk, and checkpoint.
- The guided decision interview inspects evidence first, always asks an Idea Gate 0 numbered question block through `grill-me`, exposes recommendation and rationale, records accepted defaults or overrides, and records resolved branches.
- Branch answers do not create repeated phase-transition checkpoints.
- One `Interview Gate 1: ready-for-critical` after material branches resolve and Idea Gate 0 is `grill-me satisfied`.
- One `Critical Gate 2: confident` before next-owner recommendation.
- One `Handoff Gate 3: ready-for-owner-change` only before peer owner change.
- Reopen resumes affected branches unless impact is broad.
- `grill-me` is mandatory for Idea Gate 0; depth after the initial gate is proportional. `superpowers-brainstorming` is used only when its distinct positive trigger applies.
- Optional exploration supports return to this gateway before convergence, critical pass, or handoff.
- The gateway recommends exactly one next owner when evidence supports a lane change.
- Every next-owner recommendation stops with `Continuation: waiting` and asks for explicit user confirmation; the gateway does not execute the recommended owner internally.
- The handoff lock is enforced after `Continuation: waiting`: proposals, refinements, or preferences do not clear it unless the user also gives explicit approval for the named owner/action/scope.
- Simple tasks remain blocked until Idea Gate 0 is `grill-me satisfied` and Critical Gate 2 is `confident`; then they use a chat-only `Simple Task Brief` and no retained mini-plan is created.
- Manual handoffs remain visible; no hidden dispatch or front-door router exists.
- Run `scripts/audit_contract.py --format json` for deterministic bundle token and marker evidence.
