---
name: "internal-agent-review-next-actions"
agent: "internal-gateway-operational-flow"
description: "Kick off defect-first review findings with causal layers and routed next actions"
---

<!-- markdownlint-disable-file MD041 -->

Change, diff, or asset to review:
${input:subject:Describe the PR, diff, file set, or asset under review}

Focus area:
${input:focus:Optional focus such as security, regressions, routing, or validation}

Known assumptions or concerns:
${input:concerns:List any risks, assumptions, or reviewer comments already in play}

Use these repository sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-code-review-instructions.md](../copilot-code-review-instructions.md)
- [.github/skills/internal-gateway-operational-flow/SKILL.md](../skills/internal-gateway-operational-flow/SKILL.md)
- [.github/skills/internal-code-review/SKILL.md](../skills/internal-code-review/SKILL.md)
- [.github/skills/internal-agent-support-next-step/SKILL.md](../skills/internal-agent-support-next-step/SKILL.md)
- [.github/agents/internal-gateway-operational-flow.agent.md](../agents/internal-gateway-operational-flow.agent.md)

If `subject` is a repository-owned bundle owner such as `SKILL.md`, review bundle siblings (`references/`, `scripts/`, `assets/`, and `agents/openai.yaml`) or mark the intentional non-action.

Produce review findings with:

1. Severity and confidence on every finding
2. Causal layer and fix routing plan for every actionable finding
3. Evidence gaps
4. Self-questioning notes for the most severe finding
5. Residual risks if no further changes are made
6. Recommended owner and next-step package if the task is no longer review-owned
