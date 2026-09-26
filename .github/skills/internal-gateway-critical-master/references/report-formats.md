# Critical Master Report Formats

## Lens Line

Directly after the conclusion line, write `🔎`, the localized label, and the
applied lenses in order, separated by `·`; append `— pre-mortem` when one
ran. Example:
`🔎 **Lenses:** first principles · scope compression · reverse assumption — pre-mortem`.

## Finding Block

Each finding is one compact block:

```markdown
**N. <dot> <short title>** — <classification> · <severity>/<confidence>

- **<Problem>:** what is wrong, one to two sentences, concrete.
- **<Suggestion>:** the smallest change that fixes it, one to two sentences.
- **<Why>:** why it matters, one to two sentences.
```

Severity is `high`, `medium`, or `low`, with stable dots: 🔴 high, 🟡 medium,
🟢 low. Confidence reuses the finding's evidence quality: `strong`, `partial`,
or `weak`. Each field must identify
the relevant file, decision, or mechanism without requiring the investigation
transcript. A defense belongs in the subject's rationale, not in a finding,
with one exception: a material finding the defense resolves renders as one
non-blocking line, `**N. ⚪ <short title>** — rejected-with-reason: <reason>.`
The same line renders a finding closed by new evidence in a delta pass.
Keep `Fix owner` in the caller-owned ledger. Supply `Expected verification` to
that ledger in caller mode; on direct invocation, state it inside the matching
`Next` item.

## Residuals

Each residual risk is a bold name followed by what stays open and why it
matters. Report a deferral only with its consequence.

## Open Questions

Number each material question. For choices, list lettered options with their
consequences and mark one suggested option with `💡` plus a one-sentence reason.

## Next Actions

Number each concrete action and identify the finding or residual it closes.

## Rerun Suppression

In caller mode, when the unit and evidence snapshot are unchanged, emit only
this projection, translated into the current chat language:

```markdown
# 🔍 Critical Analysis

🎯 **suppressed-unchanged**: <unit> has no changed claim, evidence, assumption, or scope since the last completed pass; its conclusion `<previous conclusion>` stands.

## ✅ Next
1. Supply the changed evidence or scope that would justify a delta or full pass.
```

## Mermaid

Use at most one top-down flowchart when it clarifies at least three material
causal, dependency, ownership, or state relationships. Use one node per
finding or effect and short `\n`-broken labels that include the severity word.
Fills are optional and never the only carrier of meaning. Preserve the
controlling conclusion in adjacent prose.

## No-Context Failure

When no subject or evidence can be recovered, emit only this projection,
translated into the current chat language:

```markdown
# 🔍 Critical Analysis

🎯 **failure-no-context**: no analysable context was available.

## ✅ Next
1. Provide a subject, decision, proposal, design, document, or evidence to critique.
```
