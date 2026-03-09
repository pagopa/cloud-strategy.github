# .github Configuration

This folder contains global GitHub Copilot customization that can be reused across repositories.

## Structure
- `copilot-instructions.md`: global baseline rules
- `copilot-commit-message-instructions.md`: commit message policy
- `copilot-code-review-instructions.md`: review policy
- `repo-profiles.yml`: reusable high-level profile catalog for different repo types
- `security-baseline.md`: portable security baseline checklist
- `DEPRECATION.md`: lifecycle policy for prompts/skills/instructions/agents
- `instructions/`: path-specific auto-applied rules
- `prompts/`: reusable slash prompts
- `skills/`: reusable implementation capabilities
- `agents/`: optional custom chat agents
- `scripts/`: validation scripts
- `workflows/`: CI validation workflows
- `templates/`: reusable templates (for example root-level `AGENTS.md`)

## Agent routing
- Read-only agents: `TechAIPlanner`, `TechAIReviewer`, `TechAISecurityReviewer`, `TechAIWorkflowSupplyChain`, `TechAITerraformGuardrails`, `TechAIIAMLeastPrivilege`
- Write-capable agent: `TechAIImplementer`
- Repo-only global customization agents: `TechAIGlobalCustomizationBuilder`, `TechAIGlobalCustomizationAuditor`

See `.github/agents/README.md` for details.

## Maintenance workflow
1. Update files under `.github/`.
2. Run `.github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
3. Optional: generate a machine-readable summary with `.github/scripts/validate-copilot-customizations.sh --scope root --mode strict --report json --report-file /tmp/copilot-report.json`.
4. Prefer cross-repo alignment with `python .github/scripts/tech-ai-sync-copilot-configs.py --target <repo-path> --mode plan` before any apply step.
5. Use `.github/scripts/bootstrap-copilot-config.sh --target <repo-path>` only as a legacy fallback bootstrap path (default excludes apply; see `.github/.bootstrap-ignore`).
6. Optionally run cross-repo assessment with `.github/scripts/validate-copilot-customizations.sh --scope all --mode legacy-compatible`.
7. Ensure workflow checks pass.
8. Update `.github/CHANGELOG.md` for notable changes.

## Notes
- `repo-profiles.yml` is currently advisory (human-readable profile catalog).
- The canonical project `AGENTS.md` belongs in repository root, not under `.github/`.
- `TechAIGlobalCustomizationBuilder`, `TechAIGlobalCustomizationAuditor`, `TechAILocalCopilotCustomizationBuilder`, and `TechAISyncCopilotConfigs` are repo-only source agents and must not be synced to consumer repositories.
- `.github/README.md`, `.github/agents/README.md`, `.github/templates/**`, and `.github/scripts/bootstrap-copilot-config.sh` are source-only assets and should not be part of consumer baselines.
- Use `templates/copilot-quickstart.md` for a short onboarding flow.
