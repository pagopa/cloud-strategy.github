from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)


def test_no_removed_execute_plan_references() -> None:
    forbidden = (
        "done-*",
        "evidence-envelope.md",
        "completion-report.md",
        "<STATE>-plan-state.md",
        "Plan profile: compact",
        "Plan profile: extended",
    )
    paths = (REPO_ROOT / ".github/skills/internal-gateway-execute-plans",)
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
