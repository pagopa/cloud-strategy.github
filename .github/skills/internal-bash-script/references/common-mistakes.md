# Common Mistakes For Bash and POSIX `sh` Scripts

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Leaving the dialect undeclared | Review rules and syntax choices become contradictory | Record the interpreter, execution environment, and POSIX baseline before choosing patterns |
| Silently changing `sh` to Bash | Deployment behavior and portability can change without approval | Preserve the declared interpreter or explicitly update the contract |
| Using Bash extensions under POSIX `sh` | Arrays, `[[ ]]`, and `local` are not portable POSIX `sh` syntax | Use scalar variables, `[ ]`, `test`, and POSIX control flow |
| Treating Bash invoked as `sh` as portability proof | One implementation does not represent each supported `sh` | Run syntax and behavior checks under every repository-supported `sh` implementation |
| Assuming `pipefail` on an unspecified `/bin/sh` | Many `/bin/sh` implementations do not provide it | Require an explicit POSIX.1-2024 baseline or avoid the option |
| Skipping dependency checks for required commands | Failures surface late and with weaker operator context | Check `command -v` before the first call |
| Building dynamic Bash commands as strings | Quoting and argument boundaries become fragile | Use arrays plus `printf` in the Bash branch; use carefully quoted scalar invocations in POSIX `sh` |
| Destructive commands without rerun safety | Repeated execution can corrupt state or surprise operators | Add `--dry-run` and make the mutation idempotent |
| Rewriting parser or cleanup scaffolding from scratch | Operator UX and failure handling drift between scripts | Reuse the starter and helper patterns from `references/templates.md` |
