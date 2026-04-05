# Internal Contract

This document defines the high-level repository behaviors that remain under automated verification.
Anything not listed here is intentionally out of scope for the Python contract runner.

## Principles

- Verify behavior, not resource formatting details.
- Keep checks high level and resilient to internal refactors.
- Do not add tests that parse or enforce the internal structure of prompts, skills, agents, or instructions unless an explicit repository contract below requires it.
- Use Python only for the contract runner and its fixtures.

## Global Resource Rules

These rules apply to all repository resources, including prompts, skills, instructions, agents, plugins, and similar assets.

### Naming By Origin

- External resource: `<short-repo>-<original-resource-name>`
- Resource created locally in `cloud-strategy.github`: `internal-<resource-name>`
- Resource created locally in another repository: `local-<resource-name>`

### Naming Presence

- Every resource must have a name.
- The resource name must match the canonical identifier used for that resource.

## Contract Categories

### Resource Governance

#### `resource-governance-uses-supported-origin-naming`

- Goal: ensure repository resources follow the naming convention defined by origin.
- Scope:
  - prompts
  - skills
  - agents
  - instructions
- Expected behavior:
  - every repository-local resource uses `internal-*`
  - every external imported resource uses `<short-repo>-*`
  - every local cross-repository resource uses `local-*`

#### `resource-governance-named-resources-declare-name`

- Goal: ensure repository-owned resources that support explicit naming metadata actually declare it.
- Scope:
  - internal prompts
  - internal skills
  - internal agents
- Expected behavior:
  - every repository-owned internal resource has a non-empty canonical identifier
  - every internal prompt, skill, and agent declares a non-empty `name:`
  - every declared `name:` matches the canonical resource identifier
  - imported non-`internal-*` resources may remain verbatim and are not normalized by this contract

#### `resource-governance-agents-preferred-optional-skills-are-well-formed`

- Goal: ensure agents publish an explicit reusable skill contract instead of implying skill usage only in prose.
- Scope:
  - internal agents
- Expected behavior:
  - every internal agent declares at least one skill in that section
  - internal agents do not use the deprecated `## Primary Skill Stack` heading

#### `resource-governance-agent-preferred-optional-skills-resolve-on-disk`

- Goal: ensure agent skill contracts point to real reusable skills rather than stale or decorative identifiers.
- Scope:
  - internal agents
  - skills
- Expected behavior:
  - internal agents do not declare agent identifiers, aliases, or missing skills as if they were reusable skill contracts

#### `resource-governance-canonical-operational-agents-publish-engine-contracts`

- Goal: enforce the canonical repository-owned operational model through explicit mandatory engines, optional support sections, and escalation boundaries.
- Scope:
  - canonical operational agents
  - skills
- Expected behavior:
  - the canonical operational agents `internal-router`, `internal-fast-executor`, `internal-planning-leader`, `internal-review-guard`, and `internal-critical-challenger` exist
  - each canonical operational agent declares `## Mandatory Engine Skills` with the repository-defined engine mapping
  - each canonical operational agent declares a non-empty `## Optional Support Skills` section
  - each canonical operational agent publishes `## Escalation / Routing`
  - each canonical operational agent references only real canonical operational-agent targets inside `## Escalation / Routing`
  - canonical operational agents do not self-route inside `## Escalation / Routing`
  - canonical operational agents do not fall back to the legacy `## Preferred/Optional Skills` heading
  - `.github/copilot-instructions.md` defines the source-side mandatory-engine baseline policy without making that rule depend on root `AGENTS.md`

#### `resource-governance-retired-operational-agents-do-not-regrow`

- Goal: prevent the retired non-sync operational catalog from reappearing on disk or through downstream routing references.
- Scope:
  - `.github/agents/`
  - repository routing and workflow references
- Expected behavior:
  - retired internal operational agent files are absent from `.github/agents/`
  - repository-owned routing references do not point users back to retired operational agent routes
  - old-to-new mapping remains only in the dedicated routing or operating-model engine skills

### Reporting

#### `reporting-operation-completion-report-contract-is-documented`

- Goal: keep the end-of-operation reporting contract visible in the primary Copilot policy layer and source-side documentation.
- Scope:
  - root `AGENTS.md`
  - `.github/copilot-instructions.md`
  - `.github/README.md`
