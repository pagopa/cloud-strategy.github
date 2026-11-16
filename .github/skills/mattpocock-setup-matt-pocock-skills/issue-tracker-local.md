# Issue tracker: Local Markdown

Specs live in the project-root `.specs/`; tickets live in `.issues/`.
Both are durable work records, separate from disposable `tmp/`.

## Conventions

- One feature per directory: `.issues/<feature-slug>/`
- The spec is `.specs/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.issues/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

For a spec, create `.specs/<feature-slug>/spec.md`. For a ticket, create
`.issues/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, and
link it to its source spec. Create only directories needed for the request.
Use `Status:` on both specs and tickets, with the configured triage roles.
Triage scans both `.specs/*/spec.md` and `.issues/*/issues/*.md`;
implementation ticket frontiers scan only the issue files.

Keep these records eligible for version control; do not stage or commit
without a user request. If ignore rules exclude them, report the conflict
instead of claiming they are shared. Do not migrate existing records.

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
