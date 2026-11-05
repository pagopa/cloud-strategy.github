---
name: internal-azure-devops
description: Use when creating, reviewing, or changing Azure DevOps pipeline YAML, templates, triggers, environments, approvals, service connections, variable groups, or project automation. Route Azure DevOps CLI execution to /awesome-copilot-azure-devops-cli and tool-neutral delivery strategy to /internal-devops-core-principles.
---

# Internal Azure DevOps

Use this workflow for Azure DevOps pipeline and project-automation delivery or
review.

## When to use

- Author or review `azure-pipelines*.yml`, pipeline templates, and their
  triggers, stages, jobs, parameters, and variables.
- Design environment promotion, approvals and checks, service connections,
  variable groups, and artifact flow.
- Automate Azure DevOps project configuration through pipelines.

Hand off:

- CLI command execution: `/awesome-copilot-azure-devops-cli`;
- tool-neutral delivery strategy: `/internal-devops-core-principles`;
- Azure RBAC, landing-zone, or Policy design behind a service connection:
  `/internal-azure`;
- Terraform code deployed by the pipeline: `/internal-terraform`.

## Workflow

1. Classify the request: pipeline authoring, pipeline review, project
   automation, deployment flow, or repository integration.
2. Discover repository conventions: existing pipelines, templates, agent
   pools and images, variables, environments, and validation commands. Reuse
   them before adding structure.
3. Design triggers, stages, jobs, dependencies, templates, parameters,
   variables, environments, and artifact flow on purpose.
4. Apply security controls: least-privilege service connections with workload
   identity federation, secrets in secret variables or Key Vault-linked
   variable groups, protected environments, and no secret output in logs.
5. When deployment is in scope, make promotion gates, health checks, and
   rollback explicit.
6. Run the focused validation available in the repository, such as YAML
   linting or pipeline validation, and name any check that stays unverified.

## References

- [`references/pipelines.md`](references/pipelines.md): load for the Azure
  DevOps authoring and review baseline.

## Output

Always return:

1. Design or review findings.
2. Material risk.
3. Next validation action, with the focused validation result when run.

Add security controls and rollback posture when the change touches secrets,
service connections, or deployment.
