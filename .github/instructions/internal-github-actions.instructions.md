---
description: GitHub Actions review checks for pinning, least privilege, script injection, untrusted triggers, and deterministic execution.
applyTo: "**/workflows/**,**/actions/**/action.y*ml"
excludeAgent: "cloud-agent"
---

# GitHub Actions Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag action and container references that are not pinned to immutable SHAs or digests.
- Verify `permissions` are least privilege at workflow and job scope.
- Flag `${{ }}` expressions with attacker-controlled data, such as pull request titles, bodies, branch names, or inputs, placed directly in `run:` scripts. Pass them through `env:`.
- Flag `pull_request_target` or `workflow_run` jobs that check out or run pull request code while holding secrets or write permissions.
- Check secret usage to ensure no hardcoded sensitive values in workflows.
- Flag long-lived cloud credentials in secrets where OIDC should be used.
- Flag production deploy jobs without protected `environment` reviewers.
- Flag `workflow_dispatch` inputs consumed by shell or deploy steps without validation.
- Verify concurrency, timeout, and cancellation controls for long-running jobs.
- Check cache and artifact keys for deterministic behavior and retention clarity.
- Flag renamed jobs or workflows that break required-check names in branch protection or rulesets.
- Trace changed reusable workflows and composite actions to their callers; flag callers left on the old inputs, outputs, or secrets.
