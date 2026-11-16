# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `tmp/.issues/`.

## Conventions

- One feature per directory: `tmp/.issues/<feature-slug>/`
- The spec is `.specs/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `tmp/.issues/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `tmp/.issues/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/mattpocock-wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `tmp/.issues/<effort>/map.md` (the Notes / Decisions-so-far / Fog body).
- **Child ticket**: `tmp/.issues/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when every file it lists is `resolved`.
- **Frontier**: scan `tmp/.issues/<effort>/issues/` for files that are open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.

<!-- local-sync:spec-tracker-paths:start -->
## Local specification and tracker paths

This contract overrides conflicting storage defaults, publication destinations,
and spec lookup instructions above.

- Read applicable repository policy and `docs/agents/issue-tracker.md` before
  publishing or locating a spec or ticket. Declared tracker types and paths
  override examples and defaults; do not infer them from folder existence.
- For a selected local Markdown tracker without declared paths, save new specs
  at `.specs/<feature-slug>/spec.md` in the project root and tickets at
  `tmp/.issues/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`.
  Link tickets to their source spec instead of copying it into the issue folder.
- Setup must retain existing tracker choices and custom paths. For a new local
  setup, record the separate spec and ticket defaults above. Do not create
  `tracker/` or `docs/.specs/` as a fallback; create only directories needed for
  the requested artifacts.
- For a configured remote tracker, use its publication and lookup workflow.
  Do not create a duplicate local spec or ticket unless the user requests it.
- Readers must honor an explicit spec reference first, then the configured
  source; for local defaults, look in `.specs/<feature-slug>/spec.md`.
  Use legacy locations only when evidenced, and clarify ambiguous matches.
- Do not move, delete, overwrite, or migrate existing specs, issues, or tracker
  configuration merely to adopt these defaults.
<!-- local-sync:spec-tracker-paths:end -->
