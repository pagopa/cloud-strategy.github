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


def test_tech_ai_validator_requires_local_prefix_for_repo_owned_assets(tmp_path: Path) -> None:
    target_root = tmp_path / "invalid-local-assets"
    copy_copilot_config(target_root)

    (target_root / ".github" / "prompts").mkdir(parents=True, exist_ok=True)
    (target_root / ".github" / "skills" / "user-admin").mkdir(parents=True, exist_ok=True)
    (target_root / ".github" / "prompts" / "add-external-user.prompt.md").write_text(
        "\n".join(
            [
                "---",
                "name: add-external-user",
                "description: Add an external user",
                "agent: agent",
                "argument-hint: user=<email>",
                "---",
                "",
                "# Add External User",
                "",
                "## Instructions",
                "1. Use `.github/skills/user-admin/SKILL.md`.",
                "",
                "## Validation",
                "- Validate the external user request.",
                "",
                "## Minimal example",
                "- Input: `user=guest@example.com`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (target_root / ".github" / "skills" / "user-admin" / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: user-admin",
                "description: Repository-local user administration workflow.",
                "---",
                "",
                "# User Admin",
                "",
                "## When to use",
                "- Manage repository-local user administration.",
                "",
                "## Validation",
                "- Validate repository-local access state.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report_file = tmp_path / "tech-ai-validator-local-prefix.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("Repository-local prompt filename must start with 'local-'" in message for message in messages)
    assert any("Repository-local prompt name must start with 'local-'" in message for message in messages)
    assert any("Repository-local skill directory must start with 'local-'" in message for message in messages)
    assert any("Repository-local skill name must start with 'local-'" in message for message in messages)


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


def test_tech_ai_validator_enforces_global_builder_semantic_sections(tmp_path: Path) -> None:
    target_root = tmp_path / "invalid-global-builder"
    copy_copilot_config(target_root)

    builder_path = target_root / ".github" / "agents" / "tech-ai-global-customization-builder.agent.md"
    builder_text = builder_path.read_text(encoding="utf-8").replace("## Token discipline", "## Token notes")
    builder_path.write_text(builder_text, encoding="utf-8")

    report_file = tmp_path / "tech-ai-validator-global-builder.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("Global customization builder missing '## Token discipline' section" in message for message in messages)


def test_root_agents_routes_customization_work_to_global_agents() -> None:
    agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "TechAIGlobalCustomizationBuilder" in agents_text
    assert "TechAIGlobalCustomizationAuditor" in agents_text
    assert "repo-only" in agents_text
    assert "## Available Skills" not in agents_text
    assert "## Available Prompts" not in agents_text


def test_global_builder_maps_consolidated_rules_and_legacy_auditor_is_deprecated() -> None:
    builder_text = (
        REPO_ROOT / ".github" / "agents" / "tech-ai-global-customization-builder.agent.md"
    ).read_text(encoding="utf-8")
    legacy_auditor_text = (
        REPO_ROOT / ".github" / "agents" / "tech-ai-customization-auditor.agent.md"
    ).read_text(encoding="utf-8")

    assert "AGENTS.md" in builder_text
    assert "copilot-instructions.md" in builder_text
    assert "copilot-code-review-instructions.md" in builder_text
    assert "security-baseline.md" in builder_text
    assert "DEPRECATION.md" in builder_text
    assert "validate-copilot-customizations.sh" in builder_text
    assert "Deprecated compatibility alias" in legacy_auditor_text
    assert "TechAIGlobalCustomizationAuditor" in legacy_auditor_text
