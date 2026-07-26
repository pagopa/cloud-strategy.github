---
name: internal-yaml
description: Use when editing or reviewing YAML or YML syntax, encoding, parser safety, or format-owner routing.
---

# Internal YAML

## When to use

- YAML or YML edits where generic format ownership is the active concern.
- Reviews focused on syntax, indentation, duplicate mapping keys, encoding,
  comments, anchors, aliases, and parser-safe structure.
- Routing a file to a narrower owner when platform or schema semantics are the
  real concern.

## When not to use

- GitHub Actions workflow semantics; use `/internal-github-actions`.
- Composite action metadata; use `/internal-github-action-composite`.
- Kubernetes workload, service, rollout, or policy semantics; use
  `/internal-kubernetes`.
- Azure DevOps pipeline behavior; use `/internal-azure-devops`.
- CloudFormation template semantics; use
  `/antigravity-cloudformation-best-practices`.

## Baseline

- Use 2-space indentation and never use tabs for indentation.
- Preserve encoding, comments, anchors, aliases, and key spelling unless the
  requested change requires otherwise.
- Treat duplicate mapping keys as findings, including duplicate keys hidden by
  merge behavior when the checker supports that parser rule.
- Keep generic YAML checks separate from platform schema and domain semantics.

## Validation

Run the bundle-owned checker with explicit files:

```bash
.github/skills/internal-yaml/scripts/check.sh FILE [FILE ...]
```

The checker returns `0` when checks passed within supported scope, `1` for
format findings, and `2` for usage, dependency, file, or internal failures.
It requires `yamllint` 1.38.0 and does not install dependencies. Supported
checks are parser-backed YAML syntax and duplicate-key detection. Schema,
tag, platform, and domain-content semantics are unsupported; route those
questions to the relevant owner.
