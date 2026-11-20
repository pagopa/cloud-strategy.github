# Azure Structure

Use this reference for tenant, management-group, subscription, landing-zone,
residency, and platform-topology placement.

## Structure patterns

- Use management groups for enterprise segmentation and inheritance scope.
- Use subscriptions for workload, platform, environment, or residency
  boundaries with explicit purpose and ownership.
- Use landing zones to package platform capabilities, connectivity, and
  operating-model expectations.
- Keep hub-spoke, Virtual WAN, private connectivity, and regional placement
  visible when they shape the platform topology.
- Separate platform subscriptions from workload subscriptions when shared
  services need stable ownership.

## Structural mappings

| Need | Placement surface | Structural rationale |
| --- | --- | --- |
| Enterprise segmentation and inheritance scope | Tenant and management-group hierarchy | Groups establish stable policy and RBAC inheritance boundaries. |
| Workload, platform, environment, or residency placement | Subscription model | Subscription purpose makes ownership, billing, and operational scope visible. |
| Packaged platform capabilities and connectivity | Landing zone | Landing zones express shared services and operating-model expectations. |
| Shared connectivity and regional layout | Platform network topology | Hub-spoke, Virtual WAN, private connectivity, and region placement shape platform boundaries. |

## Placement heuristics

| Question | Prefer | Rationale |
| --- | --- | --- |
| Does the capability provide shared connectivity or central platform plumbing? | Platform landing zone or dedicated platform subscription | Shared ownership remains stable and visible. |
| Does the capability exist for one workload or product boundary? | Workload landing zone or workload subscription | Application-specific ownership stays close to the workload. |
| Does residency or regulated access change the operating model? | Dedicated hierarchy or landing-zone segment | Connectivity, sovereignty, and approval assumptions remain explicit. |
| Does the change affect many subscriptions? | Management-group placement with staged rollout | Inheritance and blast radius are observable before expansion. |

## Rollout

Stage structural changes with the staged-rollout table in
[`operations.md`](operations.md#staged-rollout). Validate inheritance,
connectivity, automation, ownership, and continuity assumptions before
widening.
