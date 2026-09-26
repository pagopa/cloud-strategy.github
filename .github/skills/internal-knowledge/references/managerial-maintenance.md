# Managerial Maintenance

Use this reference as the single detailed owner for the managerial lane. It
keeps purpose, priorities, initiatives, proposals, accepted decisions,
current implementation, and observed outcomes readable without inventing a
technical domain or replacing a technical owner.

Managerial scope covers purpose, priorities, initiatives, proposals, and observed outcomes.

## Scope and self-contained vocabulary

The managerial lane explains why work matters, what is prioritized, which
initiatives are being considered, what has been proposed, what was explicitly
accepted, what is currently implemented, and what outcome has actually been
observed. This vocabulary fallback is self-contained: a standalone run can
apply it without a host repository, host manifest, host script, or unstated
provider terminology.

Use `purpose` for the durable reader reason to care, `priority` for an
evidenced ordering criterion, `initiative` for a bounded body of work,
`proposal` for an unaccepted option, `accepted decision` for an explicitly
approved choice, `current implementation` for a source-backed present state,
and `observed outcome` for a result supported by evidence. A proposal must not auto-promote to an accepted decision, current implementation, or observed outcome.

## Ownership map

Keep one detailed owner for each claim:

| Claim | Detailed owner | Managerial lane action |
| --- | --- | --- |
| Project purpose and durable orientation | `project-memory-maintenance.md` and the repository's canonical orientation owner | Link the owner and retain only eligible durable context. |
| Roadmap priorities and completion conditions | The common-core roadmap owner | Link the roadmap; do not duplicate its ordering or completion contract. |
| Initiatives and proposals | This reference and its authorized managerial document | Record the state, evidence, and next decision without treating it as approval. |
| Accepted decisions | ADR maintenance and the accepted ADR | Link the decision and preserve the accepted body. |
| Current implementation | Architecture, README, source, or configuration owner | Cite the current evidence; do not infer implementation from approval. |
| Observed outcomes | The authorized outcome record or existing operational owner | Cite what was observed and keep unknown outcomes explicit. |

If an owner or instruction route is missing, report the gap before complete setup and issue a bounded handoff to the named instruction owner. Do not edit
that owner's policy or instruction file from this lane.

## Durable retention boundary

For durable orientation or an approved specification, link back to
`project-memory-maintenance.md` and apply its eligibility, state, canonical
owner, and evidence checks. Project memory must not own roadmaps, plans,
backlog items, retry history, completion claims, temporary proposals, or
automatic promotion from a passing check.

## Maintenance and validation

Before authoring, recheck the existing owner, the state evidence, and the
unchanged predicate. Keep a repeated realignment unchanged when its owner,
state, and reader outcome are still correct. Validate that every link resolves,
every state has explicit evidence, proposals remain proposals until acceptance
is observed, and no technical domain or runtime profile was invented merely to
make the managerial lane look complete.
