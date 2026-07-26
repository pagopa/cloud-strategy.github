# Makefile validation contract

The bundle checker accepts explicit Makefile or `.mk` paths and runs
`checkmake` 0.3.2 with the bundled configuration. Install the pinned tool
without changing the repository:

```bash
go install github.com/checkmake/checkmake/cmd/checkmake@v0.3.2
```

The checker is read-only, emits at most 100 findings, and returns `0` when
checks passed within supported scope, `1` when the tool reports findings, and
`2` for usage, dependency, file, or internal failures. It supports
`--self-test` for the bundled fixtures and never invokes GNU Make or recipes.

At `checkmake` 0.3.2 the bundle uses the parser and Make-specific rule
families exposed by the tool, including `phonydeclared`, while configuring
`maxbodylength` to 100. The wrapper does not claim to validate `$`/`$$` intent,
parallelism, order-only prerequisites, recipe side effects, recursive Make,
or domain behavior; those remain human review concerns.
