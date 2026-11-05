# Testing Recipes For Python Tools

Preserve the declared framework, runner, naming, and native test location. The
example below uses pytest with the importable `cli.py` from
[Layout and templates](layout-and-templates.md). Use equivalent framework-native
assertions when the repository already uses another framework.

## Two useful levels

Test imported decisions and parsing in process with explicit inputs. Retain a
small process suite for the documented invocation, module or launcher, stdout,
stderr, status, and actual file effects. A process test for every pure decision
adds cost without proving a new execution contract.

| Behavior | Meaningful checks |
| --- | --- |
| Arguments | Required value, invalid input, values containing spaces |
| Execution | Documented invocation, help, success, actionable failure |
| File output | Content and destination, refusal without modification |
| Repeatability | Rerun outcome, dry-run effects when supported |

Select cases from actual behavior. Mock true external I/O, keep orchestration
real, and assert independent results. Preserve executable permissions and the
actual launcher when testing their contract.

## Runnable example

Place this illustrative test beside `cli.py`; use the actual native layout in a
consumer repository. The template returns 1 for an explicitly empty target.

```python
import os
import subprocess
import sys
from pathlib import Path

import pytest

from cli import main


@pytest.mark.parametrize(
    ("argv", "expected"),
    [(["--target", "demo"], 0), (["--target", "name with spaces"], 0),
     (["--target", ""], 1)],
)
def test_target_controls_exit_status(argv, expected):
    assert main(argv) == expected


def test_missing_target_is_rejected():
    with pytest.raises(SystemExit) as error:
        main([])
    assert error.value.code == 2


def test_direct_python_invocation_reports_missing_argument(tmp_path):
    script = Path(__file__).with_name("cli.py")
    result = subprocess.run(
        [sys.executable, str(script)], cwd=tmp_path,
        env={"PATH": os.defpath, "HOME": str(tmp_path), "LC_ALL": "C"},
        capture_output=True, text=True, check=False, timeout=5,
    )
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "--target" in result.stderr
    assert result.stdout == ""
```

The example detects missing validation, an incorrect exit result, and a broken
entrypoint connection. File-producing tools additionally need assertions on
real temporary output and protected files; stdout alone cannot prove a write.

## Isolation and fast feedback

Give each case its own workspace and reset mutable state. For processes, control
relevant home, config, locale, timezone, and command lookup, retaining explicit
required platform variables. Capture output and bound execution time. A tool
that spawns descendants needs a harness that also owns their cleanup on timeout.

Run the focused test, component suite, relevant actual integration, then declared
runtime compatibility. Keep unavailable evidence visible. With pytest, measure
expensive cases using `--durations=10`; distinguish launcher setup from execution.
Compare equivalent commands and environments before claiming gains. Add shared
fixtures or parallelism only when measurement and isolation justify them.
