# Internal AWS Routing Matrix

## Single-owner cases

- OU or account layout → `/internal-aws-organization-structure`.
- SCP, permission boundary, or trust review → `/internal-aws-governance`.
- Backup and restore proof → `/internal-aws-operations`.
- Lambda retry or event-source behavior → `/internal-aws-lambda`.
- Current AWS service documentation or regional availability → `/internal-aws-mcp-research`.
- AWS option comparison or tradeoff decision → `/internal-aws-strategic`.
- AWS spend or savings analysis → `/antigravity-aws-cost-optimizer`.

## Primary-owner disambiguation

- Lambda IAM review → `/internal-aws-governance` when the requested result is
  trust or permissions; `/internal-aws-lambda` when the requested result is
  handler or runtime behavior.
- OU plus SCP wording → `/internal-aws-organization-structure` when placement
  is the result; `/internal-aws-governance` when access controls are the result.
- Research plus strategy wording → `/internal-aws-mcp-research` when only facts
  are requested; `/internal-aws-strategic` when an option or tradeoff decision
  is requested.
- Governance plus operations wording → `/internal-aws-governance` when control
  design is the result; `/internal-aws-operations` when proof is the result.

## Permitted multi-deliverable sequences

- Current fact, then a separate option decision →
  `/internal-aws-mcp-research`, then `/internal-aws-strategic`.
- Structural design, then explicit rollout proof →
  `/internal-aws-organization-structure`, then `/internal-aws-operations`.
- Governance design, then explicit control evidence →
  `/internal-aws-governance`, then `/internal-aws-operations`.

## Near-miss distinctions

- A Python lambda expression is not an AWS Lambda request.
- Azure management-group governance is not an AWS request.
- Cost is owned by `/antigravity-aws-cost-optimizer` only when spend analysis
  or savings opportunity is the primary result.

## Review rule

Keep ambiguity in the router when the requested result is missing. Strategic
work requires a real option or tradeoff decision. Invoke only one lane for one
deliverable, and add a second lane only for a second explicit deliverable.
