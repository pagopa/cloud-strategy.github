# .github Configuration

This directory is the source-side catalog for reusable GitHub Copilot
customization assets maintained in `cloud-strategy.github`.

- Root [`AGENTS.md`](../AGENTS.md) is the strategic entrypoint.
- `.github/copilot-instructions.md` is the compact repo-wide Copilot routing bridge.
- `.github/instructions/copilot-code-review.instructions.md` owns the global review baseline.
- [`INVENTORY.md`](INVENTORY.md) is the exact path inventory for the live catalog.

## Agents

- Canonical repository-owned gateway agents:
  `internal-gateway-idea-brainstorming`, `internal-gateway-review`,
  `internal-gateway-critical-master`, `internal-gateway-simple-task`
- Approved `extended` retained plans execute through
  `internal-gateway-execute-plans`.
- When extra provenance helps, offer it as an optional follow-up detail and accept
  number-only replies.
