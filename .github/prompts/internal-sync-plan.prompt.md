---
name: "internal-sync-plan"
agent: "local-sync-global-copilot-configs-into-repo"
description: "Plan a source-authoritative consumer-repository sync without applying it."
argument-hint: "Source repo or branch, target repo, requested sync change, and target-local exceptions to preserve"
---

<!-- markdownlint-disable-file MD041 -->

Source repository or branch:
${input:source:Describe the source standards repo or branch under consideration.}

Target repository or consumer scope:
${input:target:Describe the consumer repo, branch, or sync target.}

Requested sync or governance change:
${input:change:Describe the desired sync, refresh, retire, or drift-remediation action.}

Target-local exceptions to preserve:
${input:local:List local assets, overrides, or no-touch areas if known.}

Use these sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [.github/agents/local-sync-global-copilot-configs-into-repo.agent.md](../agents/local-sync-global-copilot-configs-into-repo.agent.md)
- [.github/skills/local-agent-sync-global-copilot-configs-into-repo/SKILL.md](../skills/local-agent-sync-global-copilot-configs-into-repo/SKILL.md)
- [VERSION](../../VERSION)

Planning contract:

- This prompt is for source-authoritative consumer-repository sync planning, not
  for source-side catalog governance apply work.
- If the real task is source-side `.github/` catalog governance, route it to
  `local-sync-external-resources` instead of forcing this plan shape.
- Keep target `local-*` assets and any consumer-local override layer visible in
  the plan.
- Prefer a conflict-safe plan with explicit validation over implied apply
  approval.

Produce a sync brief with:

1. selected mode and why it fits
2. source-managed scope versus target-local assets
3. planned create, update, preserve, and delete actions
4. validation path before apply
5. blockers, rollout risks, and no-apply conditions
