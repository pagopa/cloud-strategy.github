---
name: internal-gateway-review
description: "Use this agent when repository-owned work needs defect-first review, findings consolidation, and optional remediation planning without applying fixes."
tools: ["read", "search", "execute", "web"]
disable-model-invocation: true
agents: []
handoffs:
  - label: "Next step: Execute compact remediation"
    agent: "internal-gateway-simple-task"
    prompt: "Handle only the approved compact remediation left by the review above."
    send: false
  - label: "Next step: Reopen planning"
    agent: "internal-gateway-idea-brainstorming"
    prompt: "The review above reopened scope, ownership, or planning decisions. Re-establish the target state and retained-plan profile before execution."
    send: false
  - label: "Next step: Pressure-test remediation"
    agent: "internal-gateway-critical-master"
    prompt: "Pressure-test the remediation choices exposed by the review above."
    send: false
---

# Internal Gateway Review

## Core Skill

- `internal-gateway-review`
