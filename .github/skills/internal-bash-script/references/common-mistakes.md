# Common Mistakes For Bash and POSIX `sh` Scripts

The dialect and portable minimum live in `SKILL.md`; the optional
`internal-bash` catalog covers them in depth. This table covers operator
entrypoints.

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Missing or stale purpose/usage header | Operators cannot discover the entrypoint contract locally | Before completion, add an introductory purpose/usage header consistent with `--help`; include prerequisites, defaults, safety, and exit details proportional to risk, not boilerplate for trivial scripts |
| Building dynamic Bash commands as strings | Quoting and argument boundaries become fragile | Use arrays plus `printf` in the Bash branch; use carefully quoted scalar invocations in POSIX `sh` |
| Destructive commands without rerun safety | Repeated execution can corrupt state or surprise operators | Add `--dry-run` and make the mutation idempotent |
| A multi-function script with no clear entrypoint | The starting point is not obvious | Define `main` and invoke it at the execution boundary. An unconditional call still runs when sourced; test standalone scripts by invocation and source only helpers designed for it |
| Executable statements placed between function definitions | Execution order becomes hard to follow and side effects run before the entrypoint | Keep top-level statements together below the function definitions |
| Rewriting parser or cleanup scaffolding from scratch | Operator UX and failure handling drift between scripts | Reuse the starter and helper patterns from `references/templates.md` |
