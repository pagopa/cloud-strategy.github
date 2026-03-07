# Copilot Customization Quickstart

## Goal
Bootstrap a repository with a minimal, portable `.github` Copilot customization setup.

For detailed maintenance and validation flow, refer to `.github/README.md`.

## Steps
1. Copy baseline files:
   - `.github/copilot-instructions.md`
   - `.github/copilot-commit-message-instructions.md`
   - `.github/copilot-code-review-instructions.md`
2. Add stack-specific instruction files from `.github/instructions/`.
3. Add prompt files from `.github/prompts/` relevant to the team workflow.
4. Add matching skills from `.github/skills/` referenced by prompts.
5. Run `.github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.

## Suggested starter sets
- Java repositories: `java.instructions.md`, `tech-ai-java.prompt.md`, `tech-ai-project-java/SKILL.md`
- Node.js repositories: `nodejs.instructions.md`, `tech-ai-nodejs.prompt.md`, `tech-ai-project-nodejs/SKILL.md`
- CI-focused repositories: `github-actions.instructions.md`, `tech-ai-github-action.prompt.md`, `tech-ai-cicd-workflow/SKILL.md`

## Validation gate
Add `.github/workflows/github-validate-copilot-customizations.yml` to enforce consistency in pull requests.

## Alignment strategy
- Use `.github/scripts/bootstrap-copilot-config.sh --target <repo-path>` in dry-run first for the initial copy.
- Use `python .github/scripts/tech-ai-sync-copilot-configs.py --target <repo-path> --mode plan` for conservative alignment and minimum-asset selection.
- Prefer canonical `tech-ai-*` script prompts in consumer repositories to reduce prompt duplication and token footprint.
