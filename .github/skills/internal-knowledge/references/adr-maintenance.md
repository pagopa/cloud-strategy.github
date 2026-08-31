# ADR Maintenance

Use this reference when the user asks to record, revise, accept, supersede, or otherwise maintain an architectural decision.

## Qualify the Decision

Invoke `/mattpocock-domain-modeling` when the decision still needs domain terminology, alternatives, trade-offs, or boundaries clarified. Use its ADR gate: record the decision only when it is costly to reverse, surprising without context, and the result of a real trade-off. Skip that invocation for mechanical status changes or when the user has already supplied a settled decision and rationale.

The imported skill informs the decision. This skill retains ownership of repository paths, local format, write scope, status transitions, and validation.

## Local Contract

Read the nearest `docs/adr/README.md` before writing and treat it as authoritative. Use [minimal MADR](madr-minimal.md) only when no local contract exists.

Choose the ADR directory for the affected architectural scope. Use a root ADR directory for repository-wide decisions and a context-local ADR directory only when existing context documentation establishes one. Scan that directory for the highest number and create the next `NNNN-<slug>.md`; never reuse a number for another accepted decision.

Create a new ADR with the local heading, metadata, section order, status vocabulary, and language. Ground context, decision, rationale, alternatives, and consequences in repository evidence and the settled trade-off. Do not invent consensus, approval, ownership, or implementation state.

## Status and Immutability

- A proposed ADR may be revised before acceptance.
- An accepted ADR body is immutable.
- A changed accepted decision requires a new ADR that supersedes it. Modify only the old ADR's status line when the local contract permits that transition, and link both records.
- Do not mark an ADR accepted unless the user or repository authority explicitly establishes acceptance.

## Validation and Completion

Validate filename and heading identity, metadata, required sections and order, links, unique accepted numbering, supersession symmetry, Markdown, and repository-specific checks. Report the created or changed records, decision status, supersession changes, and validation performed.
