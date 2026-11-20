# Mermaid Contract

Use this reference when deciding whether a repository knowledge document needs
a diagram or when authoring Mermaid source. A diagram is warranted by an
evidenced relationship and a reader question, not by a generic preference for
visuals.

## Warranted Relationships

| Evidenced relationship | Diagram type | Use when the reader needs |
| --- | --- | --- |
| Dependencies or data flow across at least three components | `flowchart` | The direction of dependency or data movement. |
| Calls or identity hops involving at least two actors and three steps | `sequenceDiagram` | The order of interactions and responsibility at each hop. |
| A lifecycle with at least three states | `stateDiagram-v2` | The valid states and transitions. |
| Ownership boundaries across at least two contexts | `flowchart` with subgraphs | The context boundary and which owner contains each component. |

Decide separately for each reader question. Several matching relationships may
be answered by one diagram; a matching threshold alone does not require one.
Include a diagram only when it makes the evidenced relationship clearer than
concise prose or a link to an existing owner. If an expected diagram is
omitted, record `omitted: <path>: <reason>` in the completion report. A valid
reason is that the owner document already draws the relationship, or that a
sentence communicates it fully.

## Local Diagram Cap And Size

Use at most two diagrams in one document as the default. This is a local,
derogable threshold, not a universal Mermaid rule. A third diagram is allowed
only for an independent reader question that cannot be combined clearly with
the first two. Record the reason in the report as
`diagrams: <path>: derogated(<reason>)`. If the third question is not
independent, link to the owner diagram or split the document only when the
document boundary also meets [knowledge topology](knowledge-topology.md).

Keep each `flowchart` and `stateDiagram-v2` to about 15 nodes or fewer. Keep a
`sequenceDiagram` to about six participants and 15 messages or fewer. If the
reader needs more, split the explanation across diagrams only when each serves
a distinct question; otherwise use a focused owner link or prose.

## Source Rules

- Use only `flowchart`, `sequenceDiagram`, and `stateDiagram-v2`.
- Give every diagram an `accTitle` and `accDescr`, and explain its conclusion
  in adjacent prose.
- Use stable ASCII identifiers and literal `-->` or `->>` arrows.
- Keep source theme-neutral: do not set a theme or use custom link styling,
  HTML labels, clickable nodes, icon packs, or experimental diagram types.
- Keep every edge grounded in repository evidence. A diagram may not add a
  relationship, state, or actor that the text and evidence do not support.

## Validation Evidence

Check source structure and warranted relationships separately. Parse a
diagram with `mmdc` when it is available; when it is unavailable, report the
parse check as `not-run` with that reason. A parse result establishes syntax
only, not evidentiary accuracy or reader value.
