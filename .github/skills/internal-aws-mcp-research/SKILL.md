---
name: internal-aws-mcp-research
description: Use when the task needs current AWS documentation or safe IAM inspection for Organizations, SCPs, IAM policies, delegated administrators, regional availability, or StackSets, and the assistant should prefer AWS Knowledge MCP and AWS IAM MCP when available.
disable-model-invocation: true
---

# Internal AWS MCP Research

Standardizes an AWS research workflow that prefers AWS MCP servers when available and falls back to official AWS documentation. Designed for principal-level platform governance questions, not only application coding.

If the request falls outside this lane, or routing is unclear under material routing uncertainty, route back to `internal-aws`.

## When to use

- Current AWS documentation, regional availability, or official guidance that may have changed.
- Safe IAM inspection or policy simulation for Organizations, SCPs, IAM policies, roles, or delegated administrators.
- AWS Knowledge MCP or AWS IAM MCP should be preferred when available, with an AWS-doc fallback.

## Source priority

1. AWS Knowledge MCP — current docs, latest guidance, regional availability.
2. AWS IAM MCP (read-only) — account-specific IAM inspection and policy simulation.
3. Official AWS documentation when MCP is unavailable or insufficient.

Do not assume both MCP servers are configured in the current client.

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

## Knowledge MCP tool patterns

- `search_documentation` — find relevant pages
- `read_documentation` — pull exact page into markdown
- `recommend` — expand from one page to adjacent guidance
- `list_regions`, `get_regional_availability` — region-sensitive design

## IAM MCP tool patterns (read-only default)

- `list_users`, `get_user`, `list_roles`, `list_groups`, `get_group`
- `list_policies`, `get_user_policy`, `get_role_policy`, `list_user_policies`, `list_role_policies`
- `simulate_principal_policy` — test policy effects before proposing rollout

## Safety rules

- Treat IAM MCP as read-only by default.
- Do not create, delete, attach, detach, or rotate IAM resources unless the user explicitly asks and blast radius is understood.
- Prefer `simulate_principal_policy` before proposing policy rollout.
- Distinguish documentation-backed statements from observations of a real AWS account.

Load `references/mcp-capabilities.md` for capability splits across the two MCP servers.

## Output expectations

- Research question and scope
- MCP availability used or missing
- Sources consulted
- What is confirmed by AWS docs or MCP
- What remains an architectural recommendation or inference
- Safe next steps

## Validation

- Source type (docs / live IAM / inference) is labeled for every claim.
- IAM MCP usage stayed read-only unless an explicit change was requested.
- Implications beyond the research lane are reported as labeled findings, not acted on.
