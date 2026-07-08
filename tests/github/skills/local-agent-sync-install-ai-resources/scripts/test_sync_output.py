import json
import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
SCRIPT_DIR = (
    REPO_ROOT / ".github/skills/local-agent-sync-install-ai-resources/scripts"
)
sys.path.insert(0, SCRIPT_DIR.as_posix())

from sync_output import build_compact_install_output, dump_compact_json  # noqa: E402


def test_compact_install_output_is_single_line_and_bounded() -> None:
    payload = {
        "mode": "plan",
        "validation": "blocked",
        "selected_targets": ["skills", "codex"],
        "source_resources_considered": 2,
        "copied": ["/very/long/home/path/internal-one"],
        "skipped": ["skip-one"],
        "blocked": ["/very/long/home/path/internal-two"],
        "blocked_codes": ["target-exists-unmanaged"],
        "next_action": {
            "action": "resolve_blockers",
            "requires_explicit_approval": True,
        },
        "operations": [
            {
                "action": "copy",
                "path": "/very/long/home/path/internal-one",
                "resource_id": "internal-one",
                "reason": "verbose reason omitted from compact output",
            },
            {
                "action": "blocked",
                "path": "/very/long/home/path/internal-two",
                "resource_id": "internal-two",
                "code": "target-exists-unmanaged",
                "reason": "verbose reason omitted from compact output",
            },
        ],
    }

    compact = build_compact_install_output(payload)
    line = dump_compact_json(compact)

    assert "\n" not in line
    assert json.loads(line)["next"] == "resolve_blockers"
    assert compact["counts"]["blocked"] == 1
    assert compact["changes"] == [
        {"action": "copy", "resource": "internal-one"},
        {
            "action": "blocked",
            "code": "target-exists-unmanaged",
            "resource": "internal-two",
        },
    ]
