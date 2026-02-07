# Changelog

## 2026-02-07
- Added missing global Copilot instruction files for commit messages and code review.
- Added new instruction files: YAML, Markdown, Makefile, Scripts, Lambda.
- Added new skills: `terraform-module`, `cloud-policy`.
- Added `.github/README.md` and `AGENTS` template.
- Added custom agents: `Planner`, `Implementer`, `Reviewer`, `SecurityReviewer`, `WorkflowSupplyChain`, `TerraformGuardrails`, `IAMLeastPrivilege`.
- Added `.github/agents/README.md` with routing guidance.
- Hardened prompt/skill/instruction/agent validation and workflow checks.
- Added validator scope/mode support: `--scope root|all|repo=<name>` and `--mode strict|legacy-compatible`.
- Added validator JSON reporting support: `--report json --report-file <path>`.
- Added `repo-profiles.yml` for reusable high-level repository profiles.
- Added `security-baseline.md` and `DEPRECATION.md`.
- Added `instructions/composite-action.instructions.md` for reusable composite actions.
- Added `scripts/bootstrap-copilot-config.sh` for safe `.github` bootstrap and sync.
- Added `templates/copilot-quickstart.md` for portable onboarding.
- Updated docs to be repository-agnostic and reusable across different tech stacks.
