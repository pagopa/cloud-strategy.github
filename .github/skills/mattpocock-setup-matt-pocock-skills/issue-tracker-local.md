# Issue tracker: Local Markdown

Keep requirements in durable `.specs/`, incoming issues and reusable templates
in durable `.issues/`, and implementation tickets in disposable `tmp/.issues/`.

## Conventions

- Specs: `.specs/<area>/<topic>/<feature>/spec.md`.
- Implementation tickets: `tmp/.issues/<area>/<topic>/<feature>/<NN>-<slug>.md`,
  numbered from `01` per feature; link each ticket to its durable source.
- Omit Topic for Area-wide work and Area for cross-Area work or no declared
  Areas. Use only approved scopes; never invent an Area or Topic.
- Incoming issues keep their configured durable home under `.issues/`.
  Templates stay in `.specs/_templates/` and `.issues/_templates/`.
- Use configured `Status:` roles and append comments under `## Comments`.

## When a skill says "publish to the issue tracker"

- Read applicable repository policy and `docs/agents/issue-tracker.md` before
  publishing or locating records. Preserve intentional custom paths and remote
  workflows; an old standard-default declaration is not a custom exception.
- Local defaults: specs use `.specs/<area>/<topic>/<feature>/spec.md`;
  implementation tickets use `tmp/.issues/<area>/<topic>/<feature>/<NN>-<slug>.md`,
  numbered from `01` per feature, with a link to their durable source.
  Incoming issues stay durable under `.issues/`; templates stay in
  `.specs/_templates/` and `.issues/_templates/`.
- Scope: use the nearest common approved Area/Topic. Omit Topic for Area-wide
  work and Area for cross-Area work or when no Areas are declared. Keep
  `Area:` with all affected values and `Topic:` when applicable. Uncertain
  applicability blocks publication; report it without inventing scope or
  starting a new interview. Feature directories are leaves, not scope parents;
  resolve path collisions before writing. Create no empty scope trees.
- Discovery: recursively scan `.specs/**/spec.md`, configured incoming issue
  records under `.issues/`, and `tmp/.issues/**/*.md` for configured `Status:`
  roles. Exclude every `_`-prefixed path segment, templates and examples.
  Implementation frontiers include only the selected feature's tickets.
- Retention: keep specs, incoming issues and templates eligible for version
  control; report conflicting ignore rules. Ticket comments and execution state
  in `tmp/` are temporary. Requirements and acceptance criteria must already
  have an authorized durable spec or equivalent source; otherwise propose it
  and stop until approved. Durable records must not depend on temporary tickets
  to retain their meaning. Never stage, commit or delete records automatically.
- Migration: old standard-default records require migration before affected
  tracker writes, even when a guide still declares the old default. Obtain
  approval for each source, destination, removal and reference repair, preserve
  state and content, and retain unique requirements durably before moving
  implementation tickets into `tmp/`. Without approval, stop affected writes.
  Read-only operations only report the requirement; unrelated docs stay unblocked.
  Preserve genuine custom paths and remote trackers; do not modify Wayfinder
  or plans in `tmp/.plans/`.
- Readers honor an explicit source reference first, then configured lookup;
  default spec lookup is recursive under `.specs/`, never inferred from folder
  existence. Report ambiguous matches. Do not duplicate remote records locally,
  create `tracker/` or `docs/.specs/`, or copy specs into ticket directories.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/mattpocock-wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.issues/<effort>/map.md` (the Notes / Decisions-so-far / Fog body).
- **Child ticket**: `.issues/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `.issues/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.
