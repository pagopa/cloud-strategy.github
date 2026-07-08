import subprocess
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)


def run_shell(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-lc", command],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_resolve_script_handles_validator_and_debug_log_tools() -> None:
    result = run_shell(
        "source ./.github/scripts/run.sh; "
        "printf '%s\\n' \"$(resolve_script validate_critical_output)\"; "
        "printf '%s\\n' \"$(resolve_script analyze_copilot_debug_log)\"; "
        "printf '%s\\n' \"$(resolve_script sync_home_ai_resources)\""
    )
    assert result.returncode == 0
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert lines[0].endswith(
        ".github/skills/internal-gateway-critical-master/scripts/validate_critical_output.py"
    )
    assert lines[1].endswith("tools/analyze_copilot_debug_log/run.sh")
    assert lines[2].endswith(
        ".github/skills/local-agent-sync-install-ai-resources/scripts/run.sh"
    )
