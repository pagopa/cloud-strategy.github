---
name: internal-gateway-critical-master
description: "Use this agent when a repository-owned plan, proposal, decision, or assumption set needs critical challenge before action."
tools: ["read", "search"]
disable-model-invocation: true
agents: []
handoffs:
  - label: "Next step: Reopen planning"
    agent: "internal-gateway-idea-brainstorming"
    prompt: "Continue from the critical outcome above by reopening planning."
    send: false
  - label: "Next action: Use simple fast path"
    agent: "internal-gateway-simple-task"
    prompt: "Handle only the concrete simple task left by the critical outcome."
    send: false
  - label: "Next step: Review evidence"
    agent: "internal-gateway-review"
    prompt: "Continue from the critical outcome above through defect-first evidence review."
    send: false
---

# Internal Gateway Critical Master

## Core Skill

- `internal-gateway-critical-master`
