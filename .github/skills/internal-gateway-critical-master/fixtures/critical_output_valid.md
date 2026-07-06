## Summary

We are challenging a proposal to move validation logic from CI into a pre-commit hook. The change matters now because it affects every contributor's workflow and could hide failures from the central audit log.

## Findings

### 1. The audit trail weakens

- **Impact:** Central CI logs become incomplete for compliance reviews.
- **Evidence:** `inference` - no replacement logging is described.
- **Mitigation:** Add a signed attestation step before the hook is enabled.
- **Reframe:** Treat local validation as an early filter, not a replacement for CI.
- **Question:** Which central audit record replaces the CI validation log?

## Synthesis

The strongest risk is compliance visibility, not implementation effort. The proposal can work if the mitigation is accepted.

## Outcome

`accept-with-risk`
