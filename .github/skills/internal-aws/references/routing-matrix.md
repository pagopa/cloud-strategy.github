# Internal AWS Routing Matrix

## Fallback-positive cases

- An underspecified multi-account control problem mixes organization structure,
  governance, and operations without identifying a primary deliverable. Use
  `internal-aws` to state the uncertainty, identify candidate owners, and
  select the minimum specialist set.
- An AWS platform question asks which problem-solving lane should own the work,
  but the request does not identify whether the primary concern is topology,
  governance, operations, Lambda, or current documentation. Use `internal-aws`
  to clarify the lane before dispatch.

## Direct-specialist negative cases

- OU layout or account placement → `internal-aws-organization-structure`.
- SCP or permission-boundary design → `internal-aws-governance`.
- Backup and restore validation → `internal-aws-operations`.
- Lambda retry behavior → `internal-aws-lambda`.
- Current AWS documentation lookup → `internal-aws-mcp-research`.

## Multi-domain primary-owner cases

- OU design with later SCP work → `internal-aws-organization-structure` first;
  hand the resulting governance implications to `internal-aws-governance`.
- SCP rollout evidence → `internal-aws-governance` first and
  `internal-aws-operations` second for evidence or validation.
- Lambda IAM detail → `internal-aws-lambda` when the requested deliverable is
  Lambda behavior, or `internal-aws-governance` when the requested deliverable
  is the IAM or trust boundary. Do not use the fallback when that deliverable
  is explicit.

## Review rule

Prefer a direct specialist whenever a reasonable reviewer can name one primary
owner from the request itself. The fallback is not a prerequisite for ordinary
AWS work and must never activate all AWS skills by default.
