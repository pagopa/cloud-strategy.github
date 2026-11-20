# AWS Organization Structure

Load this reference for account and OU layout, delegated administrators,
StackSets, shared services, the ownership split, or platform network
placement. It covers where capabilities live; guardrail logic stays in
[`governance.md`](governance.md).

## Account roles

- **Management account:** AWS Organizations control, billing and payer
  duties, trusted access activation, and only the actions AWS requires there.
- **Delegated administrator accounts:** day-to-day operation of integrated
  AWS services where delegation is supported.
- **Member accounts:** workload execution, service ownership, and most
  resource-level IAM decisions.

## AWS-specific reminders

- SCPs do not affect users or roles in the management account.
- RCPs do not affect resources in the management account.
- Delegated administrator accounts are member accounts, so SCPs and RCPs
  apply to them.
- StackSets with service-managed permissions do not deploy stacks into the
  management account.
- Global IAM or S3 naming collisions matter more in multi-region StackSets
  than in single-account templates.

## Ownership split

State financial ownership (payer, budgets, chargeback) separately from
operational ownership (who runs the platform capability and who owns
workload accounts). When they drift together, finance and platform controls
become hard to change independently.

## Starter account and OU patterns

| Pattern | When it fits | Watch for |
| --- | --- | --- |
| Minimal foundation: management, log archive, security tooling, shared services, workload OUs | Early multi-account platforms that need clear separation without a deep OU tree | Do not overload shared services with workload execution or exception access |
| Environment-oriented workload OUs: `prod`, `nonprod`, plus platform accounts | Teams share a control posture and rollout cadence by environment | Keep deployment-path differences out of OU names when the real split is risk or residency |
| Business-unit OUs with central platform accounts | Ownership boundaries come first and technical standardization second | Keep a clear delegated administrator model for central capabilities |
| Regulated-segment OU beside general workloads | A subset needs stronger residency, logging, or approval controls | Justify the segment by requirements, not by vague "special" status |

## Delegated administrator placement

| Question | Prefer | Reason |
| --- | --- | --- |
| Does AWS support delegated administration for this service? | A delegated administrator account | Reduces management-account use and day-to-day blast radius |
| Does the service run as a platform capability across many accounts? | A dedicated platform or security account | Keeps service ownership separate from workload accounts |
| Does the action need billing or organization control? | The management account, only when AWS requires it | Avoids making it the default operator surface |
| Is the service coupled to sensitive data or incident response? | A security or log account with named ownership | Keeps investigation and evidence flows apart from applications |

## Shared services and network placement

- Name which capability lives centrally and which teams own execution
  accounts. Central accounts without named ownership become dumping grounds.
- Place shared network capabilities (for example a network hub, central
  egress, or DNS) in a dedicated platform account and state the consumer
  accounts and regions.
- For multi-region layout, state the regional scope, the global resources
  involved, and the rollback boundary.
- Detailed VPC, Transit Gateway, and IPAM design is out of scope here; this
  reference covers placement only.

## Safe rollout units

| Structural change | Start with | Widen after |
| --- | --- | --- |
| New delegated administrator activation | One non-critical OU or one service-owned account set | Service behavior, logging, and guardrails are confirmed |
| OU realignment for workloads | One workload family with a documented rollback path | SCP and RCP impact, automation paths, and billing visibility are validated |
| StackSets baseline rollout | One account in one region or one low-risk OU | Global-resource effects and failure handling are observed |
| Shared-services account introduction | One platform capability with named consumers | Ownership, network reachability, and operational evidence are proven |

## Sources

- AWS Organizations concepts:
  <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html>
- Delegated administrator for AWS services:
  <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_delegated_admin.html>
- StackSets with service-managed permissions:
  <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-associate-stackset-with-org.html>
- StackSets best practices:
  <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-bestpractices.html>
