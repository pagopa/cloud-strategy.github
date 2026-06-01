# Common Mistakes For Bash Scripts

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Skipping dependency checks for required commands | Failures surface late and with weaker operator context | Check `command -v` before the first call |
| Building dynamic commands as strings | Quoting and argument boundaries become fragile | Use arrays plus `printf` for operator-facing formatting |
| Destructive commands without rerun safety | Repeated execution can corrupt state or surprise operators | Add `--dry-run` and make the mutation idempotent |
| Rewriting parser or cleanup scaffolding from scratch | Operator UX and failure handling drift between scripts | Reuse the starter and helper patterns from `references/templates.md` |
