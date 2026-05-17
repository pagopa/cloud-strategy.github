---
name: "internal-agent-pressure-test-plan"
agent: "internal-critical-master"
description: "Pressure-test a plan or proposal before merge, refactor, or cross-boundary implementation"
---

<!-- markdownlint-disable-file MD041 -->

Proposal or decision under test:
${input:proposal:Describe the proposal, plan, or change you want challenged}

Scope and blast radius:
${input:scope:List the files, repos, systems, or teams affected}

Assumptions to challenge:
${input:assumptions:List the assumptions you want stress-tested}

Constraints or non-negotiables:
${input:constraints:List technical, policy, or rollout constraints}

Use these repository sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/agents/internal-critical-master.agent.md](../agents/internal-critical-master.agent.md)
- [.github/skills/internal-gateway-critical-master/SKILL.md](../skills/internal-gateway-critical-master/SKILL.md)
- [.github/skills/internal-agent-support-lane-change-engine/SKILL.md](../skills/internal-agent-support-lane-change-engine/SKILL.md)
- [.github/skills/internal-agent-support-next-step/SKILL.md](../skills/internal-agent-support-next-step/SKILL.md)

Return a compact pressure test with:

1. Proposal or decision under test
2. Assumptions under test
3. Top failure modes
4. Counter-framing or inversion result
5. Explicit outcome: `reformulate-plan`, `de-escalate-to-simple`, `execute-clear-next-step`, `review-evidence`, `continue-critical`, or `accept-with-risk`
6. Return-to-owner next-step package when another lane should act
7. Residual risk if the proposal still goes ahead
