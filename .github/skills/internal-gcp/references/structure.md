# GCP Structure

Placement, billing, connectivity, residency, change units, and decision
lenses for Google Cloud. Rows marked with a source were verified on
2026-09-27; recheck them when they drive a decision.

## Placement patterns

| Need | Pattern | Acceptance criteria |
| --- | --- | --- |
| Separate platform ownership from workload ownership | Platform folder plus workload folders with explicit project purpose | Operating boundaries, billing ownership, and support paths are visible |
| Segment environments or regulatory boundaries | Environment or regulated folders with project families under them | Residency, approval, and rollout assumptions are stated |
| Keep guardrails inheritable | Put shared controls at the folder that owns the boundary, not per project | Inheritance and overrides are visible from the folder |
| Standardize shared connectivity | Shared VPC host project with named service projects | Network ownership and workload ownership are both explicit |
| Roll out baseline structure safely | One named folder, project set, host project, or region set | The first unit has observable validation and a widening condition |

Use the Google Cloud enterprise foundations blueprint as the reference
layout, not as a mandatory template.

## Connectivity

| Need | Pattern | Does not guarantee |
| --- | --- | --- |
| One operating boundary serves many workloads | Central Shared VPC host project with named service projects | Isolation between service projects; use firewall policy and IAM for that |
| Network administration needs regulatory or autonomous isolation | Dedicated host project per boundary | Connectivity between boundaries; add it explicitly |
| Many VPC networks, or hybrid sites, need hub-and-spoke routing | Network Connectivity Center hub; Shared VPC networks can join as VPC spokes | Replacement of Shared VPC; NCC composes with it ([NCC overview](https://docs.cloud.google.com/network-connectivity/docs/network-connectivity-center/concepts/overview)) |
| Service projects must attach only to approved hosts | `constraints/compute.restrictSharedVpcHostProjects` at the owning folder | Subnet-level restriction; use `compute.restrictSharedVpcSubnetworks` |

Heuristics:

- Start a broad change with one folder and one low-risk service-project set so
  inheritance and blast radius stay visible.
- Separate network and shared-service ownership when the host project would
  otherwise become the home for unrelated capabilities.

## Billing ownership

- Central platform funding may use a billing account separate from workload
  project ownership, with explicit chargeback or showback.
- Business-unit spend ownership can coexist with a centrally operated Shared
  VPC when dependency and support paths are documented.
- Regulated workloads may use a dedicated billing boundary when financial
  reporting follows the residency or approval boundary.
- Use billing export to BigQuery as the reporting source for cost evidence.
- Name billing ownership and platform ownership separately when they differ.

## Residency

| Need | Control | Does not guarantee |
| --- | --- | --- |
| Restrict where location-based resources are created | `constraints/gcp.resourceLocations` at the regulated folder | Data location commitments; the constraint page states it does not describe them ([constraints](https://docs.cloud.google.com/organization-policy/reference/org-policy-constraints)) |
| Regulated control package (for example sovereignty regimes) | Assured Workloads folder; it configures its own constraints | Coverage of unsupported services; do not modify the constraints it manages |

## Structural change units

| Change | Initial unit | Widening evidence |
| --- | --- | --- |
| New folder branch | One low-risk project family | Inheritance, automation, and rollback behavior are confirmed |
| Shared VPC introduction | One host project with one low-risk service-project set | Connectivity, logging, and ownership paths are proven |
| Billing ownership realignment | One product or environment slice | Chargeback, approvals, and automation remain correct |
| Region or residency split | One workload set with explicit fallback | Connectivity and sovereignty assumptions are validated |

## Decision lenses

| Situation | Start with | Add when material |
| --- | --- | --- |
| Org or Shared VPC choice | structure, governance | cost, continuity |
| Identity or workload access choice | identity, governance | blast radius, compliance |
| Rollout across folders or projects | rollout and rollback, blast radius | operations, continuity |
| Cost-sensitive platform decision | cost, maintainability | operations, governance |
| Resilience-sensitive design | continuity, operations | cost, blast radius |

Lens signals:

- Cost changes the preferred option: add cost.
- Monitoring, backup, inventory, or validation burden changes: add operations.
- A critical capability may be interrupted by failure: add continuity.

Worked decision shapes:

| Decision | Useful comparison |
| --- | --- |
| New platform needs segmentation | A simpler folder model versus a more segmented model, then the smallest safe rollout unit |
| Shared VPC ownership is undecided | Central network ownership versus product-aligned host projects, with the operational burden |
| External delivery system needs access | Federation versus key-based alternatives, with trust and audit boundaries |
| Shared services may be central or duplicated | Central efficiency versus environment isolation and overhead |
