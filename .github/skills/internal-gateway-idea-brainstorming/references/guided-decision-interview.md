# Guided Decision Interview

Use this reference when `internal-gateway-idea-brainstorming` needs the exact pacing, decision-ledger fields, and checkpoint states for its native guided decision interview.

## Pacing Rules

1. Inspect repository evidence before asking the user. Use files, paths, commands, and existing repository decisions first.
2. Maintain a compact decision ledger ordered by dependency. Resolve prerequisite branches before dependent branches.
3. Ask one unresolved material decision question per turn. Each question must include a recommended answer, rationale, and explicit default when useful.
4. Wait for the user's explicit answer before resolving the branch. Treat a clear affirmative reply as acceptance of the visible recommendation.
5. Record each resolved branch in the decision ledger before advancing.
6. Do not treat branch confirmations as phase-transition checkpoints.
7. After all material branches resolve, summarize the compact decision ledger and declare `Interview checkpoint: ready-for-critical`.
8. After a `confident` critical outcome, declare `Handoff checkpoint: ready-for-owner-change` only when recommending a peer transition.
9. When a reopen occurs, resume only the affected branches unless the impact is broad, and declare `Interview checkpoint: reopen`.

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
| `ready-for-owner-change` | Confident critical outcome; ready to recommend next owner. | Only before a peer transition; not after every branch resolution. |

## Proportional Depth

- Simple recoverable cases may close after a small number of questions.
- Unresolved dependent branches continue one turn at a time.
- Do not force a bulk initial questionnaire.
- Do not silently accept defaults.
- Do not ask questions that repository evidence already answers.

## grill-me Boundary

- Use `grill-me` for branch discovery when the evidence pass leaves unresolved user-only decisions.
- Do not inherit `grill-me`'s bulk-question default.
- This gateway owns its evidence-first, one-question-per-turn pacing locally.
