# Azure Organization Structure Topology Map

Use this reference for structural mappings, placement heuristics, and safe
rollout examples.

## Structural mappings

| Need | Placement surface | Structural rationale |
|---|---|---|
| Enterprise segmentation and inheritance scope | Tenant and management-group hierarchy | Groups establish stable policy and RBAC inheritance boundaries. |
| Workload, platform, environment, or residency placement | Subscription model | Subscription purpose makes ownership, billing, and operational scope visible. |
| Packaged platform capabilities and connectivity | Landing zone | Landing zones express shared services and operating-model expectations. |
| Shared connectivity and regional layout | Platform network topology | Hub-spoke, Virtual WAN, private connectivity, and region placement shape platform boundaries. |

## Placement heuristics

| Question | Prefer | Rationale |
|---|---|---|
| Does the capability provide shared connectivity or central platform plumbing? | Platform landing zone or dedicated platform subscription | Shared ownership remains stable and visible. |
| Does the capability exist for one workload or product boundary? | Workload landing zone or workload subscription | Application-specific ownership stays close to the workload. |
| Does residency or regulated access change the operating model? | Dedicated hierarchy or landing-zone segment | Connectivity, sovereignty, and approval assumptions remain explicit. |
| Does the change affect many subscriptions? | Management-group placement with staged rollout | Inheritance and blast radius are observable before expansion. |

## Safe rollout examples

| Structural change | Start with | Widen after |
|---|---|---|
| New management-group branch | One low-risk subscription family | Inheritance, policy scope, and operational ownership are confirmed. |
| Landing-zone baseline update | One landing zone or environment slice | Connectivity, automation, and rollback behavior are observed. |
| Platform subscription introduction | One shared capability with named consumers | Ownership, dependencies, and routing impact are validated. |
| Region or residency split | One workload set with explicit fallback | Connectivity, sovereignty, and continuity assumptions are proven. |
