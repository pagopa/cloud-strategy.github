---
name: "internal-review-ai-resources"
agent: "internal-gateway-operational-flow"
description: "Review repository-owned AI resources and their local contracts before cleanup, refactor, or rollout decisions."
argument-hint: "Target one file, one or more folders, the full AI catalog, or an existing retained report package"
---

<!-- markdownlint-disable-file MD041 -->

Primary goal:
${input:goal:Describe the decision this review must support.}

Review target:
${input:target:List one resource, folders, the full AI catalog, or an existing retained report package under tmp/.}

Consumers in scope:
${input:consumers:List consumers such as GitHub Copilot, Codex, local sync, or write infer from repository evidence.}

Constraints and exclusions:
${input:constraints:List no-touch areas, rollout constraints, or explicit exclusions.}

Desired depth:
${input:depth:Choose concise, detailed, or exhaustive. Default to detailed when unsure.}

Output preference:
${input:output:Write chat-only, retained report under tmp/, or infer from target size.}

Use these sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- the resolved target path or paths
- every scoped instruction whose `applyTo` matches an in-scope target path

Load only when needed:

- [.github/INVENTORY.md](../INVENTORY.md) for catalog, sync, naming, or
  propagation claims
- [.github/agents/internal-gateway-operational-flow.agent.md](../agents/internal-gateway-operational-flow.agent.md)
  and [.github/skills/internal-gateway-operational-flow/SKILL.md](../skills/internal-gateway-operational-flow/SKILL.md)
  for phase, handoff, or completion claims
- [.github/skills/internal-copilot-audit/SKILL.md](../skills/internal-copilot-audit/SKILL.md)
  for overlap, hollow-reference, governance-drift, and bundle-health checks
- creator skills only when the recommendation would create, split, retire, or
  replace those resource families

Review contract:

- Review only the target families and the direct references needed to support
  the decision.
- If the target is `.github/skills/<name>/` or `.github/skills/<name>/SKILL.md`,
  resolve the owning skill bundle and keep its bundle siblings (`references/`,
  `scripts/`, `assets/`, and `agents/openai.yaml`) in scope unless explicitly
  excluded.
- For skill bundles, treat existing bundle siblings as default in-scope
  coverage.
- For skill bundles, confirm each existing bundle sibling was reviewed, marked
  absent, or marked intentional non-action in the source-item coverage matrix.
- Start with the smallest evidence pass that can confirm or disconfirm the main
  concern.
- Use the smallest output shape that supports the decision.
- Do not modify reviewed resources. Write retained analysis only under `tmp/`.

Core review lenses:

- ownership and boundary clarity
- activation and usage proof
- reference health and bundle completeness
- validation, sync, and propagation coverage
- context cost, lazy-load fit, and token ROI
- flow behavior when plan, execute, apply-plan, review, or handoff semantics
  are part of the target

Required output contract:

1. `Executive summary`
2. `Target and coverage`, including a source-item coverage matrix
3. `Main findings`
4. `Decision table`
5. `Validation and open questions`

Allowed statuses: `KEEP`, `WRAP`, `REVISE`, `COMPRESS`, `SPLIT`, `MERGE`,
`MOVE`, `RENAME`, `RETIRE`, `CREATE`, `AUTOMATE`, `REVIEW`.
