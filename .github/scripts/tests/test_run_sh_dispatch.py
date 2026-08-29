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


def test_resolve_script_handles_current_catalog_and_debug_log_tools() -> None:
    result = run_shell(
        "source ./.github/scripts/run.sh; "
        "printf '%s\\n' \"$(resolve_script build-inventory)\"; "
        "printf '%s\\n' \"$(resolve_script analyze_copilot_debug_log)\"; "
        "printf '%s\\n' \"$(resolve_script sync_home_ai_resources)\""
    )
    assert result.returncode == 0
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert lines[0].endswith(".github/scripts/build-inventory.py")
    assert lines[1].endswith(".github/skills/local-copilot-log-analyzer/scripts/run.sh")
    assert lines[2].endswith(
        ".github/skills/local-agent-sync-install-ai-resources/scripts/run.sh"
    )


def test_resolve_script_rejects_removed_idea_tools() -> None:
    result = run_shell(
        "source ./.github/scripts/run.sh; "
        "if resolve_script adapt_critical_report >/dev/null; then exit 1; fi; "
        "if resolve_script validate_full_analysis >/dev/null; then exit 1; fi"
    )
    assert result.returncode == 0


def test_resolve_script_handles_protected_skill_scope_validator() -> None:
    result = run_shell(
        "source ./.github/scripts/run.sh; resolve_script validate-skill-change-scope"
    )
    assert result.returncode == 0
    assert result.stdout.strip().endswith(
        ".github/scripts/validate-skill-change-scope.py"
    )
