# Internal Copilot Asset Naming Rules

## Prefix convention

All repository-owned Copilot assets **must** use the `internal-` prefix. The `tech-ai-*` prefix is reserved exclusively for shared baseline assets managed by the source repository.

## File naming

| Asset type | Location | Filename pattern | Example |
|---|---|---|---|
| Prompt | `.github/prompts/` | `internal-<domain>.prompt.md` | `internal-deploy-checklist.prompt.md` |
| Skill | `.github/skills/internal-<domain>/` | `SKILL.md` | `.github/skills/internal-scp-authoring/SKILL.md` |
| Agent | `.github/agents/` | `internal-<domain>.agent.md` | `internal-incident-responder.agent.md` |
| Instruction | `.github/instructions/` | `internal-<domain>.instructions.md` | `internal-terraform-conventions.instructions.md` |

## Frontmatter `name:` field

The `name:` field in YAML frontmatter must match the `internal-<domain>` pattern:

```yaml
---
name: internal-scp-authoring
description: ...
---
```

**Never** use `TechAI*` or `tech-ai-*` in repo-owned frontmatter names.

## Domain naming guidelines

- Use lowercase kebab-case: `internal-deploy-checklist` (not `internal-DeployChecklist`).
- Keep domain segment short and descriptive (2-3 words max).
- Match the domain segment to the repo's vocabulary (e.g., if the repo calls it "scp" don't use "service-control-policy").

## AGENTS.md inventory format

When adding internal assets to the repo's `AGENTS.md`, use explicit paths:

```markdown
## Internal Assets
- **internal-scp-authoring** — skill for authoring organization SCPs
  - `.github/skills/internal-scp-authoring/SKILL.md`
- **internal-deploy-checklist** — prompt for pre-deploy validation
  - `.github/prompts/internal-deploy-checklist.prompt.md`
```

## What NOT to do

| Anti-pattern | Why | Correct approach |
|---|---|---|
| `tech-ai-my-custom.prompt.md` | Collides with shared baseline prefix | `internal-my-custom.prompt.md` |
| `my-repo-deploy.prompt.md` | No standard prefix — hard to distinguish ownership | `internal-deploy.prompt.md` |
| `INTERNAL-CAPS.prompt.md` | Case inconsistency | `internal-lowercase.prompt.md` |
| Duplicating a `tech-ai-*` skill as `internal-*` | Double maintenance, drift | Reference shared skill by path instead |
