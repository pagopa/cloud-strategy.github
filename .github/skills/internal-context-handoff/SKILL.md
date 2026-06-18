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

1. Pick compression level. Default `compact`; use `standard` for multi-step, technical, or long polluted continuation; use `deep` for complex, high-risk, or contradictory state. See `references/handoff-template.md` for field shape and selection rules.

2. Gather only continuation-critical fields. Omit non-applicable fields entirely; do not write `None.` for absent fields. The template lists available fields. If source priority cannot be inferred from evidence and omission would misroute the next agent, ask one optional source-priority question.

3. For technical tasks, inspect machine evidence: files, Git status, validation results, active processes. Record checked sources, material deltas, and the next check when they reduce restart cost. Declare evidence gaps when inspection is impossible.

4. Exclude transcript narrative, superseded attempts, and easily recoverable detail unless they explain an active risk. Redact secrets, credentials, tokens, and sensitive values with `[REDACTED]`. Preserve unresolved contradictions under `Open uncertainties`; do not choose silently.

5. Emit as paste-ready Markdown in chat by default. Persist to `tmp/context-handoffs/<timestamp>-<slug>.md` only when the user explicitly requests it; append a numeric suffix if the target path already exists.

6. Add brief `Resume instructions`. Stop after handoff creation. Do not execute the next task or open another session.

## Output boundary

The handoff is a portable reconstruction package. `internal-agent-support-next-step` remains the compact owner for transitions between already-selected owners. This skill does not choose the next owner, auto-dispatch, or bypass user approval.
