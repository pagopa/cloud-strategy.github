# Guided Decision Interview

Use this reference when `internal-gateway-idea-brainstorming` needs the exact pacing, decision-ledger fields, and checkpoint states for its native guided decision interview.

## Pacing Rules

1. Inspect repository evidence before asking the user. Use files, paths, commands, and existing repository decisions first.
2. Maintain a compact decision ledger ordered by dependency. Resolve prerequisite branches before dependent branches.
3. Load `grill-me`, then immediately ask the unresolved material decisions in one numbered question block. Order the block by dependency.
4. For each numbered question, include a recommendation, rationale, and explicit default when useful.
5. Treat visible recommendations as accepted unless the user overrides them by question number or gives different direction.
6. Record accepted defaults and overrides in the decision ledger before advancing.
7. After the user's bulk response, ask another numbered question block only for unresolved ambiguity, dependent follow-up decisions, or reopened branches.
8. Do not treat branch confirmations as phase-transition checkpoints.
9. After all material branches resolve, summarize the compact decision ledger and declare `Interview checkpoint: ready-for-critical`.
10. After a `confident` critical outcome, declare `Handoff checkpoint: ready-for-owner-change` only when recommending a peer transition.
11. Treat `Continuation: waiting` as a handoff lock after `ready-for-owner-change`; proposals, alternatives, or wording preferences do not clear the lock without explicit owner/action/scope approval.
12. When a reopen occurs, resume only the affected branches unless the impact is broad, and declare `Interview checkpoint: reopen`.

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

## Checkpoint States

| State | Meaning | When to declare |
| --- | --- | --- |
| `interviewing` | Active question in progress. | While awaiting a user answer to a material decision question. |
| `ready-for-critical` | All material branches resolved; waiting for critical challenge. | After decision-ledger summary and before loading `internal-gateway-critical-master`. |
| `reopen` | Critical pass or realignment reopened one or more branches. | When resuming affected branches after `reopen`. |
| `ready-for-owner-change` | Confident critical outcome; ready to recommend the next owner and stop with a handoff lock. | Only before a peer transition; the user confirms and invokes the next owner manually in a separate turn. |

## Proportional Depth

- Simple recoverable cases may close after a small number of questions.
- Unresolved dependent branches continue in focused numbered follow-up blocks.
- Ask the initial numbered question block immediately after the evidence pass.
- Make accepted defaults visible in the decision ledger.
- Do not ask questions that repository evidence already answers.

## grill-me Boundary

- Use `grill-me` for branch discovery when the evidence pass leaves unresolved user-only decisions.
- Inherit `grill-me`'s numbered initial question block and default-acceptance behavior.
- Declare the caller-owned override for iterative numbered follow-up blocks when using `grill-me` for branch discovery.
- Keep the interview iterative by asking focused follow-up blocks when later branches remain.
