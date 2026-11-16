# Issue tracker: Local Markdown

Specs (also called PRDs) live as Markdown files in the project-root `.specs/`.
Ordinary issues live in `tmp/.issues/`. Wayfinder efforts use the self-contained
workspace described below. Do not create a root `tracker/` directory.

## Conventions

- The spec is `.specs/<feature-slug>/spec.md`, not `docs/.specs/`
- Implementation issues are one file per ticket at `tmp/.issues/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` — never a single combined tickets file
- Each ticket links to its source spec; do not duplicate the spec in the issue directory
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

For a spec, create `.specs/<feature-slug>/spec.md`. For an implementation
ticket, create `tmp/.issues/<feature-slug>/issues/<NN>-<slug>.md`.
Create only the directories needed for the requested artifact.
Preserve existing records in their current locations; these defaults do not
authorize moving, overwriting, or deleting them.

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
