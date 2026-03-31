---
name: internal-kubernetes-deployment
description: Kubernetes deployment design, production manifests, rollout safety, probes, autoscaling, ingress, Helm packaging, config and secret handling, network policy, observability hooks, and operational hardening. Use when authoring or reviewing Kubernetes deployment assets, workload topology, or production rollout guidance.
---

# Internal Kubernetes Deployment

Use this skill for production-grade Kubernetes deployment decisions.

## Baseline Workflow

1. Identify workload type: stateless, stateful, batch, or platform component.
2. Choose the right controller: Deployment, StatefulSet, Job, or CronJob.
3. Define service exposure and traffic flow.
4. Choose the packaging and delivery mode.
5. Add health, scaling, security, and policy settings.
6. Validate rollout and rollback behavior.

## Manifest Priorities

- Explicit resource requests and limits
- Readiness and liveness probes
- ConfigMaps for non-secret config
- Secrets for sensitive values
- Service and Ingress only when the traffic model needs them
- NetworkPolicy when east-west or egress boundaries matter
- Pod disruption and rollout settings for availability

## Delivery Extensions

- Prefer raw manifests by default; add Helm only when repeated installs, versioned packaging, or environment overlays justify chart maintenance.
- Treat service mesh integration as conditional: configure traffic policy, mTLS, and mesh telemetry only when the cluster already runs a mesh or the platform standard requires it.
- Prefer controller-driven delivery such as GitOps only when the team already operates that model and the rollout ownership is explicit.

## Operational Rules

- Do not deploy bare Pods for managed workloads.
- Keep images versioned and reproducible.
- Prefer rolling updates with bounded surge and unavailability.
- Use HPA only when the workload exposes a sensible scaling signal.
- Make failure modes visible through probes and events.
- Verify workload, Service, Ingress, and policy state together; a healthy Pod alone does not prove a complete deployment.
- Add dashboards, alerts, and scrape annotations only when they match the platform's observability standard.

## Security Rules

- Run as non-root when possible.
- Minimize capabilities.
- Use read-only filesystems when feasible.
- Keep secret usage narrow and explicit.
- Avoid over-broad service account permissions.
- Use NetworkPolicy and namespace boundaries to narrow runtime traffic.

## Anti-Patterns

- Missing resource limits in shared clusters
- Using probes that only prove the process exists
- Introducing Helm, GitOps, or service mesh just to look "enterprise"
- Stuffing secrets into ConfigMaps
- Exposing workloads publicly without clear ingress intent
- Treating a successful `kubectl apply` as proof of production readiness

## Output Expectations

When producing guidance, include:

- Recommended workload shape
- Required manifest primitives
- Packaging and delivery choice
- Rollout and recovery considerations
- Security, policy, and observability gaps
