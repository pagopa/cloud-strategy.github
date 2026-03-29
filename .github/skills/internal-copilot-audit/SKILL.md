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
- Detect deprecated frontmatter and stale runtime-specific wording.
- Detect weak `AGENTS.md` bridge design.
- Detect naming violations and stale inventory references.
- Detect governance files that still describe removed, renamed, or retired assets.

## Audit Order

1. Check naming and frontmatter.
2. Check broken local references.
3. Check trigger overlap.
4. Check bridge coherence between `AGENTS.md` and `.github/copilot-instructions.md`.
5. Check whether prompts, skills, or agents became redundant after internal replacements were added.
6. Check whether governance files still describe superseded or removed assets.

## What To Flag

### Hollow assets

Flag an asset when:

- it references `resources/` or `references/` files that do not exist
- it tells the model to invoke skills or agents that are not installed
- it depends on assistant-runtime features not supported by the repository target

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

## Recommended Outputs

Produce findings grouped as:

- `Delete`
- `Replace`
- `Patch`
- `Keep`

For each finding, include:

- asset path
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
