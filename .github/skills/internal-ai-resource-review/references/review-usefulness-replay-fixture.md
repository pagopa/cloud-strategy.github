# Review Usefulness Replay Fixture

Use this fixture when validating that AI-resource reviews are decision-useful
without becoming long reports.

## Input

- Target: `.github/skills/local-ai-chatgpt-prompt-creator`.
- Branch diff tightens only the `coach-personale` validator profile.
- Live `coach-personale` prompt pack passes the validator with the required
  support pack.
- No focused `coach-personale` profile test exists.
- Focused pytest execution is unavailable in the active environment.
- Sync and inventory evidence do not show material drift.

## Expected Review Behavior

- Reports no immediate runtime break observed.
- Reports one material low-severity finding or decision note about missing
  profile-specific tests.
- Explains why the low finding matters.
- Uses an evidence digest instead of raw command output.
- Includes a decision trace that rules out unsupported drift or runtime-break
  claims.
- Names unavailable pytest execution as residual risk.
- Recommends the smallest useful next step: add focused `coach-personale`
  pass/fail validator tests.
- Does not invent additional findings to make the review look more substantial.

## Compressed Output Shape

```markdown
## Verdict

No immediate runtime break observed. The live `coach-personale` pack passes the
updated validator, but the tightened profile lacks dedicated regression
coverage.

## Findings

Low: `coach-personale` profile rules changed without a focused pass/fail test.

## Evidence Digest

Checked branch diff, validator helper, live prompt pack, nearby tests, and
inventory/sync references.

## Decision Trace

Runtime break is not supported because the live pack passes. Sync drift is not
supported because the changed surface is the validator helper and catalog
references remain present. The supported risk is test protection for the new
profile contract.

## Next Step

Add focused `coach-personale` validator tests for the required tokens and
support files.

## Residual Risk

Focused pytest execution was unavailable in the active environment.
```
