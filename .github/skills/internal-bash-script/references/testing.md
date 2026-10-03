# Python Tests For Operator Shell Scripts

Keep the existing Python framework and native component test location. This
stdlib unittest recipe demonstrates direct invocation of real shell code,
isolated files, and a controlled external command. Use framework-native
fixtures when the repository already provides them.

## Contents

- [Cases and levels](#cases-and-levels)
- [Runnable direct-invocation recipe](#runnable-direct-invocation-recipe)
- [Feedback and evidence](#feedback-and-evidence)

## Cases and levels

| Contract | Useful checks |
| --- | --- |
| Parser and guards | Help, missing value, invalid option, refusal without effects |
| Command construction | Argument boundaries and external failure propagation |
| Filesystem | Intended content or removal, protected paths unchanged |
| Operator safety | Dry-run has no mutation; repeated invocation is safe |
| Cleanup | Temporary state is removed after success and relevant failures |

Choose cases from the actual contract. Execute the documented invocation to
verify executable permissions and shebang resolution. An interpreter-only run
adds dialect evidence but does not replace the direct boundary. Source only
helpers explicitly designed for sourcing: wrapping code in `main` with an
unconditional final call still executes it on source.

## Runnable direct-invocation recipe

Place the test beside executable `tool.sh`, the bundled illustrative script at
[`cache-clean-valid.sh`](../tests/evaluation/fixtures/cache-clean-valid.sh).
The example copy must have executable permission. For a real target, test its
existing permission rather than silently repairing it in test setup.

```python
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).with_name("tool.sh")


class ScriptContractTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.cache = self.root / "cache space"
        self.target = self.cache / "dev [x]"
        self.target.mkdir(parents=True)
        self.marker = self.target / "keep.txt"
        self.marker.write_text("keep", encoding="utf-8")
        self.env = {"PATH": os.defpath, "HOME": str(self.root),
                    "LC_ALL": "C", "CACHE_ROOT": str(self.cache)}

    def run_tool(self, *args, env=None):
        return subprocess.run(
            [str(TOOL), *args], cwd=self.root,
            env=self.env if env is None else env,
            capture_output=True, text=True, check=False, timeout=5,
        )

    def test_dry_run_preserves_cache(self):
        result = self.run_tool("--env", "dev [x]", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, f"would remove {self.target}\n")
        self.assertEqual(self.marker.read_text(encoding="utf-8"), "keep")

    def test_cleanup_is_repeatable_and_keeps_neighbor(self):
        neighbor = self.cache / "protected"
        neighbor.mkdir()
        for _ in range(2):
            result = self.run_tool("--env", "dev [x]")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(self.target.exists())
            self.assertTrue(neighbor.is_dir())

    def test_missing_value_refuses_without_deletion(self):
        result = self.run_tool("--env")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--env", result.stderr)
        self.assertEqual(self.marker.read_text(encoding="utf-8"), "keep")

    def test_external_failure_preserves_status_and_arguments(self):
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        trace = self.root / "args.bin"
        stub = bin_dir / "rm"
        stub.write_text(
            "#!/bin/sh\n"
            + r'''printf '%s\0' "$@" > "$TRACE_FILE"'''
            + "\nexit 23\n",
            encoding="utf-8",
        )
        stub.chmod(0o755)
        env = dict(self.env, PATH=f"{bin_dir}{os.pathsep}{os.defpath}",
                   TRACE_FILE=str(trace))
        result = self.run_tool("--env", "dev [x]", env=env)
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertEqual(trace.read_bytes().split(b"\0")[:-1],
                         [b"-rf", b"--", os.fsencode(self.target)])
        self.assertEqual(self.marker.read_text(encoding="utf-8"), "keep")
```

The stub only records command input and supplies a failure. Python verifies the
real script's error propagation and command construction. The separate cleanup
case executes actual removal inside the disposable workspace. Assertions about
command arguments are justified here because safe command construction is the
contract; they do not establish production permissions or live service behavior.

## Feedback and evidence

Run the focused case first, then the component suite, relevant actual integration,
and declared shell compatibility. Preserve syntax and ShellCheck as separate
static evidence. Report missing interpreters and dependencies explicitly.

Keep mutable state per case; capture status, stdout, stderr, and effects. Control
home, config, locale, cwd, and command discovery. Bound execution and own cleanup
of spawned descendants where needed. Diagnose intermittent failures rather than
adding blanket retries. Measure comparable commands, environments, selected
cases, and setup costs before claiming speed gains or adding parallelism.
