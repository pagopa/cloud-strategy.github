# ADR Maintenance

Use this reference when the user asks to record, revise, accept, supersede, or otherwise maintain an architectural decision.

## Contents

- [Qualify the Decision](#qualify-the-decision)
- [Local Contract](#local-contract)
- [Archive placement](#archive-placement)
- [Identity and numbering](#identity-and-numbering)
- [Applicability And Indexing](#applicability-and-indexing)
- [Status and Immutability](#status-and-immutability)
- [Validation and Completion](#validation-and-completion)

## Qualify the Decision

Invoke `/mattpocock-domain-modeling` when the decision still needs domain terminology, alternatives, trade-offs, or boundaries clarified. Use its ADR gate: record the decision only when it is costly to reverse, surprising without context, and the result of a real trade-off. Skip that invocation for mechanical status changes or when the user has already supplied a settled decision and rationale.

The knowledge layout is itself a decision. When a plan establishes or changes
the Area and Topic set, record that set and its evidence as an ADR, so later
invocations read a decision instead of re-deriving one.

The imported skill informs the decision. This skill retains ownership of repository paths, local format, write scope, status transitions, and validation.

## Local Contract

Read `docs/adr/README.md` and the destination's Area and Topic indexes before
writing. Preserve the local record format, language, status and supersession
contract. Use [minimal MADR](madr-minimal.md) only when no local contract exists.
Local flat-placement instructions require the
[mandatory migration](legacy-migration.md#mandatory-adr-migration); they do not
make misplaced records conformant.

Do not add front matter to ADRs. Preserve their local format and metadata
contract; generated documents and append-only ledgers remain governed by
[knowledge scope](knowledge-scope.md).

When ADRs already exist without a stated local format, propose an authorized
`docs/adr/README.md` that records their shared naming, section order, status
vocabulary and supersession practice. Preserve the record format while using
the scoped placement and navigation below.

Create a new ADR with the local heading, metadata, section order, status vocabulary, and language. Ground context, decision, rationale, alternatives, and consequences in repository evidence and the settled trade-off. Do not invent consensus, approval, ownership, or implementation state.

## Archive placement

Keep one canonical ADR at the nearest common approved scope under `docs/adr/`.

| Evidenced applicability | Destination |
| --- | --- |
| One Topic | `docs/adr/<area>/<topic>/NNNN-<slug>.md` |
| An Area, including several of its Topics | `docs/adr/<area>/NNNN-<slug>.md` |
| Several Areas or the repository as a whole | `docs/adr/NNNN-<slug>.md` |

Use the existing approved Area and Topic names, not a second taxonomy.
Create a scope directory only when it holds a real decision or an index of
applicable shared decisions. Do not pre-create empty Area or Topic trees.
Never place ADRs under `docs/areas/` or copy a shared decision into each scope.

New records state the affected `Area:` values in their bodies and `Topic:`
when Topic-specific; name all affected scopes for shared decisions. A
repository-wide decision without declared Areas stays at root without
inventing an Area. Preserve an established equivalent metadata format.
Resolve applicability from authoritative records, indexes or an explicit
human decision, never from a directory or filename alone. Unresolved scope
blocks placement; it is not permission to use root as a catch-all.

## Identity and numbering

Keep `ADR-nnnn` unique across the repository, independent of its directory.

Before creating a record, recursively inventory every ADR under `docs/adr/`,
including historical and superseded records and any declared unmigrated
locations. Use one more than the highest assigned number for the next
`NNNN-<slug>.md`; do not restart numbering per Area or Topic or reuse an ID.
Conflicting IDs require resolution before creation.
Moves preserve the record's ID and filename. Recheck numbering immediately
before writing to avoid allocating a number assigned since preflight.

## Applicability And Indexing

Navigate from a compact root index to the relevant scope.

- Root: `docs/adr/README.md` states the archive contract, lists root decisions
  and links to the Area indexes. Do not require a second exhaustive catalog
  of nested ADRs.
- Area: `docs/adr/<area>/README.md` lists Area decisions, links to populated
  Topic indexes and references applicable root decisions.
- Topic: `docs/adr/<area>/<topic>/README.md` lists its decisions and references
  applicable Area and root decisions.
- Owners: Area documentation READMEs link to their ADR index. Create indexes
  only for scopes with decisions or evidenced applicable shared decisions;
  include each exact index path in the approved allowlist.

Record evidenced applicability beside decision links in the owning scope
index, including historical `Level` and `Serves` values when appropriate.
Link shared decisions rather than copying their content. Do not infer
applicability from current implementation alone or rewrite accepted ADR
bodies for discovery. Missing indexes require authorized creation, not new
frontmatter, an invented registry or an unapproved write.

## Status and Immutability

- A proposed ADR may be revised before acceptance.
- Accepted decision content is immutable. A path-only link update may maintain references without changing the decision, its rationale, or its consequences.
- A changed accepted decision requires a new ADR that supersedes it. Modify only the old ADR's status line when the local contract permits that transition, and link both records.
- Do not mark an ADR accepted unless the user or repository authority explicitly establishes acceptance.

## Validation and Completion

Validate local filename and heading identity, metadata, required sections and
order, scope placement, index and incoming links, globally unique numbering,
supersession symmetry, Markdown and repository-specific checks. Report the
created, moved or changed records, decision status, supersession changes and
validation performed. Do not claim conformance while required migration or
reference repair remains incomplete.
