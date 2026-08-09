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


def test_resolve_script_handles_critical_report_adapter_and_debug_log_tools() -> None:
    result = run_shell(
        "source ./.github/scripts/run.sh; "
        "printf '%s\\n' \"$(resolve_script adapt_critical_report)\"; "
        "printf '%s\\n' \"$(resolve_script validate_full_analysis)\"; "
        "printf '%s\\n' \"$(resolve_script analyze_copilot_debug_log)\"; "
        "printf '%s\\n' \"$(resolve_script sync_home_ai_resources)\""
    )
    assert result.returncode == 0
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert lines[0].endswith(
        ".github/skills/internal-gateway-idea/scripts/critical_report_adapter.py"
    )
    assert lines[1] == lines[0]
    assert lines[2].endswith("tools/analyze_copilot_debug_log/run.sh")
    assert lines[3].endswith(
        ".github/skills/local-agent-sync-install-ai-resources/scripts/run.sh"
    )


def test_resolve_script_handles_protected_skill_scope_validator() -> None:
    result = run_shell(
        "source ./.github/scripts/run.sh; resolve_script validate_skill_change_scope"
    )
    assert result.returncode == 0
    assert result.stdout.strip().endswith(
        ".github/scripts/validate_skill_change_scope.py"
    )
