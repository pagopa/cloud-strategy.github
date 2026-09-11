# Critical Master Report Formats

## Finding Block

Each finding is one compact block:

```markdown
**N. <dot> <short title>** — <classification> · <severity>/<confidence>

- **<Problem>:** what is wrong, one to two sentences, concrete.
- **<Suggestion>:** the smallest change that fixes it, one to two sentences.
- **<Why>:** why it matters, one to two sentences.
```

Severity dots are stable: 🔴 high, 🟡 medium, 🟢 low. Each field must identify
the relevant file, decision, or mechanism without requiring the investigation
transcript. A defense belongs in the subject's rationale, not in a finding.
Keep `Fix owner` and `Expected verification` in the caller-owned ledger.

## Residuals

Each residual risk is a bold name followed by what stays open and why it
matters. Report a deferral only with its consequence.

## Open Questions

Number each material question. For choices, list lettered options with their
consequences and mark one suggested option with `💡` plus a one-sentence reason.

## Next Actions

Number each concrete action and identify the finding or residual it closes.

## Mermaid

Use at most one top-down flowchart when it clarifies at least three material
causal, dependency, ownership, or state relationships. Use one node per
finding or effect, short `\n`-broken labels, and semantic red, amber, and
yellow fills. Preserve the controlling conclusion in adjacent prose.

## No-Context Failure

When no subject or evidence can be recovered, emit only:

```markdown
# Critical Analysis

## Status
Failure: no analysable context was available.

## Required Context
Provide a subject, decision, proposal, design, document, or evidence to critique.
```
