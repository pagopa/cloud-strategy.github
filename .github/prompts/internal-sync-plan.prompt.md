---
agent: "agent"
description: "Prepare a source-authoritative sync or catalog-governance plan before applying changes to a consumer repository"
---

Source repository or branch:
${input:source:Describe the source standards repo or branch under consideration}

Target repository or consumer scope:
${input:target:Describe the consumer repo, branch, or sync target}

Requested sync or governance change:
${input:change:Describe the desired sync, refresh, retire, or drift-remediation action}

Target-local exceptions to preserve:
${input:local:List local assets, overrides, or no-touch areas if known}

Use these repository sources first:
- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [CONTRIBUTING.md](../../CONTRIBUTING.md)
- [.github/DEPRECATION.md](../DEPRECATION.md)
- [VERSION](../../VERSION)

Produce a sync brief with:

1. Source-managed scope versus target-local assets
2. Versioning impact and any release note implications
3. Files or categories that should be preserved, updated, created, or removed
4. Validation plan before apply
5. Apply or no-apply recommendation with key risks