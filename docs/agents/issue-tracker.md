# Issue tracker: Local Markdown

Keep specs/PRDs in durable `.specs/`, incoming issues and reusable templates in
durable `.issues/`, and implementation tickets in disposable `tmp/.issues/`.
Wayfinder retains its separate workspace below.

## Conventions

- Specs use `.specs/<area>/<topic>/<feature>/spec.md`.
- Implementation tickets use `tmp/.issues/<area>/<topic>/<feature>/<NN>-<slug>.md`,
  numbered from `01` per feature, with no trailing `issues/` directory.
- Use the nearest common approved scope. Omit Topic for Area-wide work and
  Area for cross-Area work or no declared Areas. Keep `Area:` with all affected
  values and `Topic:` when applicable. Unknown scope blocks publication;
  never invent an Area or Topic. Feature directories are leaves, not scope
  parents; resolve collisions before writing and create no empty scope trees.
- Incoming issues retain their configured durable home under `.issues/`;
  templates use `.specs/_templates/` and `.issues/_templates/`.
- Each ticket links to its source spec; do not duplicate the spec in the issue directory
- Triage state is recorded as a `Status:` line near the top of each spec and issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Use the conventions above for local publication. Preserve intentional custom
paths and remote workflows; a declaration of the old standard default does
not make it a custom exception. Do not infer the tracker from folder existence
or create `tracker/`, `docs/.specs/` or local duplicates of remote records.

Before creating implementation tickets, requirements and acceptance criteria
must have an authorized durable spec or equivalent source. If missing, propose
that source and stop until approved. Tickets link to it; durable records must
not depend on temporary tickets for their meaning. Keep specs, incoming issues
and templates eligible for version control and report ignore conflicts.
Ticket state and comments in `tmp/` are temporary. Never delete records
automatically or stage or commit without a user request.

Old standard-default records require migration before affected tracker
writes, including old paths still declared in a guide. Obtain approval for
each source, destination, removal and reference repair. Preserve content,
state and IDs; retain unique requirements durably before moving implementation
tickets into `tmp/`. Without approval, stop affected writes. Read-only
operations report the requirement; unrelated docs stay unblocked. This does
not authorize a migration or alter genuine custom paths, remote trackers,
Wayfinder or plans in `tmp/.plans/`.

## Local triage discovery

Recursively scan `.specs/**/spec.md`, configured incoming issue records under
`.issues/`, and `tmp/.issues/**/*.md` for configured `Status:` roles. Exclude
every `_`-prefixed path segment, templates and examples. Implementation
frontiers scan only the selected feature's implementation tickets.
Readers honor an explicit source reference first, then configured lookup;
default spec lookup is recursive under `.specs/`. Report ambiguous matches.
Legacy records remain readable through explicit references while migration
approval is pending; that does not authorize further legacy-layout writes.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/mattpocock-wayfinder`. The **map** is a file with one **child** file per ticket.

- **Workspace**: `tmp/.wayfinder/<effort>/` — the self-contained analysis unit.
- **Map**: `tmp/.wayfinder/<effort>/map.md` — the Notes / Decisions-so-far / Fog body.
- **Child ticket**: `tmp/.wayfinder/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `tmp/.wayfinder/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map’s Decisions-so-far in `map.md`.
