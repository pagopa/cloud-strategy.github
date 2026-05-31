---
name: internal-azure-devops
description: Use when authoring, reviewing, or routing Azure DevOps pipelines or project automation before CLI operations need a narrower owner.
---

# Internal Azure DevOps

## Referenced skills

- `internal-yaml`: baseline YAML structure when editing Azure DevOps pipeline YAML.
- `awesome-copilot-azure-devops-cli`: Azure DevOps CLI operations, projects, repos, pipelines, builds, pull requests, work items, artifacts, and service endpoints.

## When to use

- Azure DevOps pipeline YAML files such as `azure-pipelines.yml`, `azure-pipelines*.yml`, or `*.pipeline.yml`.
- Azure DevOps automation where the first question is ownership, routing, permissions posture, or validation shape.
- Reviews that need to check pipeline structure, triggers, variables, environments, approvals, or artifact flow.

## When not to use

- GitHub Actions workflows or composite actions; use the GitHub Actions owners.
- Azure CLI or Azure Resource Manager work with no Azure DevOps project or pipeline surface.
- Direct Azure DevOps CLI execution; use `awesome-copilot-azure-devops-cli`.

## Baseline

- Keep pipelines readable with clear names for stages, jobs, steps, variables, and environments.
- Use least-privilege service connections and avoid hardcoded secrets.
- Prefer parameters, variable groups, and templates when they reduce real duplication.
- Keep build, test, package, and deploy responsibilities clear enough that failures point to the right stage.
- Make production promotion, approvals, rollback, and health checks explicit when deployment is in scope.
- Preserve existing repository conventions before introducing new pipeline structure.

## Pipeline depth

Load `references/pipelines.md` when the task needs a pipeline checklist, deployment strategy review, variable and parameter rules, or a richer Azure DevOps YAML baseline.

## Validation

- Validate YAML syntax with the closest repository check.
- Run the pipeline linter, dry run, or Azure DevOps validation command when the repository provides one.
- For security-sensitive changes, confirm secrets are referenced through approved stores or service connections.
