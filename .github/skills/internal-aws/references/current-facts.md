# AWS Current Facts

Load this reference when a current fact, live IAM observation, or policy
simulation controls the answer. Label every conclusion as AWS documentation,
live observation, or inference.

## Source priority

1. **AWS Knowledge MCP**, when configured: current documentation, regional
   availability, and service behavior. No AWS account or credentials are
   needed.
2. **AWS IAM MCP**, when configured, in read-only mode: live IAM state and
   policy simulation for one account.
3. **Official AWS documentation**, when no MCP server is available or the
   MCP result is insufficient.

Server names vary by client. Common names are `aws-knowledge-mcp-server` and
`awslabs.iam-mcp-server` or `iam-mcp-server`.

## AWS Knowledge MCP tools

| Tool | Use for |
| --- | --- |
| `search_documentation` | Find current documentation chunks; pick one topic such as `general`, `reference_documentation`, `current_awareness`, or `troubleshooting` |
| `read_documentation` | Read a full page when search chunks lack the needed detail |
| `list_regions` | List AWS Regions |
| `get_regional_availability` | Check service, API, or CloudFormation resource availability in a Region |
| `retrieve_skill` | Load an AWS-published agent skill found with `search_documentation` topic `agent_skills` |

Optional enrichment: AWS publishes agent skills such as `aws-iam` for IAM
edge cases. Discover the exact `skill_name` with `search_documentation`
first; do not guess it. This skill stays complete without them.

## AWS IAM MCP rules

- Keep it read-only by default. Do not create, delete, attach, detach, or
  rotate IAM resources unless the user explicitly asks and the blast radius
  is understood.
- Use `simulate_principal_policy` before proposing an identity-policy change.
  Simulation covers identity policies and SCPs where supported; it does not
  prove RCP or declarative policy effects.
- Report live observations with the account and time of observation.

## Question routing

| Question | Source |
| --- | --- |
| What does AWS currently recommend? | Knowledge MCP or official docs |
| Which Regions support this service or resource? | `get_regional_availability` or official docs |
| What does this role or user currently have? | IAM MCP, read-only |
| Would this policy allow action X on resource Y? | IAM MCP simulation, with the RCP and declarative limits stated |
| How should we govern this across the org? | Facts from the sources above; the recommendation is labeled as inference |

## Official sources

- AWS Knowledge MCP server:
  <https://github.com/awslabs/mcp/tree/main/src/aws-knowledge-mcp-server>
- AWS IAM MCP server: <https://github.com/awslabs/mcp/tree/main/src/iam-mcp-server>
- Organizations policies:
  <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html>
- SCP examples:
  <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_examples.html>
- RCPs: <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html>
- Declarative policies:
  <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_declarative_policies.html>
- IAM policy evaluation logic:
  <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html>
- IAM policy simulator limits:
  <https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_testing-policies.html>
- AWS Regional services: <https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/>
