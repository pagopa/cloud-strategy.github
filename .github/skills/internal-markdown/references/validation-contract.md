# Markdown validation contract

The bundle checker accepts explicit Markdown files and feeds each file through
standard input to `markdownlint-cli2` 0.22.1 with the bundled configuration.
Install the pinned tool without changing the repository:

```bash
npm install -g markdownlint-cli2@0.22.1
```

The checker is read-only, processes at most 100 explicit files, bounds output
to 100 findings per file, and returns `0` when checks passed within supported
scope, `1` for format findings, and `2` for usage, dependency, file, or
internal failures. It supports `--self-test` for the bundled fixtures.

Supported rules are reversed links (`MD011`), empty links (`MD042`), invalid
local fragments (`MD051`), undefined references (`MD052`), and duplicate
reference definitions (`MD053`). Markdown remains permissive: dialect choice,
external or local filesystem targets, editorial quality, and heading policy
are review-only and are not validated by this bundle.
