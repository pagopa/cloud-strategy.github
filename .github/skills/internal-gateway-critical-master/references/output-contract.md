# Output Contract

Use this reference to produce a compact, consistent critical challenge deliverable.

## Required fields

| Field | Description | Max length |
| --- | --- | --- |
| `summary` | One paragraph: what is being challenged and why it matters now. | 75 words |
| `findings` | 1-3 findings. Each finding uses the sub-fields below. | 3 items |
| `finding.objection` | Strongest objection or assumption gap. | 30 words |
| `finding.impact` | Why it matters now. | 30 words |
| `finding.evidence` | Repository evidence, inference, or named uncertainty. | 30 words |
| `finding.mitigation` | Condition or action required before execution resumes. | 30 words |
| `finding.reframe` | Optional lateral reframe. | 25 words |
| `finding.question` | Optional single root question when the answer would materially change the critique. | 25 words |
| `synthesis` | Result of the Final Consistency Gate, including defense classification, strongest defense, and remaining vulnerability when user defenses exist. | 100 words |
| `outcome` | Exactly one value from `## Outcome meanings` in `SKILL.md`. | 1 value |

## Budget

- Total output target: **600 words or fewer**.
- If the material demands more, split the work into another critical cycle.
- Do not pad findings to reach 3; one strong finding is better than three weak ones.

## Output template

```markdown
## Summary

<summary>

## Findings

### 1. <objection>

- **Impact:** <impact>
- **Evidence:** <evidence>
- **Mitigation:** <mitigation>
- **Reframe:** <reframe>
- **Question:** <question>

## Synthesis

<synthesis>

## Outcome

`<outcome>`
```

## Example

```markdown
## Summary

We are challenging a proposal to move validation logic from CI into a pre-commit hook. The change matters now because it affects every contributor's workflow and could hide failures from the central audit log.

## Findings

### 1. The audit trail weakens

- **Impact:** Central CI logs become incomplete for compliance reviews.
- **Evidence:** `inference` — no replacement logging is described.
- **Mitigation:** Add a signed attestation step before the hook is enabled.
- **Reframe:** Treat local validation as an early filter, not a replacement for CI. (Analogy: like a spell-checker that does not replace a full code review.)
- **Question:** Which central audit record replaces the CI validation log?

## Synthesis

The strongest risk is compliance visibility, not implementation effort. The proposal can work if the mitigation is accepted.

## Outcome

`accept-with-risk`
```
