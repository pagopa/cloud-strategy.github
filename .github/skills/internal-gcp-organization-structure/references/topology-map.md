# GCP Organization Structure Topology Map

When placement alternatives remain ambiguous, load this reference for deeper comparison.

## Placement patterns

| Need | Placement pattern | Acceptance criteria |
| --- | --- | --- |
| Separate platform ownership from workload ownership | Platform folder plus workload folders with explicit project purpose | Operating boundaries, billing ownership, and support paths are visible |
| Standardize shared connectivity | Shared VPC host project with named service projects | Network ownership and workload ownership are both explicit |
| Segment environments or regulatory boundaries | Environment-specific project families within justified hierarchy branches | Residency, approval, and rollout assumptions are stated |
| Split financial ownership from platform execution | Billing-account model aligned to chargeback or showback responsibility | Financial responsibility and platform responsibility are traceable |
| Roll out baseline structure safely | A named folder, project set, host project, or region set | The first unit has observable validation and a widening condition |

## Shared VPC heuristics

- Use a central host project with named service projects when one operating boundary serves many workloads.
- Use a dedicated host project or separate topology segment when network administration requires regulatory or autonomous isolation.
- Start a broad-impact change with one folder and one low-risk service-project set so inheritance and blast radius remain visible.
- Separate network and shared-service ownership when the host project would otherwise become the default home for unrelated capabilities.

## Billing ownership patterns

- Central platform funding may use billing ownership separate from workload project ownership, with explicit chargeback or showback assumptions.
- Business-unit spend ownership may coexist with a centrally operated Shared VPC service when dependency and support paths are documented.
- Regulated workloads may use a dedicated billing boundary or reporting model when financial reporting follows the residency or approval boundary.

## Structural change units

| Structural change | Initial unit | Widening evidence |
| --- | --- | --- |
| New folder branch | One low-risk project family | Inheritance, automation, and rollback behavior are confirmed |
| Shared VPC introduction | One host project with one low-risk service-project set | Connectivity, logging, and ownership paths are proven |
| Billing ownership realignment | One product or environment slice | Chargeback, approvals, and automation remain correct |
| Region or residency split | One workload set with explicit fallback | Connectivity and sovereignty assumptions are validated |
