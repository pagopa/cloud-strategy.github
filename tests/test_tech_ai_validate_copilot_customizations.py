from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def copy_copilot_config(target_root: Path) -> None:
    shutil.copytree(REPO_ROOT / ".github", target_root / ".github")
    (target_root / "AGENTS.md").write_text((REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8"), encoding="utf-8")


def run_validator(
    repo_root: Path,
    report_file: Path,
    *,
    scope: str = "root",
    mode: str = "strict",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "bash",
            str(repo_root / ".github" / "scripts" / "validate-copilot-customizations.sh"),
            "--scope",
            scope,
            "--mode",
            mode,
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


def test_tech_ai_validator_requires_internal_prefix_for_repo_owned_assets(tmp_path: Path) -> None:
    target_root = tmp_path / "invalid-internal-assets"
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
                "description: Repository-internal user administration workflow.",
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

    report_file = tmp_path / "tech-ai-validator-internal-prefix.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("Repository-internal prompt filename must start with 'internal-'" in message for message in messages)
    assert any("Repository-internal prompt name must start with 'internal-'" in message for message in messages)
    assert any("Repository-internal skill directory must start with 'internal-'" in message for message in messages)
    assert any("Repository-internal skill name must start with 'internal-'" in message for message in messages)


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

    builder_path = target_root / ".github" / "agents" / "tech-ai-standards-repo-config-builder.agent.md"
    builder_text = builder_path.read_text(encoding="utf-8").replace("## Token discipline", "## Token notes")
    builder_path.write_text(builder_text, encoding="utf-8")

    report_file = tmp_path / "tech-ai-validator-global-builder.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("Global customization builder missing '## Token discipline' section" in message for message in messages)


def test_tech_ai_validator_scope_all_covers_immediate_subrepos(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    copy_copilot_config(workspace_root)
    copy_copilot_config(workspace_root / "consumer-a")

    report_file = tmp_path / "tech-ai-validator-all.json"
    result = run_validator(workspace_root, report_file, scope="all")

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert payload["status"] == "passed"
    assert payload["scope"] == "all"


def test_tech_ai_validator_legacy_compatible_allows_legacy_prompt_conventions(tmp_path: Path) -> None:
    target_root = tmp_path / "legacy-compatible"
    copy_copilot_config(target_root)

    prompt_path = target_root / ".github" / "prompts" / "tech-ai-bash-script.prompt.md"
    prompt_text = prompt_path.read_text(encoding="utf-8")
    prompt_text = prompt_text.replace("name: TechAIBashScript\n", "")
    prompt_text = prompt_text.replace("argument-hint: action=<create|modify> script_name=<name> purpose=<purpose> [target_path=<path>] [target_file=<path>]\n", "")
    prompt_text = prompt_text.replace("---\n\n# TechAI Bash Script", "mode: create\n---\n\n# TechAI Bash Script")
    prompt_text = prompt_text.replace("## Validation\n", "## Legacy Validation\n")
    prompt_path.write_text(prompt_text, encoding="utf-8")

    report_file = tmp_path / "tech-ai-validator-legacy-compatible.json"
    result = run_validator(target_root, report_file, mode="legacy-compatible")

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert payload["status"] == "passed-with-warnings"
    assert payload["warnings"] > 0
    assert any("Legacy prompt key 'mode' found" in message for message in messages)


def test_tech_ai_validator_reports_malformed_frontmatter(tmp_path: Path) -> None:
    target_root = tmp_path / "malformed-frontmatter"
    copy_copilot_config(target_root)

    prompt_path = target_root / ".github" / "prompts" / "tech-ai-python.prompt.md"
    prompt_path.write_text(
        prompt_path.read_text(encoding="utf-8").replace("---\n\n# Python Project Task", "\n# Python Project Task", 1),
        encoding="utf-8",
    )

    report_file = tmp_path / "tech-ai-validator-malformed-frontmatter.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("malformed frontmatter fence" in message for message in messages)


def test_tech_ai_validator_requires_release_comment_for_workflow_sha_pins(tmp_path: Path) -> None:
    target_root = tmp_path / "workflow-sha-comment"
    copy_copilot_config(target_root)

    workflow_path = target_root / ".github" / "workflows" / "custom.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(
            [
                "name: custom",
                "on: push",
                "permissions:",
                "  contents: read",
                "jobs:",
                "  validate:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd",
                "",
            ]
        ),
        encoding="utf-8",
    )

    report_file = tmp_path / "tech-ai-validator-workflow-sha-comment.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("Workflow SHA pin is missing adjacent release URL comment" in message for message in messages)


def test_tech_ai_validator_requires_digest_for_workflow_docker_references(tmp_path: Path) -> None:
    target_root = tmp_path / "workflow-docker-digest"
    copy_copilot_config(target_root)

    workflow_path = target_root / ".github" / "workflows" / "custom.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(
            [
                "name: custom",
                "on: push",
                "permissions:",
                "  contents: read",
                "jobs:",
                "  validate:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: docker://alpine:3.21",
                "",
            ]
        ),
        encoding="utf-8",
    )

    report_file = tmp_path / "tech-ai-validator-workflow-docker-digest.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("Workflow docker reference is not pinned by digest" in message for message in messages)


def test_root_agents_routes_customization_work_to_global_and_local_customization_agents() -> None:
    agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "TechAIStandardsRepoConfigBuilder" in agents_text
    assert "TechAIStandardsRepoConfigAuditor" in agents_text
    assert "TechAIRepoCopilotExtender" in agents_text
    assert "TechAIDocker" in agents_text
    assert "repo-only" in agents_text
    assert "## Available Skills" not in agents_text
    assert "## Available Prompts" not in agents_text


def test_pinning_guidance_covers_hashes_modules_and_docker_digests() -> None:
    global_text = (REPO_ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
    python_text = (REPO_ROOT / ".github" / "instructions" / "python.instructions.md").read_text(encoding="utf-8")
    terraform_text = (REPO_ROOT / ".github" / "instructions" / "terraform.instructions.md").read_text(encoding="utf-8")
    docker_text = (REPO_ROOT / ".github" / "instructions" / "docker.instructions.md").read_text(encoding="utf-8")

    assert "compiled lock file with hashes" in global_text
    assert "compiled `requirements.txt` with hashes" in python_text
    assert "Pin external module sources to exact versions or immutable refs" in terraform_text
    assert "Pin base images and runtime images by digest" in docker_text


def test_global_builder_maps_consolidated_rules_and_legacy_auditor_is_deprecated() -> None:
    builder_text = (
        REPO_ROOT / ".github" / "agents" / "tech-ai-standards-repo-config-builder.agent.md"
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
    assert "TechAIStandardsRepoConfigAuditor" in legacy_auditor_text


def test_internal_builder_requires_grounding_against_concrete_target_files() -> None:
    agent_text = (
        REPO_ROOT / ".github" / "agents" / "tech-ai-repo-copilot-extender.agent.md"
    ).read_text(encoding="utf-8")
    prompt_text = (
        REPO_ROOT / ".github" / "prompts" / "tech-ai-repo-copilot-extender.prompt.md"
    ).read_text(encoding="utf-8")
    skill_text = (
        REPO_ROOT / ".github" / "skills" / "tech-ai-repo-copilot-extender" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "inspect concrete target files first" in agent_text
    assert "`Target evidence`" in agent_text
    assert "Inspect one or more concrete target files" in prompt_text
    assert "stop and report the missing grounding" in prompt_text
    assert "Identify at least one representative target file" in skill_text
    assert "do not invent fields, object shapes, identity suffixes, or naming conventions" in skill_text
