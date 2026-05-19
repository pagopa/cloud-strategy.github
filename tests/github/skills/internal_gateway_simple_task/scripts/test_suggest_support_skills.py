from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

SCRIPT_PATH = Path(
    ".github/skills/internal-gateway-simple-task/scripts/suggest_support_skills.py"
)

REPRESENTATIVE_PATHS = (
    ".github/skills/internal-demo/SKILL.md",
    ".github/agents/internal-demo.agent.md",
    ".github/instructions/demo.instructions.md",
    ".github/scripts/tool.py",
    "src/app.py",
    "scripts/demo.sh",
    "infra/main.tf",
    "src/index.ts",
    "pom.xml",
    ".github/workflows/ci.yml",
    ".github/actions/test/action.yml",
    "Dockerfile",
    "k8s/app/deployment.yaml",
)

EXPECTED_PATH_SKILLS = {
    "internal-skill-creator",
    "internal-agent-creator",
    "internal-copilot-instructions-creator",
    "internal-script-python",
    "internal-project-python",
    "internal-script-bash",
    "internal-terraform",
    "internal-project-nodejs",
    "internal-project-java",
    "internal-github-actions",
    "internal-github-action-composite",
    "internal-docker",
    "internal-kubernetes",
}

ALLOWLISTED_EXTERNAL_SKILLS: set[str] = set()


def load_script_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("suggest_support_skills", SCRIPT_PATH)

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def collect_emitted_skills(module: ModuleType) -> set[str]:
    suggestions: dict[str, set[str]] = {}

    for path_text in REPRESENTATIVE_PATHS:
        module.suggest_for_path(path_text, suggestions)

    emitted_skills = {skill for skill, _reason in module.SYMPTOM_SKILLS.values()}
    emitted_skills.update(suggestions)
    return emitted_skills


def test_suggest_support_skills_only_emits_live_skill_ids() -> None:
    module = load_script_module()
    emitted_skills = collect_emitted_skills(module)

    assert EXPECTED_PATH_SKILLS.issubset(emitted_skills)

    missing = sorted(
        skill_id
        for skill_id in emitted_skills
        if skill_id not in ALLOWLISTED_EXTERNAL_SKILLS
        and not Path(f".github/skills/{skill_id}/SKILL.md").is_file()
    )

    assert missing == []
