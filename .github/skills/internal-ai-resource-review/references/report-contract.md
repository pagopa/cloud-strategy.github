# Report Contract

Use this reference before writing the final review. Keep output proportional to
the selected profile.

## Evidence labels

Use short, explicit evidence labels in findings and recommendations:

- `file`: direct file content proves the claim
- `bundle`: a bundle root plus siblings prove the claim
- `validator`: a validator or script output proves the claim
- `test`: a focused test proves the claim
- `sync`: sync catalog or runtime support evidence proves the claim
- `retained`: a retained package supports the claim, but live verification is
  still required
- `gap`: evidence is missing, stale, or unverifiable

## Decision vocabulary

Use one primary action per finding or summary line:

- `KEEP`
- `PATCH`
- `WRAP`
- `SPLIT`
- `MERGE`
- `MOVE`
- `RETIRE`
- `CREATE`
- `COMPRESS`
- `AUTOMATE`
- `REVIEW_LATER`

## Output size

- `focused`: concise chat answer with only material findings and one keep line
  when no issue exists
- `bundle`: compact chat review with findings, bundle coverage notes, and the
  affected propagation surfaces
- `catalog`: compact but structured summary with grouped findings and explicit
  evidence gaps
- `retained-report`: retained output under `tmp/` only when the user asked for
  it or the target is already a retained package

## Required sections

Every final review should include:

1. selected profile and target
2. findings first, or an explicit no-findings result
3. evidence labels for each material claim
4. decision or recommended next action
5. validation path or explicit evidence gap
6. residual risk

## Completeness pass

Before closing the review, confirm all of these:

1. The selected profile still matches the target.
2. The relevant resource families were actually reviewed.
3. Every material recommendation names the affected validator, test, sync, or
   propagation surface, or marks the gap.
4. Bundle reviews confirm each existing bundle sibling was reviewed or marked
   intentional non-action.
5. Drift findings came from `internal-copilot-audit` when that lens was needed.
6. The report stays proportional to the evidence and does not expand into an
   encyclopedic catalog dump.
