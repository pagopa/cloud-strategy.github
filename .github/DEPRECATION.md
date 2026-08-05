# Deprecation Policy

## Purpose

Define a predictable process for deprecating Copilot customization assets:
`skills`, `agents`, prompts, and templates.

## Lifecycle states

- Active: recommended for current use.
- Deprecated: still available but scheduled for removal.
- Removed: no longer maintained or supported.

## Required process

1. Mark the asset as deprecated in its file header or first section.
2. Record the change in `.github/CHANGELOG.md` with migration guidance.
3. Keep a minimum deprecation window of one release cycle (or 30 days if no release cycle exists).
4. Provide a replacement asset when possible.
5. Remove only after the window ends and no blocking consumers remain.

## Backward compatibility rules

- Skills: keep old skill path available during transition.
- Agents: keep objective and restriction semantics stable where possible.

## Architecture-migration exception

The skill-first migration is an approved architecture exception to the normal
release-cycle window. It migrates owners, routing, references, and validation
coverage before removing the retired path-specific instruction family in the
same execution. Old Lambda skill-path handling follows the same exception: the
canonical owner is `.github/skills/internal-aws-lambda/`, and the retired
`.github/skills/internal-aws-serverless/` compatibility path is removed after
the replacement owner validates.

## Emergency exception

Immediate removal is allowed only for security or compliance issues. The removal reason must be documented in
`.github/CHANGELOG.md`.

## Current deprecations

- `.github/skills/ibm-terraform-test/`: **Removed immediately under the approved
  architecture-migration exception** on 2026-08-05 with explicit user
  authorization. Native tests and all non-language Terraform work now use
  `/internal-terraform` → `/antonbabenko-terraform-skill`. Roll back by restoring
  the last Git revision containing the complete bundle.
- `.github/workflows/_terraform-pre-commit.yml`: **Removed**. Replaced by `.github/workflows/_pre-commit.yml` after
  duplicate pre-commit workflows were consolidated into one canonical entrypoint.
- `.github/workflows/terraform-pre-commit.yml`: **Removed**. Replaced by `.github/workflows/_pre-commit.yml` so the
  source baseline ships one pre-commit workflow.
- `.github/skills/antigravity-domain-driven-design/SKILL.md`: **Removed**. Consolidated into
  `.github/skills/internal-ddd/SKILL.md`.
- `.github/skills/internal-data-registry/SKILL.md`: **Removed**. Retired from the live catalog after confirmation that
  no live references remained.
- `.github/scripts/bootstrap-copilot-config.sh`: **Removed**. Replaced by the
  `local-sync-repos` agent and skill workflow.
- `.github/skills/internal-terraform-feature/SKILL.md`: **Removed**. Merged into
  `.github/skills/internal-terraform/SKILL.md`.
- `.github/skills/internal-terraform-module/SKILL.md`: **Removed**. Merged into
  `.github/skills/internal-terraform/SKILL.md`.
- `.github/instructions/`: **Historical retirement under architecture-migration exception**. The broad,
  workflow-heavy instruction model was retired; a governed review-only instruction family was later
  reintroduced with focused checks and explicit `excludeAgent: "cloud-agent"` scoping.
- `.github/skills/internal-aws-serverless/SKILL.md`: **Removed under architecture-migration exception**. Replaced
  by `.github/skills/internal-aws-lambda/SKILL.md`.
- `.github/skills/internal-copilot-instructions-creator/SKILL.md`: **Removed under architecture-migration
  exception**. Its remaining useful ownership routes were split across skill, agent, prompt, validator, and
  owned-file authoring guidance.
