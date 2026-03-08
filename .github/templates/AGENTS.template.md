# AGENTS.md - <repository-name>

This file is for GitHub Copilot and AI assistants working in this repository.

## Naming Policy
- Use GitHub Copilot terminology in repository-facing content.
- Keep repository-facing text in English.
- Treat prompt frontmatter `name:` as the canonical command identifier.

## Decision Priority
1. Apply repository non-negotiables from `.github/copilot-instructions.md`.
2. Apply explicit user requirements for the current task.
3. Apply the selected agent behavior.
4. Apply matching `.github/instructions/*.instructions.md` files.
5. Apply selected prompt constraints from `.github/prompts/*.prompt.md`.
6. Apply implementation details from referenced `.github/skills/*/SKILL.md`.

## Agent Routing
- Keep agent guidance short and behavioral.
- Document only the preferred agents for this repository and when to use them.
- Keep file path references in `Repository Inventory (Auto-generated)` only.

## Repository Defaults
- Primary focus: <one-line repository summary>
- Priority paths:
  - `<path>`
  - `<path>`

### Default instruction routing
- `<glob>` -> `<instruction label>`

### Preferred prompts
- `<PromptName>`: <when to use it>

### Preferred skills
- `<SkillName>`: <when to use it>

### Required validations before PR
- `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`

## Repository Inventory (Auto-generated)

### Instructions
- `.github/instructions/<file>.instructions.md`

### Prompts
- `.github/prompts/<file>.prompt.md`

### Skills
- `.github/skills/<skill>/SKILL.md`

### Agents
- `.github/agents/<agent>.agent.md`
