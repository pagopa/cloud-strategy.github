# GCP Strategic Lens Playbook

When lens choice or option comparison needs deeper structure, load this reference.

## Common lens combinations

| Situation | Start with | Add when material |
| --- | --- | --- |
| Org or Shared VPC choice | organization structure, governance | FinOps, BC/DR |
| Identity or workload access choice | identity and access, governance | blast radius, compliance |
| Rollout planning across folders or projects | rollout and rollback, blast radius | operations, BC/DR |
| Cost-sensitive platform decision | FinOps, maintainability | operations, governance |
| Resilience-sensitive design | BC/DR, operations | FinOps, blast radius |

## Lens signals

- Cost impact changes the preferred option: use FinOps.
- Org, folder, project, or Shared VPC layout changes: use organization structure.
- IAM, workload identity, or Org Policy behavior changes: use governance.
- Monitoring, backup, inventory, or validation burden changes: use operations.
- Critical platform capability may be interrupted by failure: use BC/DR.

## Depth control

- Use Quick answer when one option clearly wins and the question is narrow.
- Use Decision note when at least two viable options remain.
- Use Deep analysis when the question is broad, high-risk, or explicitly detailed.

## Worked decision shapes

| Decision | Useful comparison |
| --- | --- |
| New platform needs enterprise segmentation | Compare a simpler folder and project model with a more segmented operating model, then name the smallest safe rollout unit. |
| Shared VPC ownership is undecided | Compare central network ownership with product-aligned host projects and state the operational burden tradeoff. |
| External delivery system needs GCP access | Compare federation with key-based alternatives and make trust and audit boundaries explicit. |
| Shared platform services may be centralized or duplicated | Compare central efficiency with environment isolation and operational overhead. |

## Decision note pattern

1. Decision statement: the Google Cloud choice being made.
2. Assumptions: current state, scale, compliance, and continuity constraints.
3. Viable options: two or three realistic Google Cloud paths.
4. Recommendation: the option that wins and why.
5. Tradeoffs and blast radius: benefits, costs, risks, and difficult-to-reverse effects.
6. Validation note: the current fact, proof, or behavior required before implementation.
