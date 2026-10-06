# Knowledge Navigation

Use this reference when discovering a repository's knowledge router or README
index, or when a sync/setup plan proposes an index write. Routers are evidence
only; their instruction owners maintain them.

## Router Detection

Check candidate paths in this order:

1. If `AGENTS.md` loads `AGENTS.local.md`, treat `AGENTS.local.md` as the
   candidate router.
2. Otherwise, if `AGENTS.md` is evidenced as repository-owned, treat it as the
   candidate router.
3. Otherwise, report `router: gap` and name the missing ownership or routing
   evidence.

Do not infer repository ownership from a filename, location, existence, or the
fact that a central instruction loads a local file. Inspect ownership evidence
to identify the instruction owner for a handoff. Ownership or explicit path
authorization does not bring policy edits into this skill's write scope.

## Router Handoff

Read the candidate when routing is relevant to the requested knowledge work.
Leave every byte unchanged, including existing router blocks. Report a missing
or stale route as `router: gap`, name its evidence and instruction owner, and
hand off the bounded policy change. Uncertain ownership is also a gap.

Report `router: unchanged` when the inspected route serves the reader and
`router: not-applicable` when routing was outside the resolved work. The legacy
`router: written` report value remains readable for compatibility; this skill
does not emit it for new work.

## README Index

Maintain one canonical index at docs/README.md for strategic and tactical
knowledge. Map each evidenced type to its existing owner and add a "Load when"
entry that tells the reader when to open it. Use "not evidenced" when no
supported owner exists; do not create a placeholder document. The root README
provides repository orientation and links to this index.

Treat a README index as an ordinary documentation target only when it is in
the approved allowlist. Before drafting, inspect the index and its generator
markers. When a marker or authoritative generator configuration shows the
index is generated, leave its bytes to the generator and report the owner and
enforcement gap. Write a hand-maintained index only when no generator owns it,
the path is authorized, and its links can be checked against the final target
set.

Include the alignment contract in the index: operational work cites the
knowledge IDs it realizes; the skill reads operational artifacts only as
evidence; and docs/ contains no reverse registry of operational work. Link to
[alignment](alignment.md) for IDs, Serves, precedence, and the audit outcome
rules.

Use the repository's existing entry point and information hierarchy. Keep the
root README focused on repository orientation and route readers to the
knowledge index, context map, or domain owners as supported by evidence. Do
not duplicate the detail held by linked owners. If an index target is outside
the requested bucket or approved plan, report it as excluded rather than
widening the allowlist.

## Maintained Owners

Route each link to the existing maintained owner supported by repository
evidence. Do not create or retain a compatibility page solely to preserve an
older document hierarchy. If an older page contains useful material, link to
its current owner; propose deletion only through the exact-path approval gate
in [knowledge scope](knowledge-scope.md). When no maintained owner is evidenced,
report the ownership gap rather than inventing a destination or broken link.
