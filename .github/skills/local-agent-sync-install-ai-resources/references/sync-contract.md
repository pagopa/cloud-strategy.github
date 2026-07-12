# Home Sync Contract

Use this reference for the exact repository-to-home contract.

## Scope And Ownership

- `.github/skills/` is the sole source of truth for managed skill bundles.
- `~/.agents/skills/` remains a real directory. It is a runtime projection,
  not a second source.
- Eligible skills are materialized as one absolute canonical symbolic link per
  skill. A write through that link changes the repository object directly.
- Allowlisted agents retain their existing translation and copy behavior.
- Never copy, merge, or reconcile home skill content into the repository.
- Preserve all home-only skills, including `graphify`, every `local-*` bundle,
  invalid repository bundles, and every catalog-excluded ID.

## State And Manifest

State belongs under `~/.sync/cloud-strategy-governance/home-ai-resources/`:

- `manifest.json`
- `last-plan.json`
- `last-audit.json`
- `locks/home-ai-resources.lock`

`manifest.json` uses schema version 2. Each row has these common fields:

- `target`, `resource_family`, `resource_id`, `source_path`, `target_path`,
  `source_hash`, and `last_action`.

Skill rows have `materialization: symlink`, an absolute canonical
`link_target`, and `content_hash: null`. Agent rows have
`materialization: copy`, `link_target: null`, and a content hash. Schema-v1
rows are normalized in memory as copied resources and are rewritten only after
a successful apply.

## Planning

For each eligible skill, calculate the absolute canonical source path and
inspect the direct home child:

| Current target | Plan action |
| --- | --- |
| Missing | `link` |
| Link to the canonical source | `skip`; adopt it into the manifest |
| Existing non-link directory with the same eligible ID | `link`; replace it without backup |
| Broken link | `blocked` with `link-target-missing` |
| Link to another checkout | `blocked` with `link-target-mismatch` |

Skills never use mtime or hashes to choose a winner. Agents retain the
existing hash-based copy and explicit-prune behavior.

A stale schema-v2 skill link is planned as `unlink` without
`--prune-managed`, but only when it is a direct child of the real runtime skill
root. A stale copied agent remains subject to its explicit prune safety.

## Path Safety And Apply

Before changing a skill target, require all of the following:

1. the source is a valid repository skill bundle containing `SKILL.md`;
2. the target is a direct child of the real runtime skill root;
3. the runtime skill root and every intermediate parent are real directories,
   not links;
4. the source and target stay inside their respective allowed roots; and
5. symlink creation is supported by the active filesystem.

After those checks, `create_skill_link` may remove a colliding real directory
without backup and create the absolute link. `unlink_managed_skill` unlinks
the link itself, including a broken link, and never follows its target.

Apply verifies every skill by exact link identity and every copied agent by
its expected hash. It then writes manifest v2. Unsupported link capability is
`symlink-unsupported`; do not fall back to copied skills.

Moving the repository checkout invalidates canonical link targets. Rerun sync
from the new checkout to recreate managed links.

## Modes

- `sync`: build an apply plan and auto-apply only clean repository-to-home
  work. It may create links and copy agents.
- `plan` or `dry-run`: read-only proposed operations.
- `audit`: read-only comparison of source, manifest, and managed targets.
- `doctor`: read-only runtime-root, support, catalog, and state checks.
- `apply`: explicit materialization; directory creation and copied-agent
  pruning retain their explicit flags.

Do not run against the real home during tests. Use a temporary home root.

## Reporting

Compact and report payloads expose `linked`, `unlinked`, copied agents,
skipped resources, blockers, and a bounded path sample. Report counts for
unchanged skills rather than enumerating them. Translate every blocker using
`error-codes.md` and state the next action.

## Entry Points

- Canonical runner: `scripts/run.sh`
- Python CLI: `scripts/sync_home_ai_resources.py`
- Planning and apply implementation: `scripts/home_syncing.py`
- Contract loader: `scripts/home_sync_contract.py`
- Repository dispatcher: `.github/scripts/run.sh sync_home_ai_resources ...`
