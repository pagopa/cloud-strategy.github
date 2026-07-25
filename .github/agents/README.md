# Agents Catalog

This folder contains Copilot wrapper agents for repository-owned operations plus
repo-only sync workflows.

## Agent-Owned Core

- `internal-gateway-idea`: owns substantive idea definition,
  critical challenge, and retained planning before execution.
- `internal-gateway-review-generic`: owns generic defect-first review for non-code and
  mixed artifacts before fixes.
- `internal-gateway-review-code`: owns dedicated code-focused review for source, tests,
  scripts, build metadata, dependency metadata, and code diffs.
- `internal-gateway-critical-master`: owns pressure testing.
- `internal-gateway-simple-task`: owns concrete execution through one focused lane.

## Active Gateway Agents

| Agent | Use when |
| --- | --- |
| `internal-gateway-idea` | A vague idea or unresolved goal needs definition and retained planning. |
| `internal-gateway-review-generic` | A concrete non-code or mixed artifact needs defect-first review before fixes. |
| `internal-gateway-review-code` | A concrete code target needs dedicated code review before merge or follow-up action. |
| `internal-gateway-critical-master` | A proposal or plan needs pressure before action. |
| `internal-gateway-simple-task` | A concrete low-to-medium-risk task can finish through one focused lane. |
| `internal-gateway-execute-plans` | An approved retained plan under tmp/superpowers/plans/ is ready for execution. |
