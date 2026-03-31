---
name: internal-copilot-audit
description: Audit Copilot customization health for overlap, hollow references, deprecated frontmatter, weak bridge design, naming violations, stale governance references, and redundant command-center assets. Use when reviewing the quality of `.github/` customization assets in this repository.
---

# Internal Copilot Audit

Use this skill when auditing the health of the Copilot customization catalog.

Treat the declared governance contract in the relevant agent, root `AGENTS.md`, and `.github/copilot-instructions.md` as the policy source of truth. Treat the current `.github/` catalog on disk as evidence to compare against that policy.

## Audit Goals

- Detect overlapping skills, prompts, and agents.
- Detect hollow assets that point to missing local files or missing companion skills.
- Detect declared skills that have no concrete workflow role in the agent or prompt that declares them.
- Detect deprecated frontmatter and stale runtime-specific wording.
- Detect weak `AGENTS.md` bridge design.
- Detect sync workflows that skip or fail to report governance review for `.github/copilot-instructions.md` and root `AGENTS.md`.
- Detect naming violations and stale inventory references.
- Detect governance files that still describe removed, renamed, or retired assets.

## Audit Order

1. Check naming and frontmatter.
2. Check broken local references.
3. Check declared skill contracts and decorative skill usage.
4. Check trigger overlap.
5. Check bridge coherence between `AGENTS.md` and `.github/copilot-instructions.md`.
6. Check whether prompts, skills, or agents became redundant after internal replacements were added.
7. Check whether governance files still describe superseded or removed assets.

## What To Flag

### Hollow assets

Flag an asset when:

- it references `resources/` or `references/` files that do not exist
- it tells the model to invoke skills or agents that are not installed
- it depends on assistant-runtime features not supported by the repository target

### Decorative skill contracts

Flag an asset when:

- it declares a skill but never assigns it a concrete workflow role
- it keeps a broad toolbox-style skill list without routing or trigger boundaries
- it treats a skill as available context rather than an expected procedure

### Deprecated patterns

Flag an asset when it still contains:

- `tools:`
- `model:`
- `color:`
- runtime-specific wording that should have been normalized to GitHub Copilot terminology

### Overlap problems

Flag a pair or group when:

- one asset is a weaker alias of another
- one asset is a workflow bundle built from missing dependencies
- one asset broadens trigger space without adding real capability
- a new internal asset fully supersedes an upstream one

### Bridge problems

Flag `AGENTS.md` when:

- it duplicates large sections from `.github/copilot-instructions.md`
- it claims a runtime that should remain abstract
- it routes to agents that do not exist
- its inventory references files that are gone

### Governance review gaps

Flag a sync workflow when:

- it does not report whether `.github/copilot-instructions.md` and root `AGENTS.md` were reviewed
- it marks work as `apply` even though governance review was skipped
- it proceeds to `apply` while `blocking` findings remain

## Flagging examples

- `blocking` / `Patch`: a skill references `references/example.md`, but that file is missing on disk.
- `non-blocking` / `Patch`: `AGENTS.md` still inventories a path that was deleted from `.github/`.
- `non-blocking` / `Keep`: two assets are adjacent in topic area, but their descriptions and trigger boundaries remain distinct.
- `blocking` / `Replace`: a repository-owned internal asset fully supersedes a weaker local fallback that still broadens trigger space.

## Recommended Outputs

Produce findings with both severity and action:

- Severity: `blocking` or `non-blocking`
- Action: `Delete`, `Replace`, `Patch`, or `Keep`

For each finding, include:

- asset path
- severity
- action
- issue type
- why it matters
- proposed replacement or fix

## No-Fallback Rule

When a repository-owned internal replacement exists, prefer deleting the weaker upstream asset instead of keeping a compatibility fallback.

## Anti-Patterns

- Keeping bundle skills that invoke non-existent helper skills
- Keeping source-side command-center assets in consumer sync scope
- Keeping upstream assets whose only value is historical familiarity
- Treating stale inventory references as harmless
