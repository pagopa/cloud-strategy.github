from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "AGENTS.md").is_file() and (parent / ".github").is_dir()
)
REFERENCE_PATTERN = re.compile(r"references/[A-Za-z0-9_.-]+\.md")


def test_import_bundle_is_standalone_and_owns_execution_assets(tmp_path: Path) -> None:
    source_bundle = REPO_ROOT / ".github/skills/internal-terraform-import"
    copied_bundle = tmp_path / "standalone" / "internal-terraform-import"
    shutil.copytree(source_bundle, copied_bundle)

    skill_text = (copied_bundle / "SKILL.md").read_text(encoding="utf-8")
    assert "internal-terraform" in skill_text
    assert "references/import-orchestration.md" in skill_text
    assert "references/aws-identity-center-import.md" in skill_text
    assert (copied_bundle / "scripts/import-manifest-runner.sh").is_file()
    assert (copied_bundle / "scripts/adoption_protocol.py").is_file()
    assert (copied_bundle / "scripts/resolve-aws-identity-center-import.sh").is_file()
    assert (copied_bundle / "tests/fixtures/imports.valid.jsonl").is_file()
    assert not (copied_bundle / "../internal-terraform/scripts/import-manifest-runner.sh").exists()

    for reference in REFERENCE_PATTERN.findall(skill_text):
        assert (copied_bundle / reference).is_file(), reference


def test_import_bundle_requires_explicit_invocation() -> None:
    metadata = (
        REPO_ROOT / ".github/skills/internal-terraform-import/agents/openai.yaml"
    ).read_text(encoding="utf-8")

    assert "allow_implicit_invocation: false" in metadata


def test_import_protocol_cli_runs_from_external_working_directory(tmp_path: Path) -> None:
    source_bundle = REPO_ROOT / ".github/skills/internal-terraform-import"
    protocol = source_bundle / "scripts/adoption_protocol.py"
    result = subprocess.run(
        [sys.executable, str(protocol), "classify-plan"],
        cwd=tmp_path,
        input=json.dumps({"actions": [{"address": "resource.example", "action": "no-op"}]}),
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout)["allowed"] is True
