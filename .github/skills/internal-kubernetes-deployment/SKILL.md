---
name: internal-kubernetes-deployment
description: Kubernetes deployment design, production manifests, rollout safety, probes, autoscaling, ingress, config and secret handling, and operational hardening. Use when authoring or reviewing Kubernetes deployment assets, workload topology, or production rollout guidance.
---

# Internal Kubernetes Deployment

Use this skill for production-grade Kubernetes deployment decisions.

## Baseline Workflow

1. Identify workload type: stateless, stateful, batch, or platform component.
2. Choose the right controller: Deployment, StatefulSet, Job, or CronJob.
3. Define service exposure and traffic flow.
4. Add health, scaling, and security settings.
5. Validate rollout and rollback behavior.

## Manifest Priorities

- Explicit resource requests and limits
- Readiness and liveness probes
- ConfigMaps for non-secret config
- Secrets for sensitive values
- Service and Ingress only when the traffic model needs them
- Pod disruption and rollout settings for availability

## Operational Rules

- Do not deploy bare Pods for managed workloads.
- Keep images versioned and reproducible.
- Prefer rolling updates with bounded surge and unavailability.
- Use HPA only when the workload exposes a sensible scaling signal.
- Make failure modes visible through probes and events.

## Security Rules

- Run as non-root when possible.
- Minimize capabilities.
- Use read-only filesystems when feasible.
- Keep secret usage narrow and explicit.
- Avoid over-broad service account permissions.

## Anti-Patterns

- Missing resource limits in shared clusters
- Using probes that only prove the process exists
- Stuffing secrets into ConfigMaps
- Exposing workloads publicly without clear ingress intent
- Treating a successful `kubectl apply` as proof of production readiness

## Output Expectations

When producing guidance, include:

- Recommended workload shape
- Required manifest primitives
- Rollout and recovery considerations
- Security and observability gaps
