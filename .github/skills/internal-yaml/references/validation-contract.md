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
`--self-test`, which runs every bundled valid and invalid fixture.

Supported checks are YAML parser syntax, duplicate mapping keys including the
configured duplicate-merge-key behavior, implicit boolean scalars, and implicit
or explicit octal values. Rules are configured at error level so findings stay
on exit code `1`. Mapping keys are excluded from the boolean check so platform
keys such as the workflow `on:` key are not reported. Generic YAML success is
not platform-schema validation. Schema, custom-tag, CloudFormation, Kubernetes,
workflow, and domain-content checks are unsupported and must be routed to the
relevant owner.