- Expected behavior:
  - `.github/copilot-instructions.md` defines the mandatory completion report macro categories `✅ Outcome`, `🤖 Agents`, `📘 Instructions`, and `🧩 Skills`
  - the policy requires an explicit explanation when a resource category was not used
  - root `AGENTS.md` points to `.github/copilot-instructions.md` as the owner of detailed completion-report behavior
  - `.github/README.md` documents the same completion-report contract for maintainers

#### `reporting-sync-agents-publish-completion-report-categories`

- Goal: keep the source-side governance agent and the cross-repository sync agent aligned with the repository completion-report contract.
- Scope:
  - `.github/agents/internal-sync-control-center.agent.md`
  - `.github/agents/internal-sync-global-copilot-configs-into-repo.agent.md`
- Expected behavior:
  - both agents require completed runs to end with `✅ Outcome`, `🤖 Agents`, `📘 Instructions`, and `🧩 Skills`
  - both agents require an explicit explanation when a category was not used
  - the source-side governance agent still reports `Governance files reviewed`

### Sync Planning

#### `sync-plan-regenerates-root-agents`

- Goal: keep root `AGENTS.md` aligned as a governed bridge after catalog changes.
- Fixture:
  - target repository with a root `AGENTS.md`
  - minimal infrastructure footprint
- Expected behavior:
  - the generated sync plan reports an `update` action for `AGENTS.md`

#### `sync-plan-mirrors-source-catalog`

- Goal: ensure target repositories receive the complete mirrored source catalog for Copilot resources.
- Fixture:
  - target repository with a Python source file
- Expected behavior:
  - the generated sync plan identifies the repository as Python-oriented
  - the generated sync plan selects every source instruction, prompt, skill, and agent
  - the generated sync plan includes skill support files outside `SKILL.md`
  - the generated sync plan keeps the canonical mandatory engine skills in the preferred-skills selection baseline

#### `sync-plan-preserves-local-target-assets`

- Goal: keep target-local `local-*` assets visible instead of deleting them during mirror alignment.
- Fixture:
  - target repository with a target-local `local-*` Copilot asset outside the mirrored source catalog
- Expected behavior:
  - sync apply does not overwrite or delete that `local-*` asset

#### `sync-plan-writes-tracking-file`

- Goal: create a persistent per-target sync plan inside repository-root `tmp/` before apply runs.
- Fixture:
  - target repository with a minimal supported stack
- Expected behavior:
  - plan mode writes `tmp/internal-sync-copilot-configs.plan.md`
  - the run creates `tmp/` when the target repo does not already have it
  - the file contains pending synchronization and validation sections

### Sync Application

#### `sync-apply-writes-manifest-and-agents`

- Goal: ensure apply mode still produces the core synchronization artifacts.
- Fixture:
  - fresh target repository with a minimal supported stack
- Expected behavior:
  - apply writes the sync manifest
  - apply writes `AGENTS.md`
  - manifest records managed files for the apply result

#### `sync-apply-mirrors-skill-support-files`

- Goal: ensure skill bundles are mirrored as complete directories instead of `SKILL.md` only.
- Fixture:
  - fresh target repository with a minimal supported stack
- Expected behavior:
  - apply copies non-`SKILL.md` files from mirrored skill directories
  - copied support files preserve byte-for-byte content

#### `sync-apply-removes-tracking-file-when-complete`

- Goal: delete the per-target sync plan when apply and post-checks close every planned objective.
- Fixture:
  - fresh target repository with a minimal supported stack
- Expected behavior:
  - apply removes `tmp/internal-sync-copilot-configs.plan.md` after sync and strict validation complete successfully

#### `sync-apply-keeps-tracking-file-for-local-follow-up`

- Goal: keep the per-target sync plan visible when preserved local assets still need manual action.
- Fixture:
  - target repository with an invalid local Copilot asset
- Expected behavior:
  - apply keeps `tmp/internal-sync-copilot-configs.plan.md`
  - the file contains a pending manual follow-up section describing the local issue

## Explicitly Out Of Scope

### Resource Content And Layout

- prompt frontmatter formatting
- skill section structure
- agent cohesion, routing breadth, and declared-skill breadth beyond the required explicit skill contract
- exact one-to-one mapping between preferred skills and specific agents
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
- full source mirroring behavior
