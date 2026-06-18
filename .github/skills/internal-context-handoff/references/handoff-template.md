# Handoff Template

Load this reference when the skill body directs field-selection rules or adaptive compression shape.

## Field-selection rules (all profiles)

- Include only fields that apply to the current discussion.
- Prefer concrete over speculative: include only what is known, decided, or observably pending.
- Redact secrets, credentials, tokens, keys, and sensitive values with `[REDACTED]`.
- Cite file paths, command output, or validation evidence when available.
- Declare evidence gaps explicitly instead of guessing.
- For long, polluted, or contradictory context, prefer checked sources and
  state deltas over transcript recap.

## Compact (default)

Use for single-step discussions, simple questions, or when the next agent needs minimal context.

```markdown
## Context handoff

**Goal:** [one-line primary objective]
**Current state:** [one-line status]
**Key decisions:** [bulleted list or "None."]
**Anti-scope:** [what to avoid, or "None."]
**Next step:** [one concrete action]
**Resume instructions:** [one-line guidance for the next agent]
```

## Standard

Use for multi-step technical work, repository tasks, or when evidence gaps matter.

Add these fields after `Key decisions` and before `Anti-scope` when they
materially reduce restart cost:

```markdown
**Primary source to trust first:** [authoritative artifact, file, command, or "Not established."]
**Checked sources:** [files, commands, branches, logs, or "None inspected."]
**Delta since last stable state:** [what changed since the last reliable checkpoint, or "None."]
**Evidence:**
  - [validations run, command output, or "None available."]
  - Git: [branch, status summary, or "Not inspected."]
**Unfinished work:** [bulleted list or "None."]
**Validation path:** [remaining checks, commands, or "Not yet defined."]
**Next check:** [first file, command, or question the next agent should use]
**Risks:** [active risks or "None identified."]
```

`Compact` fields remain. `Primary source to trust first`, `Checked sources`,
`Delta since last stable state`, `Evidence`, `Unfinished work`,
`Validation path`, `Next check`, and `Risks` are additions.

## Deep

Use for complex, high-risk, or contradictory state that `standard` cannot safely compress.

Add these fields after `Risks` and before `Anti-scope`:

```markdown
**Open uncertainties:** [contradictions, unknowns, or ambiguous outcomes that must be preserved without choosing silently.]
```

`Compact` and `standard` fields remain. `Open uncertainties` is the addition.

## Redaction notation

Replace any detected secret, credential, token, key, or sensitive value with:

```text
[REDACTED]
```

Never include the original value. Report the field type (e.g., `[REDACTED: API key]`) only when identifying the type adds safety without leaking the value.

## Optional persistence note

When file persistence is requested, append this line before `Resume instructions`:

```markdown
**Persisted to:** `tmp/context-handoffs/<timestamp>-<slug>.md`
```
