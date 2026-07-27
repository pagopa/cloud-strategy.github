---
name: internal-gcp-organization-structure
description: Use when /internal-gcp selects organization structure for Google Cloud org or folder layout, billing-account ownership, project segmentation, Shared VPC topology, environment boundaries, or regional placement.
---

# Internal GCP Organization Structure

## Purpose

Shape Google Cloud organization, folder, billing-account, project, Shared VPC, environment, and regional placement around clear ownership and rollout boundaries.

## When to use

Use this skill when the requested deliverable is a Google Cloud placement or topology decision.

## Process

1. Establish the platform requirements, organizational owners, billing owners, workload boundaries, environment model, and regional or residency constraints.
2. Compare viable org, folder, billing-account, project, and Shared VPC placement models against ownership, isolation, connectivity, and rollout needs.
3. Select the placement model and state where each capability lives, including the Shared VPC host and service-project relationship.
4. Name the smallest structural change unit, such as one folder, project set, host project, or region set.
5. Surface region, residency, connectivity, continuity, and ownership implications that shape the recommendation.

Load `references/topology-map.md` only when placement alternatives need deeper comparison.

## Output

- structural objective and requirements
- candidate placement models and comparison
- recommended org, folder, billing, project, and Shared VPC placement
- explicit billing and platform ownership
- smallest structural change unit
- regional, residency, connectivity, and continuity assumptions

## Completion

- The placement model is explicit at each relevant control surface.
- Billing ownership and platform ownership are named separately when they differ.
- The smallest structural change unit is named and matches the proposed change.
- Region and residency implications are stated when they shape placement.
