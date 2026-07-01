# Guided Decision Interview

Use this reference when `internal-gateway-idea-brainstorming` needs the exact pacing, decision-ledger fields, and checkpoint states for its native guided decision interview.

## Pacing Rules

1. If the request is already concrete (file edit, command run, validator run, or direct implementation), emit `Specialization Checkpoint: gated`, explain that this owner cannot decide task ownership or execute yet, name the recommended specialized owner for later, and continue with the bounded evidence pass plus mandatory Idea Gate 0.
1. Run a bounded evidence pass before asking the user. Use the smallest risk-ordered repository evidence first (files, paths, commands, and existing decisions).
1. When authoritative platform semantics control the decision, verify them early inside the bounded evidence pass.
1. Maintain a compact decision ledger ordered by dependency. Resolve prerequisite branches before dependent branches.
1. Before the first numbered block, emit a compact facts/options summary grounded in the bounded evidence pass.
1. Load `grill-me`, then immediately ask one mandatory Idea Gate 0 numbered question block. Order unresolved decisions by dependency, and include at least one human confirmation question when repository evidence appears complete.
1. For each numbered question, include a recommendation, rationale, and explicit default when useful.
1. Treat visible recommendations as accepted unless the user overrides them by question number or gives different direction.
1. Record accepted defaults and overrides in the decision ledger before advancing.
1. Preserve intent traceability in the ledger by keeping original intent and emerged requirements separate; do not restate emerged constraints as original intent.
1. After the user's bulk response, declare Idea Gate 0 as `grill-me required` or `grill-me satisfied`. Ask another numbered question block only for unresolved ambiguity, dependent follow-up decisions, or reopened branches.
1. Do not treat branch confirmations as phase-transition checkpoints.
1. After all material branches resolve and Idea Gate 0 is `grill-me satisfied`, summarize the compact decision ledger and declare `Interview Gate 1: ready-for-critical` only when assumptions/defaults are accepted, no ledger contradictions remain, and the validation path is identified.
1. At `Interview Gate 1: ready-for-critical`, ask whether to continue to critical before loading `internal-gateway-critical-master`.
1. When a reopen occurs, resume only the affected branches unless the impact is broad, and declare `Interview Gate 1: reopen`.
1. After `Critical Gate 2: confident`, emit the `Direct Execution vs Retained Plan Recommendation`: `Recommendation`, `Why`, `Tradeoff`, and `Decision`. Recommend direct execution via `internal-gateway-simple-task` when the work is concrete, one owner, one lane, one validation path, and low context risk. Recommend a `compact` or `extended` retained plan when the user asked for one, the work is broad enough to retain, validation is multi-surface, or context pressure could interrupt verified execution.
1. Avoid vague owner-retention phrasing. The user chooses `execute` for specialized direct execution, `plan` for retained-plan authoring, or an explicit override. Only if the user chooses `plan`, declare `Plan Approval Gate 3: waiting` and ask for explicit `go`/`ok`/`procedi` or equivalent approval before loading `internal-gateway-writing-plans`.
1. Only after explicit approval, declare `Plan Approval Gate 3: approved`, create the retained plan, then declare `Handoff Gate 4: plan-created`.
1. Treat `Continuation: waiting` as a handoff lock after `Handoff Gate 4: plan-created`; proposals, alternatives, or wording preferences do not clear the lock without explicit owner/action/scope approval.

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
| `Specialization Checkpoint: gated` | The incoming ask is concrete, but this owner may not decide ownership or execute until `grill-me` and critical both pass. | Before Idea Gate 0 when the user asks for direct execution-oriented work. |
| `Idea Gate 0: grill-me required` | Mandatory human confirmation loop is open. | After the evidence pass and before convergence, simple-task recommendation, planning recommendation, or handoff. |
| `Idea Gate 0: grill-me satisfied` | User answered or explicitly accepted defaults for the current request, scope, context, and evidence. | Before convergence or any simple-task/planning recommendation. |
| `Interview Gate 1: ready-for-critical` | All material branches resolved; waiting for critical challenge. | After decision-ledger summary and before loading `internal-gateway-critical-master`. |
| `Interview Gate 1: reopen` | Critical pass or realignment reopened one or more branches. | When resuming affected branches after `reopen`. |
| `Critical Gate 2: confident` | Critical challenge found the Definition Brief fit for handoff and unlocked the direct execution vs retained plan recommendation. | Before asking the user to choose `execute`, `plan`, or an explicit override. |
| `Critical Gate 2: reopen` | Critical challenge found material issues. | Before returning to affected branches in `discover`. |
| `Plan Approval Gate 3: waiting` | Critical is confident, the user chose retained-plan authoring, and planning approval is pending. | Immediately after `Critical Gate 2: confident` and after the user chooses `plan`. |
| `Plan Approval Gate 3: approved` | Explicit plan approval was received. | After explicit `go`/`ok`/`procedi` or equivalent approval. |
| `Handoff Gate 4: plan-created` | Retained plan was created and execution is blocked. | After plan creation with `Continuation: waiting` and stop-before-execution behavior. |

## Plan Alias Mapping

- `mini-plan` maps to canonical `compact`.
- `plan` maps to canonical `extended`.
- Retained-plan execution strategy is inferred later by `internal-gateway-execute-plans` from profile, folder shape, and validation path.
- Alias labels are conversational only; canonical profile terms remain `compact` and `extended`.

## Proportional Depth

- Concrete direct asks must pass `Specialization Checkpoint: gated` first. User insistence does not bypass Idea Gate 0 or Critical Gate 2.
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
- Do not let a concrete-task request or owner preference bypass the `grill-me` boundary.
- Do not skip `grill-me` just because files, docs, or local evidence appear sufficient. Use evidence to reduce the questions, then ask the human to confirm the recovered direction.
