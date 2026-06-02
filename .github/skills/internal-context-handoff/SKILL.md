---
name: internal-context-handoff
description: Use when the user asks to create a context handoff, prepare resume context, save context for a new chat, or reconstruct a clean continuation package after long, polluted, or contradictory chat context.
---

# Internal Context Handoff

## Referenced skills

- `internal-agent-support-next-step`: compact owner-transition package; this skill separates cross-chat reconstruction from owner transitions.

Produce a token-efficient, paste-ready Markdown handoff that another agent can use as its first message in a new chat. Keep the workflow manual and handoff-only: do not auto-open sessions, continue the handed-off task, or silently write files.

## When to use

- The user asks to create a context handoff, prepare resume context, save context for a new chat, or reconstruct a continuation package.
- Chat context is long, polluted, contradictory, or compromised and a clean restart package is needed.
- Any discussion that needs a portable snapshot, not only repository work.

## When not to use

- The user needs a compact transition between already-selected owners. Use `internal-agent-support-next-step` instead.
- The user needs a Decision Brief for retained planning. Use `internal-agent-support-next-step` references/decision-brief.md.
- The task is a gateway phase change or non-terminal exit. Use the owning gateway skill.

## Workflow

1. Choose the compression level: `compact` by default. Escalate to `standard` when multi-step or technical continuation needs more detail, or `deep` when complex, high-risk, or contradictory state must be preserved. Use `references/handoff-template.md` for the exact Markdown shape and field-selection rules for each level.

2. Gather only continuation-critical information. Include only fields that apply to the current discussion. The template defines the available fields; do not force every field into every handoff.

3. For technical tasks, inspect accessible machine evidence: relevant files, Git status, validation results, active processes. Declare evidence gaps when inspection is impossible.

4. Exclude transcript narrative, superseded attempts, and easily recoverable details unless they explain an active risk. Redact secrets, credentials, tokens, and sensitive values with `[REDACTED]`. Preserve unresolved contradictions under `Open uncertainties` instead of choosing silently.

5. Emit the handoff as paste-ready Markdown in chat by default. Write `tmp/context-handoffs/<timestamp>-<slug>.md` only when the user explicitly requests file persistence. Avoid overwrites: append a numeric suffix when a target path already exists.

6. Include brief `Resume instructions` for the next agent. Stop after handoff creation. Do not execute the next task or open another session.

## Output boundary

The handoff is a portable reconstruction package. `internal-agent-support-next-step` remains the compact owner for transitions between already-selected owners. This skill does not choose the next owner, auto-dispatch, or bypass user approval.

## Validation

- Handoff is self-contained and paste-ready as a first message in a new chat.
- Default `compact` level is used unless omission would make continuation unreliable.
- Secrets and sensitive values are redacted.
- File persistence only when explicitly requested.
- `internal-agent-support-next-step` boundary is preserved.
