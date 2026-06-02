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

- `grill-me`: branch-discovery method; load when unresolved branches need user interview after evidence pass.
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
| `discover` | Idea, goal, or options are vague or unresolved. | Evidence pass, decision-ledger build, guided decision interview. | Skip evidence, ask unstructured questions, or apply silent defaults. | `grill-me`, `superpowers-brainstorming` | Decision ledger, resolved branches, checkpoint state. |
| `converge` | Material branches are resolved and a compact decision ledger exists. | Summary, Definition Brief draft, `Interview checkpoint: ready-for-critical`. | Emit plan, apply changes, or imply execute approval. | `internal-gateway-critical-master` | Definition Brief, checkpoint state. |
| `critical` | Definition Brief is ready and needs mandatory challenge. | `confident` or `reopen`, visible next-owner recommendation. | Implement or routine-review. | `internal-gateway-critical-master` | Critical outcome, `Handoff checkpoint: ready-for-owner-change` when applicable. |
| `handoff` | Critical pass is `confident` and next owner is clear. | `Recommended next owner`, manual transition package, explicit confirmation request. | Auto-dispatch, internal next-owner execution, or hidden router behavior. | `internal-agent-support-next-step` | Next-step package with owner, scope, action, validation, risk, and `Continuation: waiting`. |

## Core Invariants

- One active phase at a time.
- Load `grill-me` only for branch discovery after the evidence pass; load `superpowers-brainstorming` only when its distinct positive trigger is met.
- Return from any optional exploration support to this gateway before convergence, critical pass, or handoff.
- Keep direct entry and manual transitions visible. Do not create hidden front-door routers or hidden peer dispatch.
- Stop and ask for explicit user confirmation before any next-owner transition. The user invokes `internal-gateway-simple-task` or `internal-gateway-operational-flow` manually in a separate turn.
- Use `internal-agent-support-next-step` at every phase-ending transition.
- Non-terminal stops: start with `State:` and `Continuation:`; add `User action required:` when `Continuation` is `waiting`.
- Require an explicit checkpoint before moving into `plan`, `execute`, or peer transitions.
- Use `internal-gateway-critical-master` before finalizing any substantive definition.
- Missed work: compare request, ledger, diff, and evidence before closing.

## Guided Decision Interview

This gateway uses `grill-me` for a guided decision interview in iterative numbered question blocks.

**Core pacing**: Inspect repository evidence first. Build a compact decision ledger ordered by dependency. Load `grill-me`, then immediately ask the unresolved material decisions in one numbered question block. Each question includes a recommendation, rationale, and default when useful. Treat visible recommendations as accepted unless the user overrides them by question number or gives different direction. After the user's bulk response, ask another numbered question block when unresolved ambiguity, dependent follow-up decisions, or reopened branches remain. Do not treat branch confirmations as phase-transition checkpoints.

After all material branches resolve, emit `Interview checkpoint: ready-for-critical`. After a `confident` critical outcome, emit `Handoff checkpoint: ready-for-owner-change` only when recommending a peer transition. When the critical pass or realignment reopens definition, resume only the affected branches unless impact is broad, and declare `Interview checkpoint: reopen`.

Interview depth is proportional: simple cases may close after one block; unresolved dependent branches continue in focused follow-up blocks. Do not fall back to one-question-per-turn pacing.

See `references/guided-decision-interview.md` for full pacing rules, decision-ledger fields, and checkpoint state definitions.

## Phase Rules

### Discover

Run the smallest evidence pass that can recover target, candidate owner, nearby validation, and anti-scope.
Build the decision ledger. Use the guided decision interview to resolve material branches.

- Use `grill-me` only for branch-discovery interviews after the evidence pass.
- When several credible concept directions remain, read `references/idea-shaping-frameworks.md` and `references/idea-evaluation-criteria.md` selectively before convergence.
- Use `superpowers-brainstorming` only when a design or spec approval workflow is needed.
- Return from any optional exploration support to this gateway before convergence.

### Converge

When material branches are resolved, produce a Definition Brief with these fields: `Intent`, `Recovered evidence`, `Resolved decisions`, `Open decisions`, `Direction or options`, `Anti-scope`, `Validation path or gap`, and `Stop & checkpoint`. See `references/brief-contract.md` for the full field contract.

### Critical

After `Interview checkpoint: ready-for-critical`, automatically load `internal-gateway-critical-master` and run a critical challenge against the Definition Brief. Mandatory. Do not skip it.

Declare `pre-plan critical: confident` or `pre-plan critical: reopen`. When `reopen`, return to `discover` and resume affected branches.

- **Confident**: declare `pre-plan critical: confident`, prepare handoff.
- **Reopen**: present objection, re-enter `discover`. Resume only affected branches unless impact is broad.

Do not loop more than twice without explicit user decision.

### Handoff

When `pre-plan critical: confident`, recommend exactly one next owner:

- `internal-gateway-simple-task` when the idea resolved to one quick concrete lane.
- `internal-gateway-operational-flow` `plan` when a validated Definition Brief needs operational planning.
- `internal-gateway-critical-master` when assumptions need deeper pressure-testing.
- Continue idea definition when unresolved branches remain.

Emit `Recommended next owner` with reason and a manual handoff. Include `Owner`, `Scope`, `Action`, `Validation`, `Risk`, `Continuation: waiting`, and `User action required`. Stop after the recommendation. Do not invoke, simulate, or execute the next owner internally. The user must confirm the next gate and invoke `internal-gateway-simple-task` or `internal-gateway-operational-flow` manually in a separate turn. See `references/brief-contract.md` for the field contract.

## Simple Task Brief

When the idea resolves to one quick concrete lane, emit a chat-only `Simple Task Brief` with `Target`, `Action`, `Validation`, `Risk`, and `Next owner`: `internal-gateway-simple-task`. Do not create a retained mini-plan for simple tasks. See `references/brief-contract.md` for the field contract.

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
- The guided decision interview inspects evidence first, asks iterative numbered question blocks through `grill-me`, exposes recommendation and rationale, records accepted defaults or overrides, and records resolved branches.
- Branch answers do not create repeated phase-transition checkpoints.
- One `Interview checkpoint: ready-for-critical` after material branches resolve.
- One `Handoff checkpoint: ready-for-owner-change` only before peer owner change.
- Reopen resumes affected branches unless impact is broad.
- `grill-me` is used proportionally; `superpowers-brainstorming` is used only when its distinct positive trigger applies.
- Optional exploration supports return to this gateway before convergence, critical pass, or handoff.
- The gateway recommends exactly one next owner when evidence supports a lane change.
- Every next-owner recommendation stops with `Continuation: waiting` and asks for explicit user confirmation; the gateway does not execute the recommended owner internally.
- Simple tasks use a chat-only `Simple Task Brief`; no retained mini-plan is created.
- Manual handoffs remain visible; no hidden dispatch or front-door router exists.
- Run `scripts/audit_contract.py --format json` for deterministic bundle token and marker evidence.
