from pathlib import Path
import subprocess

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)


def test_make_completion_cli_exists() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text()
    expected = (
        ".github/skills/internal-gateway-execute-plans/"
        "scripts/plan_execution.py"
    )
    assert expected in makefile
    assert (REPO_ROOT / expected).is_file()


def test_no_live_legacy_execute_plan_references() -> None:
    forbidden = (
        "done-*",
        "evidence-envelope.md",
        "completion-report.md",
        "<STATE>-plan-state.md",
        "Plan profile: compact",
        "Plan profile: extended",
    )
    paths = (
        REPO_ROOT / ".github/skills/internal-gateway-execute-plans",
        REPO_ROOT
        / ".github/skills/internal-review-high-level/references/plan-completion-audit.md",
    )
    text_parts = []
    for path in paths:
        if path.is_file():
            text_parts.append(path.read_text(errors="replace"))
        elif path.is_dir():
            for item in path.rglob("*"):
                if item.is_file() and item.suffix in {".md", ".yaml", ".py"}:
                    text_parts.append(item.read_text(errors="replace"))
    text = "\n".join(text_parts)
    assert not any(marker in text for marker in forbidden)


def test_completion_make_target_reaches_bundle_cli(tmp_path: Path) -> None:
    plan_file = tmp_path / "plan.md"
    plan_file.write_text("# Plan\n")
    status_file = tmp_path / "plan.DONE.md"
    status_file.write_text("## Status\n`DONE`\n")
    result = subprocess.run(
        [
            "make",
            "retained-plan-check",
            f"PLAN_FILE={plan_file}",
            f"STATUS_FILE={status_file}",
            "PLAN_STAGE=completion",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    assert "can't open file" not in result.stderr
    assert "No such file or directory" not in result.stderr
