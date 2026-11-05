---
name: internal-kubernetes
description: Use when the task involves Kubernetes but the winning lane is not obvious yet, or when the work spans platform architecture, manifest authoring, rollout safety, and production readiness across the repository-owned and imported Kubernetes skills.
---

# Internal Kubernetes

Choose the right Kubernetes lane before drafting guidance or editing delivery
assets. This skill orchestrates the Kubernetes family; it does not replace its
owners or route the whole catalog.

## When to use

- The task involves Kubernetes but the winning lane between platform
  architecture, workload delivery, and rollout safety is not obvious yet.
- A request mixes architecture, manifest authoring, and production-readiness
  concerns across the Kubernetes skill family.
- You need to decide whether `antigravity-kubernetes-architect` or
  `internal-kubernetes-deployment` should own the next step.

## When not to use

- The user or an upstream operational choice already selected
  `internal-kubernetes-deployment` or `antigravity-kubernetes-architect`
  directly; this skill adds no value and stays out of the turn.

## Lanes

Treat these skills as on-demand owners. Do not preload the whole family; load
one only when the request proves which problem is real.

| Lane | Owner | Trigger |
| --- | --- | --- |
| YAML syntax | `/internal-yaml` | YAML formatting or parser safety is the blocker. |
| Workload delivery | `/internal-kubernetes-deployment` | Workload manifests, service exposure, probes, autoscaling, rollout strategy, and production hardening. |
| Platform architecture | `/antigravity-kubernetes-architect` | Platform architecture, GitOps operating model, service mesh, and multi-cluster strategy. |

## Workflow

1. **Classify the pressure:** platform strategy, workload delivery authoring,
   or rollout and recovery.
2. **Pick the winning owner** from [Lanes](#lanes). Use `/internal-yaml` only
   for formatting or parser concerns; Kubernetes semantics belong to the
   deployment or architecture owner.
3. **Return one clear next lane:** which skill wins, why it wins, and what
   validation or artifact should follow.

## Guardrails

- Escalate to GitOps, service mesh, or multi-cluster design only when the user
  is actually changing platform behavior.
- A manifest edit is not platform architecture work just because the workload
  runs on Kubernetes.

## Output requirements

- selected Kubernetes lane
- winning skill and why
- key assumptions or missing inputs
- next artifact or validation step

## References

- [`references/routing-matrix.md`](references/routing-matrix.md): load when
  the request mixes platform, manifest, and rollout concerns or when the
  boundary between strategy and delivery is unclear.
