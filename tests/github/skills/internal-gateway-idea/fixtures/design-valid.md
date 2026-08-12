# Idea Design

## Intent

Keep the idea gateway fail closed across clean-chat resumption.

## Accepted Decisions

- Persist the canonical v3 state and typed event ledger separately from the Markdown design.
- Require a typed event at every content-bearing gate.

## Open Decisions

- None recorded.

## Selected Approach

Use one standard-library state and persistence owner with two ordered artifacts.

## Essential Evidence

- Focused state and producer-consumer tests.
- Strict skill validation and bounded CLI output.
