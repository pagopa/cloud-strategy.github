import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").exists() and (parent / ".github").exists()
)
BUNDLE_ROOT = REPO_ROOT / ".github/skills/local-copilot-log-analyzer"


def test_bundle_runner_works_from_unrelated_working_directory(tmp_path: Path) -> None:
    bundle = tmp_path / "local-copilot-log-analyzer"
    shutil.copytree(BUNDLE_ROOT, bundle)
    outside = tmp_path / "outside"
    outside.mkdir()
    input_path = tmp_path / "events.jsonl"
    input_path.write_text(
        '{"type":"llm_request","sid":"isolated","attrs":{"inputTokens":3}}\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "bash",
            str(bundle / "scripts/run.sh"),
            "debug-logs",
            str(input_path),
        ],
        cwd=outside,
        env={**os.environ, "PYTHON_BIN": sys.executable},
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["aggregate"]["input_tokens"] == 3
    assert report["sessions"][0]["session_id"] == "isolated"
