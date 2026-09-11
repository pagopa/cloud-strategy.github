# Catalog Governance Rules

These rules govern repository-owned Copilot catalog assets, their source ownership, and their validation surfaces.

## skill-first-root-agents-is-entrypoint - Root agent entrypoint

- Rule ID: skill-first-root-agents-is-entrypoint
- Owner: Catalog governance
- Severity: blocking
- Enforcement owner: `.github/tools/catalog/rules.py` checks required bridge presence and selected references; detailed content placement is not enforced
- Evidence: `INTERNAL_CONTRACT.md`, `AGENTS.md`, `.github/tools/catalog/rules.py`
- Remediation: Restore the root entrypoint role and remove duplicated procedural detail from always-on policy.
- Rule: `AGENTS.md` remains the stable repository entrypoint; volatile inventory and detailed procedures stay in their canonical owners.

## skill-first-inventory-is-externalized - Inventory ownership

- Rule ID: skill-first-inventory-is-externalized
- Owner: Catalog governance
- Severity: blocking
- Enforcement owner: `.github/tools/catalog/rules.py` through `make catalog-check`
- Evidence: `INTERNAL_CONTRACT.md`, `AGENTS.local.md`, `.github/INVENTORY.md`, `.github/tools/inventory/inventory.py`
- Remediation: Rebuild the inventory from filesystem state and keep policy files limited to pointing at it.
- Rule: `.github/INVENTORY.md` is the exact live asset inventory and policy files must not duplicate it.

## skill-first-domain-skills-are-canonical - Skill ownership

- Rule ID: skill-first-domain-skills-are-canonical
- Owner: Catalog governance
- Severity: blocking
- Enforcement owner: `.github/tools/skills/rules.py` validates selected bundle structure; canonical guidance ownership is not enforced end to end
- Evidence: `INTERNAL_CONTRACT.md`, `.github/skills/internal-knowledge/SKILL.md`, `AGENTS.local.md`, `.github/tools/skills/rules.py`
- Remediation: Move reusable domain guidance into the smallest valid skill owner and keep the always-on entrypoint compact.
- Rule: Repository-owned skills are the canonical home for reusable technical-domain guidance and their bundles remain self-contained.
