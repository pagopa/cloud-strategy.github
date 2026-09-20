# Report Layout

## Compact report order

Open with the review verdict, the separate evidence outcome, and a one-sentence
reason that states the declared use, reviewed scope, coverage, and material
limit. Then use this order and omit sections that do not change the review:

1. `# 🛰️ Review High Level: <target>`.
2. Verdict and evidence outcome with the reason blockquote.
3. The smallest useful purpose-selected diagram set, if a visual adds value.
4. `## 📌 Findings` with material finding blocks.
5. `## 🧪 Evidence gaps` that can change the verdict.
6. `## ❓ Open` when a material question remains.
7. `## 👉 Next` with concrete follow-up actions.

## Finding block shape

Each finding is one compact block. Keep `Problem`, `Suggestion`, and `Why`
stable in the current report language:

```markdown
**N. <short title>** — <severity>/<confidence>

- **<Problem>:** what is wrong, one to two sentences, with a traceable
  location such as `path:line` or section reference.
- **<Suggestion>:** the smallest useful report-only follow-up, one to two
  sentences.
- **<Why>:** why it matters for the verdict, one to two sentences.
- **Location:** the affected artifact, section, transition, or mechanism.
- **Evidence:** `direct observation`, `supported inference`, or `evidence gap`,
  with the supporting anchor.
- **Consequence:** the effect on the declared use, affected transition, or
  accountability boundary.
- **Expected verification:** the closure condition when closure is not
  obvious; omit it only when the report already states a complete check.
```

Rules:

- Severity and confidence are written as independent canonical values. Use the
  full severity vocabulary `critical`, `high`, `medium`, and `low`; symbols or
  formatting may accompany them but cannot carry their meaning alone.
- Each field must be understandable without rereading the investigation:
  name the file, section, decision, or mechanism involved; never a cryptic ID
  alone.
- Do not emit `Fix owner` in chat; route it to the caller-owned record when one
  exists. Keep `Expected verification` visible whenever the finding is not
  self-closing.
- Keep residual risk beside the finding or evidence gap it qualifies.

For a flow finding, `Location`, `Evidence`, `Consequence`, and `Expected
verification` identify the affected transition and the check that would close
the finding. A proposed improvement remains a recommendation; it never
changes the reviewed artifact.

## Evidence gaps shape

Each gap is a bold name followed by what stays unconfirmed and why it can
change the verdict. A bare name or one-word entry is invalid.

## Open shape

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

Use the smallest useful diagram set, including no diagram, when a visual
projection clarifies relationships in scope. Select the diagram by purpose:

- Use `flowchart TD` or `flowchart LR` for branches, dependencies, loops,
  dead ends, and ownership paths.
- Use `sequenceDiagram` for actor handoffs, messages, approvals, and other
  ordered interactions.
- Use `stateDiagram-v2` for lifecycle states, stop conditions, recovery, and
  completion.

When flow analysis is in scope, trace the relevant trigger, preconditions,
actors, inputs, outputs, decisions, handoffs, completion, failures, recovery,
ownership, contradictory conditions, dead ends, and cycles without exit. Do not
claim a relationship is covered merely because it appears in a visual summary.

Mark each material relationship as `[documented]`, `[observed]`, `[proposed]`,
or `[unknown]` in the diagram or adjacent prose:

- `documented` is stated by the reviewed artifact or governing source.
- `observed` requires captured runtime or other direct operational evidence;
  static YAML, metadata, and diagrams alone cannot establish it.
- `proposed` is a recommended or desired relationship, not current behavior.
- `unknown` is not established by the available evidence.

Diagrams are optional, theme-neutral, and readable without color. Do not use
fixed semantic fills or color as the only meaning carrier. If no compatible
Mermaid renderer was used, say that the diagram is unverified in adjacent
prose. The controlling conclusion, provenance, and evidence remain
understandable when the diagram is not rendered.
