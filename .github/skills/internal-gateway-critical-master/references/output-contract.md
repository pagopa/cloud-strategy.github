# Output Contract

Use this reference to produce a compact, consistent critical challenge deliverable.

## Required section order

1. `## Summary`
2. `## Challenge Context`
3. Optional `## Pre-mortem` (required only when pre-mortem status is `triggered`)
4. `## Findings`
5. `## Synthesis`
6. `## Outcome`

## Required fields

| Field | Description | Max length |
| --- | --- | --- |
| `summary` | One paragraph: what is being challenged and why it matters now. | 75 words |
| `challenge_context.lenses` | Exactly three lenses used; the third must be `analogy` or `reverse-assumption`. | 3 items |
| `challenge_context.premortem` | `triggered` or `not-triggered`. | 1 value |
| `findings` | 1-3 findings. Each finding uses the sub-fields below. | 3 items |
| `finding.objection` | Strongest objection or assumption gap. | 30 words |
| `finding.impact` | Why it matters now. | 30 words |
| `finding.evidence` | Claim class and evidence quality; see evidence shape below. | 30 words |
| `finding.mitigation` | Condition or action required before execution resumes. | 30 words |
| `finding.reframe` | Optional lateral reframe. | 25 words |
| `finding.question` | Optional single root question across all findings. At most one. | 25 words |
| `synthesis.defense` | One of `none`, `resolves`, `narrows`, `accepts-risk`, `unanswered`. | 1 value |
| `synthesis.strongest_objection` | The strongest supported objection. | 15 words |
| `synthesis.unresolved_uncertainty` | Named uncertainty remaining after the gate. | 15 words |
| `synthesis.strongest_defense` | Required when Defense is not `none`. | 15 words |
| `synthesis.remaining_vulnerability` | Required when Defense is not `none`. | 15 words |
| `outcome` | Exactly one value from `## Outcome meanings` in `SKILL.md`. | 1 value |

## Evidence shape

Each finding's evidence bullet declares a claim class and an evidence quality:

```markdown
- **Evidence:** `inference`; quality=`partial` — no replacement audit record is described.
```

Allowed claim classes: `confirmed`, `inference`, `estimate`.
Allowed evidence quality values: `strong`, `partial`, `weak`.

## Pre-mortem shape

When `Pre-mortem: triggered`, include one failure and 2-3 causes with qualitative likelihood:

```markdown
## Pre-mortem

- **Failure:** Central compliance evidence disappears after rollout.
- **Cause 1:** Local-only logs | class=`inference` | likelihood=`high` | mitigation=retain central signed validation.
- **Cause 2:** Partial adoption | class=`estimate` | likelihood=`medium` | mitigation=gate rollout on repository coverage.
```

Allowed likelihood values: `high`, `medium`, `low`.
A non-empty mitigation is required for every `high` or `medium` cause.

## Defense shape

When Defense is `none`, no additional defense fields are required.
When Defense is not `none`, add both `Strongest defense` and `Remaining vulnerability`:

```markdown
- **Defense:** `narrows`
- **Strongest objection:** Compliance visibility remains unowned.
- **Unresolved uncertainty:** The replacement audit record is unknown.
- **Strongest defense:** A signed attestation step narrows the audit gap.
- **Remaining vulnerability:** Attestation coverage depends on local adoption.
```

## Output template

```markdown
## Summary

<summary>

## Challenge Context

- **Lenses:** <lens1>, <lens2>, <lens3>
- **Pre-mortem:** `not-triggered`

## Findings

### 1. <objection>

- **Impact:** <impact>
- **Evidence:** `<class>`; quality=`<quality>` — <evidence>
- **Mitigation:** <mitigation>
- **Reframe:** <reframe>
- **Question:** <question>

## Synthesis

- **Defense:** `<defense>`
- **Strongest objection:** <objection>
- **Unresolved uncertainty:** <uncertainty>

## Outcome

`<outcome>`
```

## Example

```markdown
## Summary

We are challenging a proposal to move validation logic from CI into a pre-commit hook. The change matters now because it affects every contributor's workflow and could hide failures from the central audit log.

## Challenge Context

- **Lenses:** first-principles, constraint-audit, reverse-assumption
- **Pre-mortem:** `not-triggered`

## Findings

### 1. The audit trail weakens

- **Impact:** Central CI logs become incomplete for compliance reviews.
- **Evidence:** `inference`; quality=`partial` — no replacement logging is described.
- **Mitigation:** Add a signed attestation step before the hook is enabled.
- **Reframe:** Treat local validation as an early filter, not a replacement for CI.
- **Question:** Which central audit record replaces the CI validation log?

## Synthesis

- **Defense:** `none`
- **Strongest objection:** Compliance visibility remains unowned.
- **Unresolved uncertainty:** The replacement audit record is unknown.

## Outcome

`accept-with-risk`
```

## Budget

- Total output target: **600 words or fewer**.
- If the material demands more, split the work into another critical cycle.
- Do not pad findings to reach 3; one strong finding is better than three weak ones.
