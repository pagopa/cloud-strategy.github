# Bundle Maintenance

Use this reference only when changing this bundle.

## Validation

Run from the bundle root:

```text
python3 -m pytest tests -q
python3 -m py_compile scripts/adoption_protocol.py
bash -n scripts/import-manifest-runner.sh
shellcheck -s bash scripts/import-manifest-runner.sh
```

The tests resolve every path from the bundle directory, so they also run from
a standalone copy of the bundle.

The live protocol tests must cover protocol-v2 handoff validation, complete
plan-action classification, import and state-move adoption, exact saved-plan
application, immutable records, and bundle portability.

## Single-entrypoint runner

The runner remains a single operator entrypoint by design. Runner and resource
adapters are sourced into the same Bash process, and the live lifecycle shares
trap cleanup, fail-closed exits, plan artifacts, authorization, evidence, and
receipt state. Splitting those stages would require a new cross-file state
contract and would make adapter injection and immutable-record ordering less
explicit. Keep the exception bounded: new provider or resource behavior must
remain in adapters, and a future lifecycle helper extraction must preserve the
bundle-local portability contract.

When the runner's usage text or adapter capability checks change, update the
`## Run` section of `SKILL.md` in the same change; the bundle tests compare
them.
