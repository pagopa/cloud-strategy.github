---
name: internal-azure-devops
description: Use when the user needs Azure DevOps pipeline YAML authoring or review, project automation, pipeline triggers, variables, environments, approvals, or artifact-flow guidance. Do not use for GitHub Actions; Azure CLI or Resource Manager work with no pipeline surface; tenant, governance, or operations design; or materially ambiguous requests with no clear pipeline deliverable.
---

# Internal Azure DevOps

## Handoffs

| To | When |
|---|---|
| `internal-azure` | material routing uncertainty prevents selecting a primary Azure specialist |
| `internal-yaml` | baseline YAML structure when editing pipeline YAML |
| `awesome-copilot-azure-devops-cli` | direct CLI operations |

## When to use

- Azure DevOps pipeline YAML files such as `azure-pipelines.yml`, `azure-pipelines*.yml`, or `*.pipeline.yml`.
- Azure DevOps automation where the first question is ownership, routing, permissions posture, or validation shape.
- Reviews that need to check pipeline structure, triggers, variables, environments, approvals, or artifact flow.

## When not to use

- GitHub Actions workflows or composite actions; use the GitHub Actions owners.
- Azure CLI or Azure Resource Manager work with no Azure DevOps project or pipeline surface.
- Direct Azure DevOps CLI execution; use `awesome-copilot-azure-devops-cli`.
- The request is materially ambiguous and no primary Azure owner can be named → `internal-azure`.

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
