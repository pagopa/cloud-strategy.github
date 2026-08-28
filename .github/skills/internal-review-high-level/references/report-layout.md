# Report Layout

### Finding block shape

Each finding is one compact block:

```markdown
**N. <dot> <short title>** — <severity>/<confidence>

- **<Problem>:** what is wrong, one to two sentences, with a traceable
  location such as `path:line` or section reference.
- **<Suggestion>:** the smallest useful report-only follow-up, one to two
  sentences.
- **<Why>:** why it matters for the verdict, one to two sentences.
```

Rules:

- Severity dots are stable: 🔴 high, 🟡 medium, 🟢 low.
- Each field must be understandable without rereading the investigation:
  name the file, section, decision, or mechanism involved; never a cryptic ID
  alone.
- Do not emit `Fix owner` or `Expected verification` fields in chat; route
  them to the caller-owned record when one exists.
- Keep residual risk beside the finding or evidence gap it qualifies.

### Evidence gaps shape

Each gap is a bold name followed by what stays unconfirmed and why it can
change the verdict. A bare name or one-word entry is invalid.

### Open shape

Each open question is numbered and stated in plain language. When the answer
is a choice, list lettered options with their consequence (for example `A)`
keep the current owner, `B)` propose a separate design), then add one
suggested option marked with `💡` together with a one-sentence reason. Omit
the section when nothing material is open.

### Next shape

Number each action, make it concrete, and reference the finding, evidence
gap, or open question it closes. One action per step; no vague instructions
such as "improve the document".

### Mermaid rules

Use at most one diagram, and only when it clarifies three or more material
causal, dependency, ownership, or state relationships. Use a top-down
flowchart with:

- one node per finding or effect, anchored as `Finding N` or by its short
  name;
- short self-explanatory phrases of two to four `\n`-broken lines, not bare
  IDs;
- an emoji prefix per node and semantic fills: red for the problem, amber for
  decision-level effects, yellow for verdict-level effects;
- the controlling conclusion in adjacent prose; the diagram is never the sole
  carrier of evidence.
