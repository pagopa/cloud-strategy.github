# Azure Organization Structure Topology Map

Use this reference when turning a structural Azure question into the right control surface.

## Core boundary

- **Tenant and management-group hierarchy**: own enterprise segmentation, policy inheritance scope, and landing-zone grouping.
- **Subscriptions**: own workload, platform, environment, or residency placement boundaries.
- **Landing zones**: package platform capabilities, connectivity, and operating-model expectations.
- **Platform network topology**: decide hub-spoke, Virtual WAN, private connectivity, and regional placement at layout level.

## Default review checklist

1. Is this a structure choice, a governance control, or an operations concern?
2. Does the capability belong at tenant, management-group, subscription, or landing-zone level?
3. Is the change shaping layout, shaping permissions, or validating a rollout?
4. What is the smallest safe rollout unit: one management group, one subscription set, or one region set?
5. What must be validated before broad rollout?
6. What is the rollback path if connectivity, policy inheritance, or platform automation breaks?

## Common structural mappings

| Need | Use first | Notes |
| --- | --- | --- |
| Separate platform ownership from workload ownership | management-group plus subscription model | Keep landing-zone scope explicit |
| Standardize shared connectivity | platform-level topology choice | Keep routing and region placement visible |
| Segment environments or regulatory boundaries | subscription purpose plus hierarchy placement | Do not hide residency assumptions |
| Place shared services or platform controls | landing-zone placement | Keep governance logic separate |
| Roll out baseline structure safely | rollout unit definition | Validate one safe unit before widening |

## Important Azure-specific reminders

- Management groups shape policy and RBAC inheritance scope, but they do not replace subscription-level ownership.
- Landing-zone design should keep platform topology separate from workload-by-workload implementation detail.
- Regional placement is a structural concern when it changes connectivity, sovereignty, or continuity assumptions.
