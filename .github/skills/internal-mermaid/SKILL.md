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

## Theme-neutral communication

- Let the renderer and the active light or dark theme own the fill and text
  contrast of every box that contains visible text.
- Express meaning in this order: text labels; topology, direction, and labeled
  edges; native shapes and line patterns; then emoji as supplementary cues.
- Pair every emoji with a text label. The diagram must remain understandable if
  an emoji is missing, monochrome, or rendered differently.
- Add a short legend when symbols are numerous or their meaning is not obvious.
- Use `accTitle` and `accDescr` when supported, and state the controlling
  conclusion in adjacent prose when the diagram carries one.
- Apply an explicit fill color only to a box whose rendered content is empty.
  A box containing a label, value, icon, emoji, or legend text must retain the
  renderer's default fill and text colors. A node ID does not make a box empty
  when the renderer displays that ID.
- For an empty box, `style`, `classDef`, and `class` may set `fill` only. Omit
  all other explicit colors and appearance styling, including `linkStyle`,
  `theme`, `themeVariables`, and appearance-oriented init directives.

## Generate

- Clarify the purpose and audience first.
- Pick the smallest diagram type that fits: flowchart, sequence, state, class, ER, or journey.
- Quote node labels, especially labels containing punctuation.
- Apply Theme-neutral communication.
- Keep the diagram minimal. Include only relationships that serve its purpose.

## Modify

- Preserve existing node IDs, edge directions, and shape semantics.
- Produce the minimal diff needed for the requested change.
- Apply Theme-neutral communication.
- Preserve compatible existing styling. Remove an explicit fill from any
  text-bearing box touched by the requested change.
- Keep unaffected labels, ordering, and relationships stable.

## Validate

- Check the diagram with an available renderer such as `mmdc` or the Mermaid Live Editor.
- Without an available renderer, report the diagram as unverified. Never claim validity from inspection alone.
- Audit every explicit fill target and confirm that its rendered box contains
  no visible content. Audit the remaining source for explicit colors, themes,
  and appearance styling.
- When visual compatibility is material, render the same source with both light
  and dark themes and confirm that meaning remains clear.
- Confirm that text carries the meaning and emoji are only supplementary cues.
- Check that the chosen diagram type supports its syntax and arrows.

## Review

- Prefer the smallest Mermaid diagram type that fits the purpose.
- Use quoted labels and a readable direction.
- Treat an explicit fill on a text-bearing box as a readability defect. Treat
  other explicit colors, themes, or appearance styling as a theme-compatibility
  risk.
- Confirm that removing emoji or line styling would not remove essential meaning.
- Reject decorative diagrams that do not communicate a needed relationship.

## Troubleshoot

- Reduce the diagram to the smallest failing snippet, then add parts back one at a time.
- Treat a text-bearing box with an explicit fill as the first likely cause of
  light/dark contrast failures. Isolate other explicit colors, themes, or
  appearance styling while diagnosing.
- Check for unquoted labels containing `()[]#;`.
- Check for a missing or wrong diagram type.
- Check that arrows are valid for the chosen type.
