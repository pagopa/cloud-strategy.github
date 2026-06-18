---
name: internal-gateway-simple-task
description: "Use this agent when a concrete low-to-medium-risk repository-owned task can be answered, edited, diagnosed, validated quickly, executed, or switched to plan mode to produce a retained plan instead of same-chat execution."
tools: ["read", "edit", "search", "execute", "web"]
disable-model-invocation: true
agents: []
handoffs:
  - label: "Next step: Reopen planning"
    agent: "internal-gateway-idea-brainstorming"
    prompt: "Reopen planning because this task no longer fits the simple single-lane fast path. Preserve scope, validation, and risk, then choose the right retained-plan profile before execution."
    send: false
  - label: "Next step: Pressure-test task"
    agent: "internal-gateway-critical-master"
    prompt: "Pressure-test the reasoning, assumptions, or failure modes that made this task leave the simple fast path."
    send: false
  - label: "Next step: Review target"
    agent: "internal-gateway-review"
    prompt: "The work above became defect-first analysis rather than direct execution. Review the concrete target and stop before applying fixes."
    send: false
---

# Internal Gateway Simple Task

## Core Skill

- `internal-gateway-simple-task`
