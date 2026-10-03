import subprocess
from pathlib import Path

import pytest

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)


def run_shell(command: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-lc", command, "test-runner", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_resolve_script_handles_current_catalog_and_debug_log_tools() -> None:
    result = run_shell(
        "source ./.github/tools/run.sh; "
        "printf '%s\\n' \"$(resolve_script build-inventory)\"; "
        "printf '%s\\n' \"$(resolve_script analyze_copilot_debug_log)\"; "
        "printf '%s\\n' \"$(resolve_script sync_home_ai_resources)\""
    )
    assert result.returncode == 0
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert lines[0].endswith(".github/tools/inventory/build-inventory.py")
    assert lines[1].endswith(".github/skills/local-copilot-log-analyzer/scripts/run.sh")
    assert lines[2].endswith(
        ".github/skills/local-agent-sync-install-ai-resources/scripts/run.sh"
    )


@pytest.mark.parametrize("tool", ["adapt_critical_report", "validate_full_analysis"])
def test_resolve_script_rejects_removed_idea_tools(tool: str) -> None:
    result = run_shell('source ./.github/tools/run.sh; resolve_script "$1"', tool)
    assert result.returncode == 1
    assert result.stdout == ""


def test_resolve_script_handles_protected_skill_scope_validator() -> None:
    result = run_shell(
        "source ./.github/tools/run.sh; resolve_script validate-skill-change-scope"
    )
    assert result.returncode == 0
    assert result.stdout.strip().endswith(
        ".github/tools/skills/validate-skill-change-scope.py"
    )
