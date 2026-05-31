---
name: "internal-review-ai-resources"
agent: "internal-gateway-operational-flow"
description: "Review repository-owned AI resources, referenced assets, and flow behavior across AGENTS.md and .github"
argument-hint: "Target one file, one or more folders, the full AI catalog, or an existing retained report package"
---

<!-- markdownlint-disable-file MD041 -->

Primary goal:
${input:goal:Describe why this review is needed and what decision it must support}

Review target:
${input:target:List one resource, several folders, the full AI catalog, or an existing retained report package}

Consumer surfaces:
${input:consumers:List relevant consumers such as GitHub Copilot, Codex, local sync, or write infer from repository evidence}

Known local assumptions or concerns:
${input:assumptions:List internal wrappers, imported-resource posture, known drift, prior findings, or write infer from repository evidence}

Desired depth:
${input:depth:Choose concise, detailed, or exhaustive; default to detailed when unsure}

Constraints and exclusions:
${input:constraints:List no-touch areas, rollout constraints, evidence limits, or explicit exclusions}

Output preference:
${input:output:Write chat-only, retained report under tmp/, or infer from target size}

Use these repository sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [INTERNAL_CONTRACT.md](../../INTERNAL_CONTRACT.md)
- [.github/agents/internal-gateway-operational-flow.agent.md](../agents/internal-gateway-operational-flow.agent.md)
- [.github/skills/internal-gateway-operational-flow/SKILL.md](../skills/internal-gateway-operational-flow/SKILL.md)
- [.github/skills/internal-ai-resource-review/SKILL.md](../skills/internal-ai-resource-review/SKILL.md)

Then use `internal-ai-resource-review` as the reusable qualitative owner for
profile selection, target coverage, lifecycle checks, report shape, and bundle
review depth.

Review target may be one resource path, one or more folders, the full AI
catalog, or an existing retained review package under `tmp/`. Use the skill to
select `focused`, `bundle`, `catalog`, or `retained-report` and keep the review
analysis-only.

If the target is a skill bundle, treat the bundle root plus existing
`references/`, `scripts/`, `assets/`, and `agents/openai.yaml` as in scope.

Load additional repository skills only when the target or its evidence path
needs their owner rules. In particular, load
`internal-copilot-audit` only when overlap, hollow references, stale contracts,
naming drift, or governance drift findings are needed. Do not load every skill
only because it exists.

Use `LESSONS_LEARNED.md` only when it is explicitly in the target, referenced by
an in-scope resource, or needed to verify a retained-learning claim. Treat it as
non-canonical retained evidence until codified in the smallest valid owner.

The review is analysis-only. Do not modify the reviewed resources. If retained
analysis is needed, write only under `tmp/`.

Do not name vendor-specific reasoning engines or compare them. Review consumer
surfaces, contracts, and repository behavior instead.

Do not produce an encyclopedic review. Include only real problems, important
tradeoffs, recommended decisions, blocking uncertainties, and high-ROI quick
wins. If a resource has no meaningful problem, use an explicit keep result and
move on.

Do not propose new technology before diagnosing the existing repository
correctly.

## Language Rules

- Write the final analysis and summary in the language of the current chat.
- If the current chat language is ambiguous or mixed, prefer Italian.
- Keep file paths, enum values, evidence labels, status labels, and command names
  exactly as requested.
