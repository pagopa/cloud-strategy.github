# Analysis Of Agent Rules

Target: `agent-rules.md`.

1. The file repeats "Keep diffs small and focused on the request." in two
   sections. Remove one copy.
2. The file has no rule about credentials or secrets. Add a secrets section.
3. "Ask before deleting any file" and "Ask before changing a public API" use
   the same permission shape. Merge them with the `build/` cleanup rule into
   one rule: "Ask before any destructive change."
