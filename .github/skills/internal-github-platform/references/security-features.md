# Security Features

This skill owns the rollout plan for GitHub security features. Feature
configuration belongs to the matching skill.

| Feature | Configuration owner |
|---|---|
| Code scanning with CodeQL, including default setup and Actions workflow scanning | `/awesome-copilot-codeql` |
| Dependabot alerts, security updates, and version updates | `/awesome-copilot-dependabot` |
| Secret scanning, push protection, custom patterns, alert remediation | `/awesome-copilot-secret-scanning` |

## Rollout plan shape

1. Inventory repositories by visibility, language, and criticality.
2. Pick the first wave: a few representative repositories with active owners.
3. Enable features in a fixed order, for example dependency graph and
   Dependabot alerts, then secret scanning with push protection, then code
   scanning.
4. Set alert triage owners and response targets before widening.
5. Widen in waves and prove each wave with alert volume, false-positive rate,
   and blocked-push counts from the audit log or security overview.
6. Record exceptions (for example archived or vendored repositories) with an
   owner and review date.

Features and licensing change over time. Verify current plan requirements in
GitHub documentation before committing to a rollout order.
