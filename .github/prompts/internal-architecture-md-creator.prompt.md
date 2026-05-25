---
name: "internal-architecture-md-creator"
agent: "internal-gateway-operational-flow"
description: "Generate or refresh a repository `docs/01-architecture.md` contract from repository evidence."
argument-hint: "Optional target repository path plus optional focus, constraints, or chat-language preference"
---

<!-- markdownlint-disable-file MD041 -->

Target repository:
${input:repository:Repository path or name. Leave empty to target the current repository root.}

Optional focus areas:
${input:focus:Optional focus such as runtime flow, IaC layout, CI/CD, testing, security boundaries, monorepo split, or AI-agent risk surface.}

Optional constraints or exclusions:
${input:constraints:Optional non-negotiables, ADRs to preserve, sections to skip, or areas to leave unchanged.}

Chat response language:
${input:language:Match the current chat unless explicitly overridden. Retained artifact content must stay in English.}

Use these sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [.github/agents/internal-gateway-operational-flow.agent.md](../agents/internal-gateway-operational-flow.agent.md)
- [.github/skills/internal-gateway-operational-flow/SKILL.md](../skills/internal-gateway-operational-flow/SKILL.md)

Execution contract:

1. Resolve `repository` to a real workspace path. Ask only if the repository is
   still unresolved after obvious path checks.
2. Inspect the repository before writing. Prefer evidence from source code,
   config, workflows, tests, IaC, and existing docs.
3. Create or update only `docs/01-architecture.md`.
4. Keep retained artifact content, headings, tables, and filenames in English.
   The chat summary may follow the requested chat language.
5. Do not invent architecture. Mark unsupported claims as `Unknown / To verify`.
6. If `docs/01-architecture.md` already exists, refresh it in place and remove
   claims that current evidence no longer supports.
7. If the request conflicts with the observed architecture, explain the conflict
   before editing.

Required artifact outline:

```md
# Architecture

## 1. Purpose
## 2. System overview
## 3. Current vs intended architecture
## 4. Technology stack
## 5. Repository map
## 6. Architectural boundaries
## 7. Dependency rules
## 8. Key flows
## 9. Configuration and environment
## 10. Testing and validation
## 11. Architectural decisions visible in the repo
## 12. AI-agent working rules
## 13. Last verified
## 14. Unknown / To verify
```

Output rules:

- Keep the document concise, evidence-based, and stable enough for repeated
  AI-agent use.
- Use source paths when a claim is `Documented`, `Evidenced`, or `Inferred`.
- Never expose secret values.
- Suggest `AGENTS.md` or `.github/copilot-instructions.md` snippet updates only
  in chat when the repository would clearly benefit. Do not edit those files
  unless explicitly requested.
