---
name: internal-azure-devops
description: Use when /internal-azure selects Azure DevOps pipeline YAML, project automation, triggers, environments, approvals, or artifact-flow work.
---

# Internal Azure DevOps

Use this workflow for Azure DevOps pipeline and project-automation delivery or
review.

## When to use

Use when `/internal-azure` selects a pipeline, environment-promotion, or Azure
DevOps automation deliverable.

## Workflow

1. Perform request classification: identify pipeline authoring, pipeline review,
   project automation, deployment flow, or repository integration.
2. Complete repository convention discovery: inspect existing pipeline files,
   templates, agent images, validation commands, variables, environments, and
   deployment conventions.
3. Produce the pipeline or automation design with intentional triggers,
   stages, jobs, dependencies, templates, parameters, variables, environments,
   approvals, and artifact flow.
4. Define security controls: least-privilege service connections, approved
   secret stores, protected environments, and safe logging.
5. Make rollback, health checks, and promotion gates explicit whenever
   deployment is in scope.
6. Run focused validation for YAML syntax, repository checks, pipeline linting,
   dry runs, or Azure DevOps validation commands available in the repository.

## Pipeline principles

- Keep build, test, package, and deploy responsibilities clear enough that
  failures point to the owning stage.
- Use parameters for caller-controlled choices and variable groups for shared
  configuration.
- Publish test results and artifacts with recognizable names.
- Preserve repository conventions before introducing new pipeline structure.

Load `references/pipelines.md` for the deeper authoring and review baseline.

## Completion criteria

Return the classified request, discovered conventions, pipeline or automation
design, security controls, rollback posture, and focused validation result.
