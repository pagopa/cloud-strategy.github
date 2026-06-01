---
name: internal-yaml
description: Use when editing YAML or YML files that need formatting, schema awareness, or domain-owner routing.
---

# Internal YAML

## Referenced skills

Treat the referenced skills below as on-demand owners. Do not preload them for
every YAML edit; load them only when path, platform semantics, runtime, or
validation need proves a narrower schema-aware owner.

- `internal-github-actions`: GitHub Actions workflows when `.github/workflows/` or workflow behavior is the target.
- `internal-github-action-composite`: GitHub composite action metadata when `action.yml` or `action.yaml` is the target.
- `internal-kubernetes`: Kubernetes manifests and deployment routing when workload, service, rollout, or cluster semantics are the real problem.
- `internal-terraform`: Terraform-adjacent generated or configuration checks when HCL ownership dominates and YAML is incidental.
- `internal-azure-devops`: Azure DevOps pipeline YAML when pipeline behavior is the target.

## When to use

- `.yaml` or `.yml` edits where no narrower schema owner is already obvious.
- Reviews focused on indentation, stable keys, comments, anchors, and parser-safe YAML.
- Routing decisions for YAML files that may belong to a CI, Kubernetes, Azure DevOps, or other domain owner.

## When not to use

- GitHub Actions workflow semantics; use `internal-github-actions`.
- Composite action metadata; use `internal-github-action-composite`.
- Kubernetes workload, service, probe, rollout, or policy semantics; use `internal-kubernetes`.
- Azure DevOps pipeline behavior; use `internal-azure-devops`.

## Baseline

- Use 2-space indentation and avoid tabs.
- Keep key names stable and readable.
- Quote values only when needed for correctness.
- Keep anchors and aliases simple.
- Keep comments concise and in English.
- Validate with the schema-aware owner when YAML tags or platform semantics make generic YAML parsing unsafe.

## Validation

- Run the nearest generic YAML parser only when the file is safe for generic YAML parsing.
- Use schema-aware validation for GitHub Actions, Kubernetes, CloudFormation-style tags, or platform-specific YAML.
- Reuse the repository validator when one already covers the touched YAML family.
