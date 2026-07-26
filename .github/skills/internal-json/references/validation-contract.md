# JSON validation contract

Run the checker with Python 3.10 or newer and explicit JSON paths:

```bash
python3 .github/skills/internal-json/scripts/check.py [--format text|json] FILE [FILE ...]
```

The script uses only the Python standard library and never installs
dependencies. It is read-only, checks at most 100 findings, and returns `0`
when checks passed within supported scope, `1` for format findings, and `2`
for usage, file, or internal failures. `--self-test` checks the bundled
fixtures.

Supported findings are `JSON_BOM`, `JSON_ENCODING`, `JSON_SYNTAX`,
`JSON_DUPLICATE_KEY`, `JSON_NON_FINITE`, `JSON_UNSAFE_INTEGER`,
`JSON_NUMBER_RANGE`, and `JSON_UNPAIRED_SURROGATE`. Integers must remain within
`[-9007199254740991, 9007199254740991]`; finite numbers must remain within the
IEEE-754 binary64 maximum magnitude.

The checker does not validate schemas, required properties, business meaning,
registry or organization rules, generated-content policy, or other domain
semantics. Route those concerns to the owning domain skill.
