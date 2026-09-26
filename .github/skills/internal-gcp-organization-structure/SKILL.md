---
name: internal-gcp-organization-structure
description: Use when /internal-gcp selects organization structure for Google Cloud org or folder layout, billing-account ownership, project segmentation, Shared VPC topology, environment boundaries, or regional placement.
---

# Internal GCP Organization Structure

Use this workflow to shape Google Cloud organization, folder, billing-account,
project, Shared VPC, environment, and regional placement around clear
ownership and rollout boundaries.

## When to use

Use when `/internal-gcp` selects the organization-structure lane: a Google
Cloud placement or topology decision.

## Workflow

1. Establish the platform requirements, organizational owners, billing
   owners, workload boundaries, environment model, and regional or residency
   constraints.
2. Compare viable org, folder, billing-account, project, and Shared VPC
   placement models against ownership, isolation, connectivity, and rollout
   needs.
3. Select the placement model and state where each capability lives,
   including the Shared VPC host and service-project relationship.
4. Name the smallest structural change unit, such as one folder, project set,
   host project, or region set.
5. Surface region, residency, connectivity, continuity, and ownership
   implications that shape the recommendation.

## Output

Return these sections:

- Structural objective and requirements.
- Candidate placement models and comparison.
- Recommended org, folder, billing, project, and Shared VPC placement.
- Explicit billing and platform ownership.
- Smallest structural change unit.
- Regional, residency, connectivity, and continuity assumptions.

## References

- [`references/topology-map.md`](references/topology-map.md): load only when
  placement alternatives need deeper comparison.

## Completion criteria

- The placement model is explicit at each relevant control surface.
- Billing ownership and platform ownership are named separately when they
  differ.
- The smallest structural change unit is named and matches the proposed
  change.
- Region and residency implications are stated when they shape placement.
