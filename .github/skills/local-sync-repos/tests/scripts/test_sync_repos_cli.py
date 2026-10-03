import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
CLI = REPO_ROOT / ".github/skills/local-sync-repos/scripts/sync_repos.py"


def _run_cli(
    command: str, source: Path, target: Path, output_format: str = "compact"
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            CLI.as_posix(),
            command,
            "--source-root",
            str(source),
            "--target-repo",
            str(target),
            "--format",
            output_format,
        ],
        capture_output=True,
        text=True,
    )


def test_plan_writes_only_target_tmp_plan(source_repo: Path, target_repo: Path) -> None:
    result = _run_cli("plan", source_repo, target_repo)
    assert result.returncode == 0
    assert (target_repo / "tmp/local-sync-repos.plan.md").is_file()
    assert not (target_repo / "AGENTS.md").exists()


def test_apply_requires_matching_saved_plan(
    source_repo: Path, target_repo: Path
) -> None:
    result = _run_cli("apply", source_repo, target_repo)
    assert result.returncode == 1
    assert "missing-plan" in result.stderr


def test_apply_blocks_dirty_managed_overlap(
    source_repo: Path, target_repo: Path
) -> None:
    _run_cli("plan", source_repo, target_repo)
    (target_repo / ".editorconfig").write_text("dirty\n", encoding="utf-8")
    result = _run_cli("apply", source_repo, target_repo)
    assert result.returncode == 1
    assert "dirty-managed-overlap" in result.stderr


def test_apply_converges_and_preserves_consumer_owned_files(
    source_repo: Path, target_repo: Path
) -> None:
    local_instruction = target_repo / ".github/instructions/local-team.instructions.md"
    local_agents = target_repo / "AGENTS.local.md"
    local_instruction.parent.mkdir(parents=True, exist_ok=True)
    local_instruction.write_bytes(b"local instruction\n")
    local_agents.write_bytes(b"local policy\n")
    _run_cli("plan", source_repo, target_repo)
    assert _run_cli("apply", source_repo, target_repo).returncode == 0
    second = _run_cli("plan", source_repo, target_repo, output_format="json")
    payload = json.loads(second.stdout)
    assert payload["managed_mutation_paths"] == []
    assert (target_repo / ".github/workflows/_pr-title.yml").read_bytes() == (
        source_repo / ".github/workflows/_pr-title.yml"
    ).read_bytes()
    assert (target_repo / ".vscode/settings.json").read_bytes() == (
        source_repo / ".vscode/settings.json"
    ).read_bytes()
    assert local_instruction.read_bytes() == b"local instruction\n"
    assert local_agents.read_bytes() == b"local policy\n"


def test_apply_rejects_stale_plan_fingerprint(
    source_repo: Path, target_repo: Path
) -> None:
    _run_cli("plan", source_repo, target_repo)
    (target_repo / ".editorconfig").write_text("changed\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(target_repo), "add", "-A"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(target_repo), "commit", "-m", "drift"],
        check=True,
        capture_output=True,
    )
    result = _run_cli("apply", source_repo, target_repo)
    assert result.returncode == 1
    assert "stale-plan" in result.stderr


def test_apply_deletes_target_only_non_local_instruction(
    source_repo: Path, target_repo: Path
) -> None:
    stale = target_repo / ".github/instructions/stale.instructions.md"
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text("stale\n", encoding="utf-8")
    _run_cli("plan", source_repo, target_repo)
    assert _run_cli("apply", source_repo, target_repo).returncode == 0
    assert not stale.exists()


def test_agents_local_is_create_once(
    source_repo: Path, target_repo: Path, agents_local_template: Path
) -> None:
    _run_cli("plan", source_repo, target_repo)
    assert _run_cli("apply", source_repo, target_repo).returncode == 0
    assert (
        target_repo / "AGENTS.local.md"
    ).read_bytes() == agents_local_template.read_bytes()
    (target_repo / "AGENTS.local.md").write_bytes(b"consumer-edit\n")
    _run_cli("plan", source_repo, target_repo)
    assert _run_cli("apply", source_repo, target_repo).returncode == 0
    assert (target_repo / "AGENTS.local.md").read_bytes() == b"consumer-edit\n"


def test_compact_format_reports_operation_counts(
    source_repo: Path, target_repo: Path
) -> None:
    result = _run_cli("plan", source_repo, target_repo, output_format="compact")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["operation_counts"] == {"by_action": {"create": 10}, "total": 10}


def test_converged_apply_removes_target_plan_file(
    source_repo: Path, target_repo: Path
) -> None:
    _run_cli("plan", source_repo, target_repo)
    plan_file = target_repo / "tmp/local-sync-repos.plan.md"
    assert plan_file.is_file()
    assert _run_cli("apply", source_repo, target_repo).returncode == 0
    assert not plan_file.exists()
