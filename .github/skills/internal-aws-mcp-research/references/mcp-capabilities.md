# AWS MCP Capabilities

Use this reference to choose the safest AWS MCP path for the question at hand.

## AWS Knowledge MCP

Best for:

- Current AWS documentation.
- Architecture and best-practice lookups.
- Regional availability checks.
- CloudFormation and CDK reference discovery.

Notable capabilities from the server documentation:

- `search_documentation`
- `read_documentation`
- `recommend`
- `list_regions`
- `get_regional_availability`

Operational notes:

- Remote HTTP server.
- Public internet access required.
- No AWS account or AWS authentication required.
- Subject to rate limits.

## AWS IAM MCP

Best for:

- Inspecting current IAM state in an AWS account.
- Listing users, roles, groups, and policies.
- Retrieving inline policy details.
- Simulating permissions before rollout.

Operational notes:

- Requires AWS credentials.
- Supports read-only mode and should default to it for analysis.
- Mutating operations exist, so treat them as explicit-change tools, not as
  default exploration tools.

## Recommended split of responsibilities

| Question type | Preferred server |
| --- | --- |
| "What does AWS currently recommend?" | AWS Knowledge MCP |
| "Which regions support this?" | AWS Knowledge MCP |
| "What does this role or user currently have?" | AWS IAM MCP |
| "Would this policy allow action X on resource Y?" | AWS IAM MCP with simulation |
| "How should we govern this across the org?" | Supply the relevant facts from whichever MCP source applies and label the unresolved decision as an inference |
