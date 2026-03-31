# zOptimizer Final

> Live cleanup plan only. Completed analysis and historical carry-over were intentionally removed.

## Current Snapshot

- `85` skills on disk: `26` `internal-*`, `30` `obra-*`, `29` external-prefixed.
- `20` agents on disk.
- Working hierarchy:
  - `obra-*` = strategic layer
  - `internal-*` = tactical owner
  - external-prefixed skills = merge source or support-only specialist
- `5` imported agents still use deprecated `tools:` frontmatter:
  - `awesome-copilot-azure-principal-architect.agent.md`
  - `awesome-copilot-critical-thinking.agent.md`
  - `awesome-copilot-devils-advocate.agent.md`
  - `awesome-copilot-devops-expert.agent.md`
  - `awesome-copilot-plan.agent.md`

## Merge Then Remove

| External Skill | Internal Owner |
|---|---|
| `awesome-copilot-agent-governance` | `internal-agent-development`, `internal-sync-control-center` |
| `awesome-copilot-create-github-pull-request-from-specification` | `internal-pr-editor` |
| `awesome-copilot-instructions-blueprint-generator` | `internal-ai-resource-creator`, `internal-agents-md-bridge` |
| `awesome-copilot-postgresql-optimization` | `internal-performance-optimization` |
| `awesome-copilot-sql-optimization` | `internal-performance-optimization` |
| `terraform-terraform-style-guide` | `internal-terraform` |

## Keep As Support-Only

- `antigravity-api-design-principles`
- `antigravity-aws-cost-optimizer`
- `antigravity-aws-serverless`
- `antigravity-cloudformation-best-practices`
- `antigravity-domain-driven-design`
- `antigravity-golang-pro`
- `antigravity-grafana-dashboards`
- `antigravity-kubernetes-architect`
- `antigravity-network-engineer`
- `awesome-copilot-agentic-eval`
- `awesome-copilot-azure-devops-cli`
- `awesome-copilot-azure-pricing`
- `awesome-copilot-azure-resource-health-diagnose`
- `awesome-copilot-azure-role-selector`
- `awesome-copilot-cloud-design-patterns`
- `awesome-copilot-codeql`
- `awesome-copilot-dependabot`
- `awesome-copilot-secret-scanning`
- `openai-gh-address-comments`
- `openai-gh-fix-ci`
- `openai-skill-creator`
- `terraform-terraform-search-import`
- `terraform-terraform-test`

## Execution Order

1. Merge the six broad externals into the listed internal owners.
2. Delete those six external skills after the internal owners absorb the needed content.
3. Keep the listed specialists as support-only and out of broad default routing.
4. Trim agent routing after the catalog is smaller.
5. Resolve the five imported agents with deprecated `tools:` frontmatter as a second-wave cleanup.
