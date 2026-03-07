from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def copy_copilot_config(target_root: Path) -> None:
    shutil.copytree(REPO_ROOT / ".github", target_root / ".github")
    (target_root / "AGENTS.md").write_text((REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8"), encoding="utf-8")


def run_validator(repo_root: Path, report_file: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "bash",
            str(repo_root / ".github" / "scripts" / "validate-copilot-customizations.sh"),
            "--scope",
            "root",
            "--mode",
            "strict",
            "--report",
            "json",
            "--report-file",
            str(report_file),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_tech_ai_validator_writes_json_report_for_valid_repository(tmp_path: Path) -> None:
    target_root = tmp_path / "valid-repo"
    copy_copilot_config(target_root)

    report_file = tmp_path / "tech-ai-validator-report.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert payload["status"] == "passed"
    assert payload["failures"] == 0
    assert payload["warnings"] == 0


def test_tech_ai_validator_reports_missing_prompt_argument_hint(tmp_path: Path) -> None:
    target_root = tmp_path / "invalid-repo"
    copy_copilot_config(target_root)

    prompt_path = target_root / ".github" / "prompts" / "tech-ai-bash-script.prompt.md"
    prompt_lines = [
        line for line in prompt_path.read_text(encoding="utf-8").splitlines() if not line.startswith("argument-hint:")
    ]
    prompt_path.write_text("\n".join(prompt_lines) + "\n", encoding="utf-8")

    report_file = tmp_path / "tech-ai-validator-failure.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("Missing frontmatter key 'argument-hint'" in message for message in messages)


def test_tech_ai_validator_requires_root_agents_file(tmp_path: Path) -> None:
    target_root = tmp_path / "legacy-agents-repo"
    shutil.copytree(REPO_ROOT / ".github", target_root / ".github")
    (target_root / ".github" / "AGENTS.md").write_text("# Legacy AGENTS\n", encoding="utf-8")

    report_file = tmp_path / "tech-ai-validator-root-agents.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("AGENTS.md must live in repository root" in message for message in messages)
