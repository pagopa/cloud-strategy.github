# Source Synchronization Rules

These rules govern source-to-target synchronization and preservation of consumer-owned assets.

## skill-first-knowledge-docs-keep-ownership-split - Knowledge ownership

- Rule ID: skill-first-knowledge-docs-keep-ownership-split
- Owner: Source synchronization
- Severity: blocking
- Enforcement owner: not enforced
- Evidence: `INTERNAL_CONTRACT.md`, `.github/skills/local-sync-repos/references/sync-contract.md`, `.github/skills/local-agent-sync-install-ai-resources/references/sync-contract.md`
- Remediation: Keep source-managed files and consumer-local knowledge separate, and block ambiguous coexistence.
- Rule: Synchronization preserves existing consumer-local knowledge and does not turn target-local files into source-managed policy.

## resource-governance-uses-supported-origin-naming - Resource origin naming

- Rule ID: resource-governance-uses-supported-origin-naming
- Owner: Source synchronization
- Severity: blocking
- Enforcement owner: not enforced
- Evidence: `INTERNAL_CONTRACT.md`, `.github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml`, `.github/skills/local-sync-repos/SKILL.md`
- Remediation: Rename or classify the resource according to its actual repository origin before synchronization.
- Rule: Repository-local resources use `internal-*`, imported resources use the supported external origin prefix, and cross-repository resources use `local-*`.

## home-sync-preserves-home-only-resources - Home-only preservation

- Rule ID: home-sync-preserves-home-only-resources
- Owner: Source synchronization
- Severity: blocking
- Enforcement owner: `.github/skills/local-agent-sync-install-ai-resources/scripts/home_syncing.py` and `.github/skills/local-agent-sync-install-ai-resources/tests/scripts/test_apply_paths.py`
- Evidence: `.github/skills/local-agent-sync-install-ai-resources/references/sync-contract.md`, `.github/skills/local-agent-sync-install-ai-resources/tests/scripts/test_apply_paths.py`
- Remediation: Preserve home-only skills and resolve ownership before applying a plan.
- Rule: Home-only skills, local bundles, invalid repository bundles, and catalog-excluded IDs remain untouched by repository-to-home synchronization.
