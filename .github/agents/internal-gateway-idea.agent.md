---
name: internal-gateway-idea
description: "Use this agent when a repository-owned request starts with a vague idea, unclear goal, unresolved option set, or needs substantive definition, convergence, critical challenge, and retained planning before execution."
tools: ["read", "edit", "search", "execute", "web"]
disable-model-invocation: true
agents: []
handoffs:
  - label: "Next step: Execute compact plan"
    agent: "internal-gateway-execute-plans"
    prompt: "Execute only the approved compact retained plan left by the idea definition above. Verify the plan declares `Recommended consumer: internal-gateway-execute-plans`."
    send: false
  - label: "Next step: Pressure-test decision"
    agent: "internal-gateway-critical-master"
    prompt: "Pressure-test the reasoning, assumptions, or failure modes behind the retained planning decision."
    send: false
  - label: "Next step: Review target"
    agent: "internal-gateway-review-generic"
    prompt: "The work above became review-oriented rather than planning-oriented. Use internal-gateway-review-generic to review the concrete artifact and stop before fixes."
    send: false
---

# Internal Gateway Idea

## Core Skill

- `internal-gateway-idea`
