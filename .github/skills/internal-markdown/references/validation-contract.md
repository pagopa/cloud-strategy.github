# Markdown validation contract

The bundle checker accepts explicit Markdown files and feeds each file
through standard input to `markdownlint-cli2` 0.22.1 with the bundled
configuration. Install the pinned tool without changing the repository:

```bash
npm install -g markdownlint-cli2@0.22.1
```

The checker is read-only, processes at most 100 explicit files, bounds
output to 100 findings per file, and uses the exit codes defined in
`SKILL.md`. It supports `--self-test` for the bundled fixtures.

Supported rules are reversed links (`MD011`), empty links (`MD042`), invalid
local fragments (`MD051`), undefined references (`MD052`), and duplicate
reference definitions (`MD053`). Review-only exclusions are defined in
[Validation](../SKILL.md#validation).
