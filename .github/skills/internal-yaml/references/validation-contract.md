# YAML validation contract

The bundle checker accepts explicit `.yaml` and `.yml` files and uses
`yamllint` 1.38.0 with the bundled configuration. Install the pinned tool
without changing the repository:

```bash
pipx install yamllint==1.38.0
```

The checker is read-only and returns `0` when checks passed within supported
scope, `1` when the tool reports findings, and `2` for usage, dependency,
file, or internal failures. It bounds emitted findings to 100 and supports
`--self-test` for the bundled fixtures.

Supported checks are YAML parser syntax and duplicate mapping keys, including
the configured duplicate-merge-key behavior. Generic YAML success is not
platform-schema validation. Schema, custom-tag, CloudFormation, Kubernetes,
workflow, and domain-content checks are unsupported and must be routed to the
relevant owner.
