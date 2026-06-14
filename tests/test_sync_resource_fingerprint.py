from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(
    ".github/skills/local-agent-sync-external-resources/scripts/sync_resource_fingerprint.py"
).resolve()


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def test_snapshot_writes_manifest_and_uses_relative_resource_ids(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    input_file = repo / "sample.txt"
    input_file.write_text("hello\n", encoding="utf-8")
    output_file = repo / "manifest.json"

    result = run_script(
        "snapshot",
        "sample.txt",
        "--root",
        str(repo),
        "--output",
        str(output_file),
        "--source-ref-base",
        "upstream/resources",
    )

    assert output_file.as_posix() in result.stdout
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    resource = payload["resources"][0]
    assert payload["hash_algo"] == "sha256"
    assert resource["resource_id"] == "sample.txt"
    assert resource["target_path"] == "sample.txt"
    assert resource["source_ref"] == "upstream/resources/sample.txt"


def test_diff_json_reports_created_removed_and_changed(tmp_path: Path) -> None:
    old_manifest = tmp_path / "old.json"
    new_manifest = tmp_path / "new.json"
    old_manifest.write_text(
        json.dumps(
            {
                "resources": [
                    {
                        "resource_id": "a.txt",
                        "source_hash": "111",
                        "content_hash": "111",
                    },
                    {
                        "resource_id": "b.txt",
                        "source_hash": "222",
                        "content_hash": "222",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    new_manifest.write_text(
        json.dumps(
            {
                "resources": [
                    {
                        "resource_id": "b.txt",
                        "source_hash": "333",
                        "content_hash": "333",
                    },
                    {
                        "resource_id": "c.txt",
                        "source_hash": "444",
                        "content_hash": "444",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = run_script(
        "diff",
        "--old",
        str(old_manifest),
        "--new",
        str(new_manifest),
        "--format",
        "json",
    )
    payload = json.loads(result.stdout)

    assert payload["summary"]["created"] == 1
    assert payload["summary"]["removed"] == 1
    assert payload["summary"]["changed"] == 1
