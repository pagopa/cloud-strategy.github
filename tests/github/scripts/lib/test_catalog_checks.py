from __future__ import annotations

from pathlib import Path

from lib.catalog_checks import (
    apply_to_pattern_matches_target,
    collect_matching_instruction_paths,
)

INSTRUCTION_APPLY_TO = {
    ".github/instructions/awesome-copilot-azure-devops-pipelines.instructions.md": (
        "**/azure-pipelines.yml, **/azure-pipelines*.yml, **/*.pipeline.yml"
    ),
    ".github/instructions/awesome-copilot-go.instructions.md": "**/*.go,**/go.mod,**/go.sum",
    ".github/instructions/awesome-copilot-kubernetes-manifests.instructions.md": (
        "k8s/**/*.yaml,k8s/**/*.yml,manifests/**/*.yaml,manifests/**/*.yml,"
        "deploy/**/*.yaml,deploy/**/*.yml,charts/**/templates/**/*.yaml,"
        "charts/**/templates/**/*.yml"
    ),
    ".github/instructions/awesome-copilot-shell.instructions.md": "**/*.sh",
    ".github/instructions/internal-bash.instructions.md": "**/*.sh",
    ".github/instructions/internal-copilot-agent-authoring.instructions.md": (
        ".github/agents/internal-*.agent.md,.github/agents/local-*.agent.md"
    ),
    ".github/instructions/internal-copilot-skill-reference-authoring.instructions.md": (
        ".github/skills/internal-*/references/**/*.md,.github/skills/local-*/references/**/*.md"
    ),
    ".github/instructions/internal-docker.instructions.md": (
        "**/Dockerfile,**/Dockerfile.*,**/*.dockerfile,**/.dockerignore,"
        "**/docker-compose*.yml,**/docker-compose*.yaml,**/compose*.yml,**/compose*.yaml"
    ),
    ".github/instructions/internal-github-action-composite.instructions.md": "**/actions/**/action.y*ml",
    ".github/instructions/internal-github-actions.instructions.md": "**/workflows/**,**/actions/**/action.y*ml",
    ".github/instructions/internal-lambda.instructions.md": (
        "**/*lambda*.tf,**/*lambda*.py,**/*lambda*.js,**/*lambda*.ts"
    ),
    ".github/instructions/internal-markdown.instructions.md": "**/*.md",
    ".github/instructions/internal-nodejs.instructions.md": (
        "**/*.js,**/*.cjs,**/*.mjs,**/*.ts,**/*.tsx,**/package.json,**/tsconfig.json"
    ),
    ".github/instructions/internal-python.instructions.md": "**/*.py",
    ".github/instructions/internal-terraform.instructions.md": "**/*.tf",
    ".github/instructions/internal-yaml.instructions.md": "**/*.yml,**/*.yaml",
}


def write_instruction(root: Path, relative_path: str, apply_to: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ndescription: Test instruction\napplyTo: '{apply_to}'\n---\n",
        encoding="utf-8",
    )


def write_instruction_catalog(root: Path) -> None:
    for relative_path, apply_to in INSTRUCTION_APPLY_TO.items():
        write_instruction(root, relative_path, apply_to)


def test_apply_to_pattern_matches_target_treats_globstar_as_zero_or_more_directories() -> (
    None
):
    assert apply_to_pattern_matches_target("**/*.py", "lambda.py")
    assert apply_to_pattern_matches_target("**/*.py", "src/functions/lambda.py")
    assert apply_to_pattern_matches_target("k8s/**/*.yaml", "k8s/pod.yaml")
    assert apply_to_pattern_matches_target("k8s/**/*.yaml", "k8s/apps/payment/pod.yaml")


def test_collect_matching_instruction_paths_covers_realistic_sample_paths(
    tmp_path: Path,
) -> None:
    write_instruction_catalog(tmp_path)

    expected_by_target = {
        "src/payment_lambda.py": {
            ".github/instructions/internal-lambda.instructions.md",
            ".github/instructions/internal-python.instructions.md",
        },
        ".github/workflows/_pre-commit.yml": {
            ".github/instructions/internal-github-actions.instructions.md",
            ".github/instructions/internal-yaml.instructions.md",
        },
        ".github/actions/setup/action.yml": {
            ".github/instructions/internal-github-action-composite.instructions.md",
            ".github/instructions/internal-github-actions.instructions.md",
            ".github/instructions/internal-yaml.instructions.md",
        },
        "scripts/run.sh": {
            ".github/instructions/awesome-copilot-shell.instructions.md",
            ".github/instructions/internal-bash.instructions.md",
        },
        "azure-pipelines.yml": {
            ".github/instructions/awesome-copilot-azure-devops-pipelines.instructions.md",
            ".github/instructions/internal-yaml.instructions.md",
        },
        "k8s/pod.yaml": {
            ".github/instructions/awesome-copilot-kubernetes-manifests.instructions.md",
            ".github/instructions/internal-yaml.instructions.md",
        },
        "compose.yaml": {
            ".github/instructions/internal-docker.instructions.md",
            ".github/instructions/internal-yaml.instructions.md",
        },
        "config/settings.yaml": {".github/instructions/internal-yaml.instructions.md"},
        "docs/guide.md": {".github/instructions/internal-markdown.instructions.md"},
        ".github/agents/internal-review.agent.md": {
            ".github/instructions/internal-copilot-agent-authoring.instructions.md",
            ".github/instructions/internal-markdown.instructions.md",
        },
        ".github/skills/internal-demo/references/usage.md": {
            ".github/instructions/internal-copilot-skill-reference-authoring.instructions.md",
            ".github/instructions/internal-markdown.instructions.md",
        },
        "Dockerfile": {".github/instructions/internal-docker.instructions.md"},
        "infra/payment_lambda.tf": {
            ".github/instructions/internal-lambda.instructions.md",
            ".github/instructions/internal-terraform.instructions.md",
        },
        "package.json": {".github/instructions/internal-nodejs.instructions.md"},
        "tsconfig.json": {".github/instructions/internal-nodejs.instructions.md"},
        "services/api/main.go": {
            ".github/instructions/awesome-copilot-go.instructions.md"
        },
    }

    for target_path, expected_paths in expected_by_target.items():
        assert (
            set(collect_matching_instruction_paths(tmp_path, target_path))
            == expected_paths
        )
