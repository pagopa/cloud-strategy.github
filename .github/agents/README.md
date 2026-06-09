# Agents Catalog

This folder contains Copilot wrapper agents for repository-owned operations plus
repo-only sync workflows.

## Skill-First Core

- `internal-gateway-idea-brainstorming`: owns substantive idea definition,
  critical challenge, and retained planning before execution.
- `internal-gateway-review`: owns defect-first review, findings consolidation,
  and remediation planning.
- `internal-gateway-critical-master`: owns pressure testing.
- `internal-gateway-simple-task`: owns concrete execution and approved compact
  retained-plan consumption.

## Active Gateway Wrappers

| Wrapper | Core skill | Use when |
| --- | --- | --- |
| `internal-gateway-idea-brainstorming` | `internal-gateway-idea-brainstorming` | A vague idea or unresolved goal needs definition and retained planning. |
| `internal-gateway-review` | `internal-gateway-review` | A concrete artifact needs defect-first review and maybe remediation planning. |
| `internal-gateway-critical-master` | `internal-gateway-critical-master` | A proposal or plan needs pressure before action. |
| `internal-gateway-simple-task` | `internal-gateway-simple-task` | A concrete low-to-medium-risk task can finish through one focused lane. |

Approved `extended` retained plans route directly to `internal-executing-plans`.
