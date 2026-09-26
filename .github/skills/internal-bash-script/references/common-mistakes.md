# Common Mistakes For Bash and POSIX `sh` Scripts

The dialect and portable minimum live in `SKILL.md`; the optional
`internal-bash` catalog covers them in depth. This table covers operator
entrypoints.

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Missing purpose or usage context | Operators cannot discover the entrypoint contract locally | Add a purpose header, usage examples, and `--help` |
| Building dynamic Bash commands as strings | Quoting and argument boundaries become fragile | Use arrays plus `printf` in the Bash branch; use carefully quoted scalar invocations in POSIX `sh` |
| Destructive commands without rerun safety | Repeated execution can corrupt state or surprise operators | Add `--dry-run` and make the mutation idempotent |
| A multi-function script with no `main` entrypoint | The starting point is not obvious and the script cannot be sourced for testing | Define `main` and call `main "$@"` as the last line |
| Executable statements placed between function definitions | Execution order becomes hard to follow and side effects run before the entrypoint | Keep top-level statements together below the function definitions |
| Rewriting parser or cleanup scaffolding from scratch | Operator UX and failure handling drift between scripts | Reuse the starter and helper patterns from `references/templates.md` |
