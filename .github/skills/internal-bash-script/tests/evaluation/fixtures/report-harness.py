# Harness fixture for C-DIRECT-INVOCATION; not collected by pytest.
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).with_name("report.sh")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SCRIPT), *args], text=True, capture_output=True, check=False
    )


def check_help() -> None:
    result = run("--help")
    assert result.returncode == 0
    assert "Usage" in result.stdout
