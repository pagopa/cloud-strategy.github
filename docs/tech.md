# Technology

## Purpose

This document describes the observed technology stack and tooling used in this
repository.

## Languages And Runtimes

| Area | Technology |
| --- | --- |
| Automation and tests | Python 3.x |
| Build and task entrypoints | Make, shell scripts |
| Governance assets | Markdown, YAML, JSON |
| CI and contract enforcement | GitHub Actions workflows plus local script entrypoints |

## Tooling

| Category | Observed tooling |
| --- | --- |
| Sync logic | `.github/skills/local-sync-repos/scripts/sync_repos.py`, `.github/skills/local-sync-repos/scripts/sync_contract.py` |
| Catalog generation | `.github/scripts/build_inventory.py`, inventory helpers in `.github/scripts/lib/`, and `./.github/scripts/run.sh build_inventory` |
| Contract checks | `pytest` tests under `tests/` and `.github/skills/*/tests/`, plus validator subcommands through `run.sh` |
| Linting and policy checks | Make targets such as `docs-lint`, `token-risks`, and catalog checks |

## Validation Surface

- Python tests are the primary regression mechanism for sync and contract logic.
- Skill-owned tests live under the owning `.github/skills/<skill>/tests/` bundle;
  root `tests/` is reserved for shared and cross-boundary contracts.
- Script-level validators check catalog consistency and generated inventory.
- Make targets provide standard execution entrypoints for maintainers.

## Technical Constraints

- Keep repository assets text-based and diff-friendly.
- Keep sync logic deterministic and safe for consumer-local preservation.
- Keep policy and projection compact to reduce drift risk.
- Keep source-managed templates distinct from target-owned runtime assets.

## Unknown / To Verify

- Minimum Python patch version required across all contributor environments.
- Any optional external tools that are required outside documented validators.
