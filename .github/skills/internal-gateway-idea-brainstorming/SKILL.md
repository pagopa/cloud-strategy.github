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
- `idea-refine`: optional support for raw multi-direction option shaping; load only when several credible concept directions remain.
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

- The target state, scope, owner, and validation path are already concrete enough to act; recommend `internal-gateway-simple-task` or the already-selected path.
- The user explicitly asks for `execute`, `apply-plan`, defect-first `review`, or critical challenge and the lane is already settled.
- A retained plan folder is already approved for execution; route to `internal-gateway-operational-flow` `apply-plan`.
- The request is catalog governance, consumer propagation, or broad sync maintenance rather than a pre-action fit decision.
- The request is purely operational mode ambiguity with no substantive ideation need; route to `internal-gateway-operational-flow`.

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
| `discover` | Idea, goal, or options are vague or unresolved. | Evidence pass, decision-ledger build, guided decision interview. | Skip evidence, ask bulk questions, or apply silent defaults. | `grill-me`, `idea-refine`, `superpowers-brainstorming` | Decision ledger, resolved branches, checkpoint state. |
| `converge` | Material branches are resolved and a compact decision ledger exists. | Summary, Definition Brief draft, `Interview checkpoint: ready-for-critical`. | Emit plan, apply changes, or imply execute approval. | `internal-gateway-critical-master` | Definition Brief, checkpoint state. |
| `critical` | Definition Brief is ready and needs mandatory challenge. | `confident` or `reopen`, visible next-owner recommendation. | Implement or routine-review. | `internal-gateway-critical-master` | Critical outcome, `Handoff checkpoint: ready-for-owner-change` when applicable. |
| `handoff` | Critical pass is `confident` and next owner is clear. | `Recommended next owner`, manual transition package. | Auto-dispatch or hidden router behavior. | `internal-agent-support-next-step` | Next-step package with owner, scope, action, validation, risk. |

## Core Invariants

- One active phase at a time.
- Load `grill-me` only for branch discovery after the evidence pass; load `idea-refine` or `superpowers-brainstorming` only when their distinct positive triggers are met.
- Return from any optional exploration support to this gateway before convergence, critical pass, or handoff.
- Keep direct entry and manual transitions visible. Do not create hidden front-door routers or hidden peer dispatch.
- Use `internal-agent-support-next-step` at every phase-ending transition.
- Non-terminal stops: start with `State:` and `Continuation:`; add `User action required:` when `Continuation` is `waiting`.
- Require an explicit checkpoint before moving into `plan`, `execute`, or peer transitions.
- Use `internal-gateway-critical-master` before finalizing any substantive definition.
- Missed work: compare request, ledger, diff, and evidence before closing.

## Guided Decision Interview

This gateway owns a native guided decision interview. Do not delegate the interview pacing to `grill-me` or reduce it to a bulk questionnaire.

1. **Inspect repository evidence first.** Read files, paths, commands, or existing decisions before asking the user.
2. **Build a compact decision ledger.** Order decisions by dependency. Record each branch, its status, and the evidence that resolved it.
3. **Ask one unresolved material decision question per turn.** Include a recommended answer, rationale, and explicit default when useful.
4. **Wait for the user's explicit answer.** Treat a clear affirmative reply as acceptance of the visible recommendation. Record the resolved branch before advancing.
5. **Do not treat branch confirmations as phase-transition checkpoints.** A branch answer updates the decision ledger; it does not automatically move to `converge` or `critical`.
6. **After all material branches resolve, summarize the compact decision ledger and wait at `Interview checkpoint: ready-for-critical`.**
7. **After a `confident` critical outcome, emit `Handoff checkpoint: ready-for-owner-change` only when recommending a peer transition.**
8. **When the critical pass or a later realignment reopens definition, resume only the affected branches** unless the impact is broad, and declare `Interview checkpoint: reopen`.

Interview depth is proportional: simple recoverable cases may close after a small number of questions, while unresolved dependent branches continue one turn at a time. Do not force a bulk initial questionnaire.

See `references/guided-decision-interview.md` for pacing, decision-ledger fields, proportional depth, reopen behavior, and checkpoint states.

## Phase Rules

### Discover

Run the smallest evidence pass that can recover target, candidate owner, nearby validation, and anti-scope.
Build the decision ledger. Use the guided decision interview to resolve material branches.

- Use `grill-me` only for branch-discovery interviews after the evidence pass.
- Use `idea-refine` only when the decision is genuinely exploratory rather than deterministic maintenance. See `references/compatibility-matrix.md` for `idea-refine` activation rules.
- Use `superpowers-brainstorming` only when a design or spec approval workflow is needed.
- Return from any optional exploration support to this gateway before convergence.

### Converge

When material branches are resolved, produce a Definition Brief:

- `Intent`: what the user is trying to decide or achieve.
- `Recovered evidence`: files, repository facts, or source facts used.
- `Resolved decisions`: branches closed through the interview or evidence.
- `Open decisions`: user-only decisions or `none`.
- `Direction or options`: the chosen path or the narrowed set.
- `Anti-scope`: what must not happen yet.
- `Validation path or gap`: command, review path, or explicit gap.
- `Stop & checkpoint`: where the agent must pause and the exact approval needed.

Before exiting `converge`, use Define Check 1-3, then emit `Interview checkpoint: ready-for-critical`.

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

Emit `Recommended next owner` with reason and a manual handoff. Include:

- `Owner`: exact next agent or skill owner.
- `Scope`: files, directories, artifacts, or decision surface in scope.
- `Action`: one concrete next action.
- `Validation`: command, review path, evidence, or explicit gap.
- `Risk`: residual risk, rollback note, or reason the transition should stay manual.
- `Continuation`: `continuing` or `waiting`.

For simple recoverable ideas that resolve directly, emit a chat-only `Simple Task Brief` instead of a retained plan artifact.

## Simple Task Brief

When the idea resolves to one quick concrete lane, emit a chat-only `Simple Task Brief`:

- `Target`: what should be done.
- `Action`: one concrete action.
- `Validation`: focused validation path or explicit gap.
- `Risk`: residual risk.
- `Next owner`: `internal-gateway-simple-task`.

Do not create a retained mini-plan for simple tasks.

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
- Load `internal-high-level-review` for plan-completion audit and scope-drift analysis.

## Validation

- Entry point and phase are explicit, or workflow falls back to `discover`.
- Every phase includes owner, scope, anti-scope, action, validation, risk, and checkpoint.
- The guided decision interview inspects evidence first, asks one material question per turn, exposes recommendation and rationale, waits for explicit answer, and records resolved branches.
- Branch answers do not create repeated phase-transition checkpoints.
- One `Interview checkpoint: ready-for-critical` after material branches resolve.
- One `Handoff checkpoint: ready-for-owner-change` only before peer owner change.
- Reopen resumes affected branches unless impact is broad.
- `grill-me` is used proportionally; `idea-refine` and `superpowers-brainstorming` are used only when distinct positive triggers apply.
- Optional exploration supports return to this gateway before convergence, critical pass, or handoff.
- The gateway recommends exactly one next owner when evidence supports a lane change.
- Simple tasks use a chat-only `Simple Task Brief`; no retained mini-plan is created.
- Manual handoffs remain visible; no hidden dispatch or front-door router exists.
