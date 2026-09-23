# Project Memory Maintenance

Use this reference when the knowledge workflow considers retaining project
orientation or a selected approved specification. Project memory is selective
durable knowledge. It is not an issue tracker, backlog, planning system, or
execution record.

The managerial lane may link durable project purpose or an approved
specification to this owner, but it does not copy the managerial state
vocabulary here. Roadmap priorities, initiatives, proposals, plans, retry
history, and completion claims stay with their detailed owners.

## Retention Boundary

Retain a memory item only when all of the following are evidenced:

- the material explains durable project purpose, boundaries, vocabulary, or a
  selected specification that a future reader must be able to find;
- the evidence is current, approved, historical by explicit record, or
  implementation-complete by explicit evidence;
- a canonical owner or source can be named and linked;
- the item has a reader outcome beyond recording that work was requested; and
- the item is not a duplicate of an existing document, decision, or specification.

A signal, a useful idea, or a temporary note is not enough. When eligibility is
unclear, keep the material temporary and report the missing evidence.

## Existing Owner Check

Before creating or refreshing a memory item, inspect the existing owner in this
order when applicable:

1. root README and repository entry points;
2. context or context-map documents;
3. architecture and domain documents;
4. accepted ADRs and their indexes; and
5. the specification or other document named as the canonical source.

If an existing owner already carries the material, link to it and repair only
the approved owner. Do not create a second copy to make a project-memory list
look complete. If no owner exists, record an ownership gap; do not invent a
placeholder owner or a repository-specific path.

## Eligible Memory Types

### Project Orientation

Project orientation may retain the current purpose, important boundaries,
reader-facing entry points, and durable vocabulary needed to navigate the
repository. Each claim needs current evidence and an owner. Do not turn an
orientation entry into a full architecture document, roadmap, or operating
plan.

### Selected Specification

A selected specification may be retained as a link and short orientation note
when its approval and canonical ownership are explicit. The memory entry points
to the specification; it does not copy the specification or become a second
contract. A draft, proposal, issue, plan, or unapproved analysis remains
temporary unless a separate owner explicitly records its durable status.

## State Distinctions

Use the state stated by the evidence. Never infer one state from another:

| State | Required evidence | What it does not mean |
| --- | --- | --- |
| `current` | The owner or source identifies the material as the current description. | It does not prove approval or implementation. |
| `approved` | An explicit approval record names the specification or decision. | It does not prove that implementation is complete. |
| `historical` | The owner records that the material describes a past state or superseded decision. | It does not make the material current guidance. |
| `implementation-complete` | A canonical source explicitly records completion and its evidence. | It is never inferred from a closed issue, merged change, or a passing check alone. |

If evidence supports more than one state, retain the distinctions in separate
fields or entries. If the state is unknown, write `unknown` in the audit or
completion report and do not upgrade the memory item.

## Record Shape

When an approved target has a project-memory entry, keep it small and link-first:

```markdown
### <Retained topic>

- Type: `orientation` or `selected-specification`
- State: `current`, `approved`, `historical`, or `implementation-complete`
- Reader outcome: <what a future reader can decide or find>
- Canonical owner: <relative link or `unknown`>
- Evidence: <relative links supporting the type and state>
- Retention reason: <why this belongs in durable project memory>
```

Every link must resolve. A missing owner, state, or evidence link is a failed
retention candidate, not an invitation to fill the field with a guess.

## Explicit Exclusions

Project memory must not own or create:

- issues, backlog items, roadmaps, TODO lists, or prioritization;
- plans, task execution, status siblings, retry history, or completion claims;
- temporary notes, drafts, unapproved specifications, or placeholders;
- generated inventories, copied contracts, or a second ADR body; or
- automatic promotion from temporary material when a task closes or a check passes.

When a candidate belongs to one of these categories, keep it with its existing
owner and report the project-memory exclusion. Do not convert the exclusion
into a new durable artifact.

## Maintenance And Validation

For a retained item, recheck the canonical owner, links, evidence, and state
before writing. Remove or revise a memory entry only when the owner or approved
request establishes that its evidence is stale, superseded, or wrong. Preserve
historical entries when their historical value is explicit; do not present them
as current guidance.

Validate that the owner and evidence links resolve, the state is explicitly
supported, no duplicate contract was created, and no backlog or execution
content crossed the boundary. Report what was checked and which evidence is
still unknown.
