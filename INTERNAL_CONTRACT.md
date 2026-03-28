# Internal Contract

This document defines the high-level repository behaviors that remain under automated verification.
Anything not listed here is intentionally out of scope for the Python contract runner.

## Principles

- Verify behavior, not resource formatting details.
- Keep checks high level and resilient to internal refactors.
- Do not add tests that parse or enforce the internal structure of prompts, skills, agents, or instructions.
- Use Python only for the contract runner and its fixtures.

## Contract Categories

### Sync Planning

#### `sync-plan-detects-root-agents-conflict`

- Goal: protect manually managed root `AGENTS.md` files from accidental overwrite.
- Fixture:
  - target repository with a root `AGENTS.md`
  - minimal infrastructure footprint
- Expected behavior:
  - the generated sync plan reports a `conflict` action for `AGENTS.md`

#### `sync-plan-selects-python-assets`

- Goal: ensure Python repositories still receive a Python-oriented shared baseline.
- Fixture:
  - target repository with a Python source file
- Expected behavior:
  - the generated sync plan identifies the repository as Python-oriented
  - the generated sync plan selects at least one managed prompt for that stack

#### `sync-plan-preserves-manual-target-assets`

- Goal: keep target-local unmanaged assets visible instead of silently absorbing them into the baseline.
- Fixture:
  - target repository with a manual custom Copilot asset outside the managed baseline
- Expected behavior:
  - sync apply does not overwrite or delete that manual asset

### Sync Application

#### `sync-apply-writes-manifest-and-agents`

- Goal: ensure apply mode still produces the core synchronization artifacts.
- Fixture:
  - fresh target repository with a minimal supported stack
- Expected behavior:
  - apply writes the sync manifest
  - apply writes `AGENTS.md`
  - manifest records managed files for the apply result

## Explicitly Out Of Scope

### Resource Content And Layout

- prompt frontmatter formatting
- skill section structure
- agent body wording
- inventory wording details
- cross-link completeness between resources

These are governed by repository conventions, skills, and dedicated validation workflows rather than this contract.

### Legacy Migration Mechanics

- alias mapping details
- rename choreography
- backwards-compatibility edge cases

These may change over time and should not be locked by high-level contract tests.

## Change Rule

Add a new contract only when a regression would materially break:

- sync planning
- sync application
- target repository safety
- baseline selection behavior
