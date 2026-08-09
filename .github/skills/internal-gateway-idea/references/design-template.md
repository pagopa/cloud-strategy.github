# Internal Gateway Idea Design Template

`state.json` and `design.md` are separate runtime artifacts. The JSON state is
the only persisted workflow state; the Markdown file is the bounded design and
its post-G3 review ledger. There are no packet files, review files, transcripts,
status siblings, `state.yaml`, or review-packet directories.

## `state.json`

The canonical state uses the exact `internal-gateway-idea-state/v2` fields below.
`advisory_return_state` is optional at runtime and is present only during
`ADVISORY_REVIEW`.

```json
{
  "schema": "internal-gateway-idea-state/v2",
  "slug": "example",
  "revision": 1,
  "state": "WAIT_G1",
  "design_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "assurance": "standard",
  "review_sources": [],
  "reviewed_revision": null,
  "approved_revision": null
}
```

The state parser rejects unknown keys, duplicate sources, stale revisions,
v1 state, wrong types, and a design hash mismatch. Actor, legal events, and
typed payloads are derived or transient and are never serialized.

## `design.md` before G3

Normal G0 starts with no runtime artifacts. A typed `resolve-g0` event passed to
`init` writes this bounded Markdown file first and then creates `state.json` at
`WAIT_G1`. Before G3, the file is at most 300 non-whitespace tokens and contains
only these sections:

## Intent

Record the accepted intent and target outcome.

## Accepted Decisions

Record typed decisions accepted at G0.

## Open Decisions

Record unresolved user-owned decisions. Do not infer a decision from silence.

## Selected Approach

Record the typed approach selected at G2, when one exists.

## Essential Evidence

Record only evidence needed to resume the current revision.

## Review Ledger after G3

After mandatory critic ingestion, append the consolidated ledger to the same
`design.md`. Store finding IDs, review sources, decision-relevant text, blocking
and conflict status, evidence references, and disposition. Raw packet JSON is
never stored.

| ID | Sources | Critique | Recommendation | Reason | Blocking | Evidence | Disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F-001 | standard | Example finding | Example remedy | Example reason | false | design.md#L1 | closed |

## Persistence and continuation

Replace `design.md` with a same-directory temporary file, flush it, and
atomically replace it. Compute its SHA-256 from the exact UTF-8 bytes, then
replace `state.json` with a separate same-directory temporary file. This is two
individual replacements, not a cross-file transaction; a crash between them
must reopen the earliest safe gate on hash mismatch.

Load only the two stable artifacts in a clean chat. Derive the current actor,
legal events, revision, and next action from validated state. If evidence is
missing, malformed, stale, or v1, fail closed and restart at the earliest gate
that can be proven. An on-demand advisory is the only pre-G0 exception: it
creates the bounded pair at `ADVISORY_REVIEW` and returns to `WAIT_G0` without
satisfying mandatory G4 review.
