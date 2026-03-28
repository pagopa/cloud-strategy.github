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

    report_file = tmp_path / "internal-validator-report.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert payload["status"] in ("passed", "passed-with-warnings")
    assert payload["failures"] == 0


def test_tech_ai_validator_reports_missing_prompt_argument_hint(tmp_path: Path) -> None:
    target_root = tmp_path / "invalid-repo"
    copy_copilot_config(target_root)

    prompt_path = target_root / ".github" / "prompts" / "internal-bash-script.prompt.md"
    prompt_lines = [
        line for line in prompt_path.read_text(encoding="utf-8").splitlines() if not line.startswith("argument-hint:")
    ]
    prompt_path.write_text("\n".join(prompt_lines) + "\n", encoding="utf-8")

    report_file = tmp_path / "internal-validator-failure.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("Missing frontmatter key 'argument-hint'" in message for message in messages)


def test_tech_ai_validator_requires_supported_origin_prefix_for_repo_owned_assets(tmp_path: Path) -> None:
    target_root = tmp_path / "invalid-origin-assets"
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

    report_file = tmp_path / "internal-validator-origin-prefix.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("Repository-owned prompt filename must use a supported origin prefix" in message for message in messages)
    assert any("Repository-owned prompt name must use a supported origin prefix" in message for message in messages)
    assert any("Repository-owned skill directory must use a supported origin prefix" in message for message in messages)
    assert any("Repository-owned skill name must use a supported origin prefix" in message for message in messages)


def test_tech_ai_validator_accepts_supported_origin_prefixes_for_repo_owned_assets(tmp_path: Path) -> None:
    target_root = tmp_path / "valid-origin-assets"
    copy_copilot_config(target_root)

    (target_root / ".github" / "prompts").mkdir(parents=True, exist_ok=True)
    (target_root / ".github" / "agents").mkdir(parents=True, exist_ok=True)
    (target_root / ".github" / "skills" / "claude-docx").mkdir(parents=True, exist_ok=True)
    (target_root / ".github" / "prompts" / "claude-docx.prompt.md").write_text(
        "\n".join(
            [
                "---",
                "name: claude-docx",
                "description: Sync the Claude docx skill.",
                "agent: agent",
                "argument-hint: task=<summary>",
                "---",
                "",
                "# Claude DOCX",
                "",
                "## Instructions",
                "1. Use `.github/skills/claude-docx/SKILL.md`.",
                "",
                "## Validation",
                "- Validate the synchronized Claude skill metadata.",
                "",
                "## Minimal example",
                "- Input: `task=sync the skill`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (target_root / ".github" / "skills" / "claude-docx" / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: claude-docx",
                "description: Synced from an external Claude repository.",
                "---",
                "",
                "# Claude DOCX",
                "",
                "## When to use",
                "- Use when maintaining the synced Claude docx skill.",
                "",
                "## Validation",
                "- Validate synchronized upstream metadata.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (target_root / ".github" / "agents" / "local-agent-sync.agent.md").write_text(
        "\n".join(
            [
                "---",
                "name: local-agent-sync",
                "description: Handle local synchronization workflows.",
                'tools: ["search"]',
                "---",
                "",
                "# Local Agent Sync",
                "",
                "## Objective",
                "Keep local synchronization workflows aligned.",
                "",
                "## Restrictions",
                "- Keep repository-facing text in English.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report_file = tmp_path / "internal-validator-valid-origin-prefixes.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert payload["status"] in ("passed", "passed-with-warnings")
    assert not any("supported origin prefix" in message for message in messages)


def test_tech_ai_validator_requires_root_agents_file(tmp_path: Path) -> None:
    target_root = tmp_path / "legacy-agents-repo"
    shutil.copytree(REPO_ROOT / ".github", target_root / ".github")
    (target_root / ".github" / "AGENTS.md").write_text("# Legacy AGENTS\n", encoding="utf-8")

    report_file = tmp_path / "internal-validator-root-agents.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("AGENTS.md must live in repository root" in message for message in messages)


def test_tech_ai_validator_scope_all_covers_immediate_subrepos(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    copy_copilot_config(workspace_root)
    copy_copilot_config(workspace_root / "consumer-a")

    report_file = tmp_path / "internal-validator-all.json"
    result = run_validator(workspace_root, report_file, scope="all")

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert payload["status"] in ("passed", "passed-with-warnings")
    assert payload["scope"] == "all"


def test_tech_ai_validator_legacy_compatible_allows_legacy_prompt_conventions(tmp_path: Path) -> None:
    target_root = tmp_path / "legacy-compatible"
    copy_copilot_config(target_root)

    prompt_path = target_root / ".github" / "prompts" / "internal-bash-script.prompt.md"
    prompt_text = prompt_path.read_text(encoding="utf-8")
    prompt_text = prompt_text.replace("name: internal-bash-script\n", "")
    prompt_text = prompt_text.replace("argument-hint: action=<create|modify> script_name=<name> purpose=<purpose> [target_path=<path>] [target_file=<path>]\n", "")
    prompt_text = prompt_text.replace("---\n\n# Internal Bash Script", "mode: create\n---\n\n# Internal Bash Script")
    prompt_text = prompt_text.replace("## Validation\n", "## Legacy Validation\n")
    prompt_path.write_text(prompt_text, encoding="utf-8")

    report_file = tmp_path / "internal-validator-legacy-compatible.json"
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

    prompt_path = target_root / ".github" / "prompts" / "internal-python.prompt.md"
    prompt_path.write_text(
        prompt_path.read_text(encoding="utf-8").replace("---\n\n# Python Project Task", "\n# Python Project Task", 1),
        encoding="utf-8",
    )

    report_file = tmp_path / "internal-validator-malformed-frontmatter.json"
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

    report_file = tmp_path / "internal-validator-workflow-sha-comment.json"
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

    report_file = tmp_path / "internal-validator-workflow-docker-digest.json"
    result = run_validator(target_root, report_file)

    payload = json.loads(report_file.read_text(encoding="utf-8"))
    messages = [finding["message"] for finding in payload["findings"]]
    assert result.returncode == 1
    assert payload["status"] == "failed"
    assert any("Workflow docker reference is not pinned by digest" in message for message in messages)


def test_root_agents_routes_customization_work_to_global_and_local_customization_agents() -> None:
    agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "internal-sync-global-copilot-configs-into-repo" in agents_text
    assert ".github/instructions/internal-docker.instructions.md" in agents_text
    assert ".github/prompts/internal-docker.prompt.md" in agents_text
    assert ".github/skills/internal-docker/SKILL.md" in agents_text
    assert "repo-only" not in agents_text or "source-only" in agents_text
    assert "## Available Skills" not in agents_text
    assert "## Available Prompts" not in agents_text


def test_pinning_guidance_covers_hashes_modules_and_docker_digests() -> None:
    global_text = (REPO_ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
    python_text = (REPO_ROOT / ".github" / "instructions" / "internal-python.instructions.md").read_text(encoding="utf-8")
    terraform_text = (REPO_ROOT / ".github" / "instructions" / "internal-terraform.instructions.md").read_text(encoding="utf-8")
    docker_text = (REPO_ROOT / ".github" / "instructions" / "internal-docker.instructions.md").read_text(encoding="utf-8")

    assert "immutable dependency and image pins" in global_text
    assert "compiled `requirements.txt` with hashes" in python_text
    assert "Pin external module sources to exact versions or immutable refs" in terraform_text
    assert "Pin base images and runtime images by digest" in docker_text

