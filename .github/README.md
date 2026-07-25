# .github Configuration

This directory is the source-side catalog for reusable GitHub Copilot
customization assets maintained in `cloud-strategy.github`.

- Root [`AGENTS.md`](../AGENTS.md) is the strategic agent-policy entrypoint.
- `.github/copilot-instructions.md` is review-only for GitHub.com Copilot code review.
- [`INVENTORY.md`](INVENTORY.md) is the exact path inventory for the live catalog.

## Agents

- Canonical repository-owned gateway agents:
  `internal-gateway-idea`, `internal-gateway-review-generic`,
  `internal-gateway-critical-master`, `internal-gateway-simple-task`
- Specialist repository-owned review agents:
  `internal-gateway-review-code` for code-focused review before merge or follow-up action.
- Approved retained plans under tmp/superpowers/plans/ execute through
  `internal-gateway-execute-plans`.
- When extra provenance helps, offer it as an optional follow-up detail and accept
  number-only replies.
