# Knowledge Navigation

Use this reference when discovering a repository's knowledge router or README
index, or when a sync/setup plan proposes to write either one. Discovery
identifies the candidate; it does not grant write authority.

## Router Detection

Check candidate paths in this order:

1. If `AGENTS.md` loads `AGENTS.local.md`, treat `AGENTS.local.md` as the
   candidate router.
2. Otherwise, if `AGENTS.md` is evidenced as repository-owned, treat it as the
   candidate router.
3. Otherwise, report `router: gap` and name the missing ownership or routing
   evidence.

Do not infer repository ownership from a filename, location, existence, or the
fact that a central instruction loads a local file. A write requires positive
proof for that exact path: authoritative synchronization metadata identifying
it as repository-owned, or the user's explicit attestation of that path in the
approved write allowlist. If either proof is absent or ambiguous, leave the
router unchanged and report `router: gap`.

## Bounded Router Edits

Read the entire candidate before planning a change. A router edit changes only
the content between these exact markers:

```text
<!-- knowledge-router:start -->
<!-- knowledge-router:end -->
```

Preserve every byte outside the delimited block. If the markers are duplicated,
malformed, or cannot be preserved, do not write; report the gap. Add a new
block only when the exact router path is authorized and ownership is proved.
Keep routing entries concise, task-oriented, and directed to the smallest
valid owner. Do not rewrite neighboring policy, generated content, or
instructions owned elsewhere.

Report `router: written` when the authorized block changed, `router:
unchanged` when a proved and authorized block already serves the reader, and
`router: gap` when selection or ownership is unresolved. Use
`router: not-applicable` only when no router write was part of the resolved
work.

## README Index

Treat a README index as an ordinary documentation target only when it is in
the approved allowlist. Before drafting, inspect the index and its generator
markers. When a marker or authoritative generator configuration shows the
index is generated, leave its bytes to the generator and report the owner and
enforcement gap. Write a hand-maintained index only when no generator owns it,
the path is authorized, and its links can be checked against the final target
set.

Use the repository's existing entry point and information hierarchy. Keep the
root README focused on repository orientation and route readers to the
knowledge index, context map, or domain owners as supported by evidence. Do
not duplicate the detail held by linked owners. If an index target is outside
the requested bucket or approved plan, report it as excluded rather than
Do not widen the allowlist.
