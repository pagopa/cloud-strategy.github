# Guided Decision Interview

Use this reference when `internal-gateway-idea-brainstorming` needs the exact pacing, decision-ledger fields, and checkpoint states for its native guided decision interview.

## Pacing Rules

1. If the request is already concrete (file edit, command run, validator run, or direct implementation), emit `Specialization Checkpoint: waiting`, ask whether the user is sure to keep this owner, explain why a specialized owner is safer, and recommend the next owner before continuing.
1. Inspect repository evidence before asking the user. Use files, paths, commands, and existing repository decisions first.
2. Maintain a compact decision ledger ordered by dependency. Resolve prerequisite branches before dependent branches.
3. Load `grill-me`, then immediately ask one mandatory Idea Gate 0 numbered question block. Order unresolved decisions by dependency, and include at least one human confirmation question when repository evidence appears complete.
4. For each numbered question, include a recommendation, rationale, and explicit default when useful.
5. Treat visible recommendations as accepted unless the user overrides them by question number or gives different direction.
6. Record accepted defaults and overrides in the decision ledger before advancing.
7. After the user's bulk response, declare Idea Gate 0 as `grill-me required` or `grill-me satisfied`. Ask another numbered question block only for unresolved ambiguity, dependent follow-up decisions, or reopened branches.
8. Do not treat branch confirmations as phase-transition checkpoints.
9. After all material branches resolve and Idea Gate 0 is `grill-me satisfied`, summarize the compact decision ledger and declare `Interview Gate 1: ready-for-critical` only when assumptions/defaults are accepted, no ledger contradictions remain, and the validation path is identified.
10. At `Interview Gate 1: ready-for-critical`, ask whether to continue to critical before loading `internal-gateway-critical-master`.
11. When a reopen occurs, resume only the affected branches unless the impact is broad, and declare `Interview Gate 1: reopen`.
12. After `Critical Gate 2: confident`, declare `Plan Approval Gate 3: waiting` and ask for explicit `go`/`ok`/`procedi` or equivalent approval before loading `internal-gateway-writing-plans`.
13. Only after explicit approval, declare `Plan Approval Gate 3: approved`, create the retained plan, then declare `Handoff Gate 4: plan-created`.
14. Treat `Continuation: waiting` as a handoff lock after `Handoff Gate 4: plan-created`; proposals, alternatives, or wording preferences do not clear the lock without explicit owner/action/scope approval.

## Decision Ledger Fields

Each row in the decision ledger:

| Field | Purpose |
| --- | --- |
| `Branch` | The decision being resolved. |
| `Status` | `open`, `resolved`, `reopened`. |
| `Evidence` | Repository facts, file states, or commands that inform the branch. |
| `Recommendation` | The recommended answer and rationale. |
| `User answer` | The explicit user reply, or `pending`. |
| `Impact` | `local` or `broad`; used during reopen to decide branch scope. |
| `Gate` | The active gate affected by the branch: `Idea Gate 0`, `Interview Gate 1`, `Critical Gate 2`, `Plan Approval Gate 3`, or `Handoff Gate 4`. |

## Checkpoint States

| State | Meaning | When to declare |
| --- | --- | --- |
| `Specialization Checkpoint: waiting` | The incoming ask is concrete and must confirm this non-specialized owner before proceeding. | Before Idea Gate 0 when the user asks for direct execution-oriented work. |
| `Idea Gate 0: grill-me required` | Mandatory human confirmation loop is open. | After the evidence pass and before convergence, simple-task recommendation, planning recommendation, or handoff. |
| `Idea Gate 0: grill-me satisfied` | User answered or explicitly accepted defaults for the current request, scope, context, and evidence. | Before convergence or any simple-task/planning recommendation. |
| `Interview Gate 1: ready-for-critical` | All material branches resolved; waiting for critical challenge. | After decision-ledger summary and before loading `internal-gateway-critical-master`. |
| `Interview Gate 1: reopen` | Critical pass or realignment reopened one or more branches. | When resuming affected branches after `reopen`. |
| `Critical Gate 2: confident` | Critical challenge found the Definition Brief fit for handoff. | Before recommending the next owner. |
| `Critical Gate 2: reopen` | Critical challenge found material issues. | Before returning to affected branches in `discover`. |
| `Plan Approval Gate 3: waiting` | Critical is confident but planning approval is pending. | Immediately after `Critical Gate 2: confident` and before loading `internal-gateway-writing-plans`. |
| `Plan Approval Gate 3: approved` | Explicit plan approval was received. | After explicit `go`/`ok`/`procedi` or equivalent approval. |
| `Handoff Gate 4: plan-created` | Retained plan was created and execution is blocked. | After plan creation with `Continuation: waiting` and stop-before-execution behavior. |

## Plan Alias Mapping

- `mini-plan` maps to canonical `compact` and recommended consumer `internal-gateway-simple-task`.
- `plan` maps to canonical `extended` and recommended consumer `internal-gateway-execute-plans`.
- Alias labels are conversational only; canonical profile terms remain `compact` and `extended`.

## Proportional Depth

- Concrete direct asks must pass `Specialization Checkpoint: waiting` first unless the user explicitly confirms they still want this owner.
- Simple recoverable cases may close after a small number of questions, but they still require Idea Gate 0.
- Unresolved dependent branches continue in focused numbered follow-up blocks.
- Ask the initial numbered question block immediately after the evidence pass.
- Make accepted defaults visible in the decision ledger.
- Do not ask questions that repository evidence already answers.

## grill-me Boundary

- Use `grill-me` for mandatory Idea Gate 0 after every evidence pass.
- Inherit `grill-me`'s numbered initial question block and default-acceptance behavior.
- Declare the caller-owned override for iterative numbered follow-up blocks when using `grill-me` for branch discovery.
- Keep the interview iterative by asking focused follow-up blocks when later branches remain.
- Do not skip `grill-me` just because files, docs, or local evidence appear sufficient. Use evidence to reduce the questions, then ask the human to confirm the recovered direction.
