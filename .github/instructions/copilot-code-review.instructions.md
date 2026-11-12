---
description: Severity anchors and cross-cutting security and change-hygiene checks for every changed file.
applyTo: "**"
excludeAgent: "cloud-agent"
---

# Cross-Cutting Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

## Severity Anchors

- Critical: secret exposure, remote code execution, data loss, an unguarded destructive action, or a merge-blocking contract break.
- Major: a correctness bug, security weakness, broken validator or CI gate, behavior regression, or changed behavior without tests.
- Minor: an edge-case, resilience, observability, or maintainability risk worth fixing before merge.
- Nit: an optional clarity issue. Raise it only when it can cause misreading.

## Security

- Least privilege and no hardcoded secrets are merge-blocking expectations.
- Flag new permissions, roles, token scopes, or network exposure broader than the change needs.
- Flag credentials, tokens, keys, and tenant or account identifiers in code, configuration, fixtures, logs, or docs.
- Flag untrusted input that reaches shell commands, file paths, templates, queries, or deserialization without validation.
- Flag delete, overwrite, force-push, or state-removal operations without a guard, dry run, or explicit confirmation.

## Change Hygiene

- Flag rewrites of unaffected code, dead code, and leftover debug output.
- Flag dependency additions that are unpinned, unused, or broader than the change needs.
- Flag user-visible behavior changes without matching docs, changelog, or migration notes when the repository keeps them.
