---
name: internal-aws-mcp-research
description: Use when /internal-aws selects the AWS research lane to retrieve current official AWS documentation, regional availability, service behavior, IAM state, or policy-simulation evidence.
---

# Internal AWS MCP Research

Provide current AWS facts through AWS MCP servers when available, with official
AWS documentation as the fallback. Label every conclusion as documentation,
live observation, or inference.

## When to use

Use this lane for current AWS documentation, regional availability, service
behavior, IAM observations, and policy-simulation evidence.

## Source priority

1. AWS Knowledge MCP — current docs, latest guidance, regional availability.
2. AWS IAM MCP (read-only) — account-specific IAM inspection and policy simulation.
3. Official AWS documentation when MCP is unavailable or insufficient.

## Server identities

- AWS Knowledge MCP: `aws-knowledge-mcp-server`
- AWS IAM MCP: `awslabs.iam-mcp-server` or `iam-mcp-server`

Exact configured name can vary by client.

## Workflow

1. Classify the question.
   - Docs, best practices, service behavior, regional support → Knowledge MCP.
   - Real IAM state, principals, attached policies, permission testing → IAM MCP.
   - Mixed → Knowledge MCP first, IAM MCP for confirmation.
2. Detect available AWS MCP servers in the current environment.
3. Use the safest tool path first (Knowledge MCP for docs; IAM MCP read-only for inspection and `simulate_principal_policy`).
4. If AWS MCP is unavailable, use `references/official-source-map.md`.
5. Summarize with source type labeled: AWS docs / Knowledge MCP guidance / live IAM observation / inferred recommendation.

Load `references/mcp-capabilities.md` for capability splits and tool patterns
when selecting an AWS MCP server or tool.

## Safety rules

- Treat IAM MCP as read-only by default.
- Do not create, delete, attach, detach, or rotate IAM resources unless the user explicitly asks and blast radius is understood.
- Prefer `simulate_principal_policy` before proposing policy rollout.
- Distinguish documentation-backed statements from observations of a real AWS account.

## Output contract

- Research question and scope
- MCP availability used or missing
- Sources consulted
- What is confirmed by AWS docs or MCP
- What remains an architectural recommendation or inference
- Safe next steps

## Validation

- Source type (docs / live IAM / inference) is labeled for every claim.
- IAM MCP usage stayed read-only unless an explicit change was requested.
- Unresolved freshness gaps are stated beside the affected conclusion.
