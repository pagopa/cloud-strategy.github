# Python Tests For Shell Helpers And Fragments

Keep the repository's Python framework. This recipe uses only stdlib unittest;
pytest can also collect it. Assertions remain in Python. Shell fixtures and
fixed invocation snippets exercise the real shell behavior.

## Contents

- [Choose the boundary](#choose-the-boundary)
- [Runnable helper recipe](#runnable-helper-recipe)
- [External commands and compatibility](#external-commands-and-compatibility)

## Choose the boundary

Source only helpers designed for sourcing. Execute fragments through their
declared interpreter; embedded shell also needs evidence from its owning format
when that integration changes. Pass inputs as process arguments, never as
interpolated source. Record the dialect and required implementation matrix.

| Behavior | Useful cases |
| --- | --- |
| Argument boundaries | Spaces, wildcard characters, empty values where valid |
| Failure propagation | External failure, refused input, partial output |
| File effects | Intended changes and protected state unchanged |
| Sourcing | Loading is safe; calling the function produces the result |

## Runnable helper recipe

Place the test beside `helper.bash`, the bundled illustrative helper at
[`list-files-valid.bash`](../tests/evaluation/fixtures/list-files-valid.bash).
Use the native component layout in a consumer repository.

```python
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HELPER = Path(__file__).with_name("helper.bash")
BASH = shutil.which("bash")


@unittest.skipUnless(BASH, "declared Bash interpreter is unavailable")
class HelperContractTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.env = {"PATH": os.defpath, "HOME": str(self.root), "LC_ALL": "C"}

    def test_sourcing_has_no_operator_output(self):
        result = subprocess.run(
            [BASH, "-c", '. "$1"', "helper-test", str(HELPER)],
            cwd=self.root, env=self.env, capture_output=True,
            text=True, check=False, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_empty_directory_has_no_logs(self):
        result = self.count_logs(self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "0\n")

    def test_paths_keep_spaces_and_wildcards_literal(self):
        directory = self.root / "logs ; literal"
        directory.mkdir()
        log = directory / "one [x] *.log"
        log.write_text("example", encoding="utf-8")
        result = self.count_logs(directory)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [f"log: {log}", "1"])
        self.assertEqual(log.read_text(encoding="utf-8"), "example")

    def count_logs(self, directory):
        return subprocess.run(
            [BASH, "-c", '. "$1"; count_logs "$2"',
             "helper-test", str(HELPER), str(directory)],
            cwd=self.root, env=self.env, capture_output=True,
            text=True, check=False, timeout=5,
        )
```

The quoted-path case rejects the bundled defective helper that loops over
`$(ls ...)`. The empty case detects unintended processing of an unmatched glob.
The source-only case checks the loading boundary without asserting source text.

## External commands and compatibility

Stub only real external boundaries with an executable in a temporary bin
folder. Put it first in PATH and give it explicit success or failure behavior.
Record arguments without shell assertions; validate them in Python only when
argument construction is the contract. A permissive stub does not prove real
command behavior. Keep focused actual integration where required.

Use isolated home, config, cwd, and explicit required environment variables.
Keep cleanup in Python even if the shell fails. Bound subprocess execution;
if descendants are possible, own process-group cleanup as well. A timeout is a
failure with diagnostics, not a success or silently retried case.

Run focused tests, the component suite, actual integration, and declared shell
implementations separately. Bash as sh does not prove POSIX portability. Missing
required implementations remain unverified. Measure equivalent commands and
setup costs before widening fixture scope or adding parallelism; preserve cases
that detect failures. Investigate intermittent behavior rather than hiding it.
