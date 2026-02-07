# .github Configuration

This folder contains global Copilot/Codex customization for Cloud Strategy repositories.

## Structure
- `copilot-instructions.md`: global baseline rules
- `copilot-commit-message-instructions.md`: commit message policy
- `copilot-code-review-instructions.md`: review policy
- `instructions/`: path-specific auto-applied rules
- `prompts/`: reusable slash prompts
- `skills/`: reusable implementation capabilities
- `agents/`: optional custom chat agents
- `scripts/`: validation scripts
- `workflows/`: CI validation workflows
- `templates/`: reusable templates (for example `AGENTS.md`)

## Maintenance workflow
1. Update files under `.github/`.
2. Run `.github/scripts/validate-copilot-customizations.sh`.
3. Ensure workflow checks pass.
4. Update `.github/CHANGELOG.md` for notable changes.
