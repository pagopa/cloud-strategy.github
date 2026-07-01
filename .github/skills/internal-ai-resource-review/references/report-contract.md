# Report Contract

Use this reference before writing the final review. Keep output proportional to
the selected profile.

## Evidence labels

Use short, explicit evidence labels in findings and recommendations:

- `file`: direct file content proves the claim
- `bundle`: a bundle root plus siblings prove the claim
- `validator`: a validator or script output proves the claim
- `test`: a focused test proves the claim
- `test-gap`: a missing focused test is the supported risk
- `sync`: sync catalog or runtime support evidence proves the claim
- `runtime-artifact`: live prompt pack, generated artifact, or fixture evidence
  proves the runtime-facing behavior
- `retained`: a retained package supports the claim, but live verification is
  still required
- `gap`: evidence is missing, stale, or unverifiable
- `uncertain`: the claim remains plausible but not proven by available evidence

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

## Adaptive layout patterns

Use the shortest layout that still supports the user's decision. Section names
may vary, but the final answer must preserve the decision logic.

For normal AI-resource reviews, prefer:

1. verdict with confidence
2. material findings, defect-first
3. evidence digest
4. decision trace
5. next step
6. residual risk

For high-severity findings, lead with findings, then impact and next step.

For no-finding or low-finding reviews, make the decision logic explicit with a
verdict, evidence digest, decision trace, next step, and residual risk. Do not
invent extra findings to make a small review look more substantial.

## Evidence compression

Separate evidence into these layers:

- `user-facing evidence`: proof the user needs to trust the verdict;
- `working evidence`: tool outputs, broad grep results, long diffs, file maps,
  and checklists used during review;
- `internal synthesis`: comparisons, grouping, counterfactuals, and rejected
  paths.

Only user-facing evidence appears by default. Compress working evidence with an
evidence digest, a 2-4 line decision trace, compact evidence labels, and a named
residual risk. Use small tables only when they clarify the decision. Suppress raw
output when a digest preserves the same proof strength.

## Missing proof handling

When a proof cannot be run or loaded, report:

1. the unavailable proof;
2. why it could not be used;
3. the confidence impact;
4. the substitute check used, if any;
5. the expected follow-up validation.

Partial evidence may support a verdict, but the unavailable focused proof stays
visible as residual risk.

## Required sections

Every final review should include:

1. selected profile and target
2. findings first, or an explicit no-findings result
3. evidence labels for each material claim
4. decision or recommended next action
5. validation path or explicit evidence gap
6. residual risk

Small reviews may merge sections only when the verdict, evidence digest,
decision trace, next action, and residual risk remain understandable.

## Completeness pass

Before closing the review, confirm all of these:

1. The selected profile still matches the target.
2. The relevant resource families were actually reviewed.
3. Every material recommendation names the affected validator, test, sync, or
   propagation surface, or marks the gap.
4. Bundle reviews confirm each existing bundle sibling was reviewed or marked
   intentional non-action.
5. Drift findings came from `internal-copilot-audit` when that lens was needed.
6. No-finding and low-finding reviews still explain why the result matters and
  what next action follows.
7. The report stays proportional to the evidence and does not expand into an
   encyclopedic catalog dump.
