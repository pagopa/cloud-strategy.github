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

## Chat projection

For `chat-only` reviews, use the shortest projection that still supports the
user's decision. Start with exactly four fields in this order:

- `🔎`: a localized verdict and counts by severity.
- `📌`: one sentence explaining why that verdict follows.
- `🧪`: reviewed scope, completed validation, and any material evidence gap.
- `👉`: one user action and the consequence of accepting it.

Visible labels match the user's chat language. Canonical uppercase decision
values and evidence labels are internal by default. Map Critical findings to
`B` identifiers, Important findings to `I` identifiers, and Suggestions to
`S` identifiers. Show every blocking and important finding, consolidate
equivalent findings, and keep suggestions compact.

Every material finding contains `Location`, `Evidence`, `Impact`, and
`Correction`. Add `Expected verification` when closure is not obvious. Mark
uncertainty inline as `to confirm` and do not create another severity.

Keep counter-analysis records, review gates, decision traces, and internal
evidence digests hidden unless they materially change the verdict. Missing
proof stays visible through `🧪`. The final action names one user response and
states its consequence; a review never implies that a patch was already
applied.

## Retained output

Use retained output only when the user asks for it or the selected target is a
retained review package. Preserve profile-proportional detail, evidence
labels, evidence digest, decision trace, validation gaps, and residual risk
when the retained artifact needs them. Retained output may keep canonical
uppercase decision values and internal evidence labels.

Retained review completion returns a compact chat card plus the retained path.
The chat summary must remain distinct from the retained report and must not
replace its evidence, decision trace, validation gaps, or residual-risk
detail. Keep retained reports under `tmp/` and preserve their existing file
layout.

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

## Conditional requirements

Chat-only output follows `Chat projection`. Retained output follows `Retained
output` and returns the compact chat card with the retained path. Use the
selected profile and target as internal review context, and surface them in
chat only when they change the user's decision.

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
