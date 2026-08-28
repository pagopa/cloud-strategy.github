---
name: internal-mermaid
description: Use when generating, modifying, validating, reviewing, or troubleshooting Mermaid diagrams.
---

# Internal Mermaid

## When to use

- Mermaid diagrams are the active deliverable or require structural review.
- A diagram needs a minimal, readable representation of system relationships.

## When not to use

- The work concerns prose, policy, or another diagram language rather than Mermaid.
- A visual editor or renderer is the primary task.

## Generate

- Clarify the purpose and audience first.
- Pick the smallest diagram type that fits: flowchart, sequence, state, class, ER, or journey.
- Quote node labels, especially labels containing punctuation.
- Keep the diagram minimal. Include only relationships that serve its purpose.

## Modify

- Preserve existing node IDs, edge directions, and shape semantics.
- Produce the minimal diff needed for the requested change.
- Keep unaffected labels, ordering, and relationships stable.

## Validate

- Check the diagram with an available renderer such as `mmdc` or the Mermaid Live Editor.
- Without an available renderer, report the diagram as unverified. Never claim validity from inspection alone.
- Check that the chosen diagram type supports its syntax and arrows.

## Review

- Prefer the smallest Mermaid diagram type that fits the purpose.
- Use quoted labels and a readable direction.
- Reject decorative diagrams that do not communicate a needed relationship.

## Troubleshoot

- Reduce the diagram to the smallest failing snippet, then add parts back one at a time.
- Check for unquoted labels containing `()[]#;`.
- Check for a missing or wrong diagram type.
- Check that arrows are valid for the chosen type.
