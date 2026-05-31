from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

SKILL_PATH = Path(".github/skills/internal-gateway-simple-task/SKILL.md")
SUPPORT_ROUTING_PATH = Path(
    ".github/skills/internal-gateway-simple-task/references/support-routing.md"
)
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

CLAIM_GATE_SYMPTOMS = {
    "bug",
    "tdd",
    "performance",
    "pr-readiness",
    "code-review",
    "no-findings",
    "systems-review",
    "completion-claim",
}


def load_script_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("suggest_support_skills", SCRIPT_PATH)

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def section_between(text: str, heading: str) -> str:
    section = text.split(heading, 1)[1]
    return section.split("\n## ", 1)[0]


def claim_gate_owners_from_skill(skill_text: str) -> set[str]:
    section = section_between(skill_text, "## Claim Gates")
    return set(re.findall(r"^- Load `([^`]+)` before", section, flags=re.MULTILINE))


def claim_gate_owners_from_reference(reference_text: str) -> set[str]:
    section = section_between(reference_text, "## Claim Gates")
    owners: set[str] = set()

    for line in section.splitlines():
        if not line.startswith("| "):
            continue

        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < 2:
            continue

        owner = cells[1]
        if owner.startswith("`") and owner.endswith("`"):
            owners.add(owner.strip("`"))

    return owners


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


def test_suggest_support_skills_claim_gate_owners_match_core_contract() -> None:
    module = load_script_module()
    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    reference_claim_gate_owners = claim_gate_owners_from_reference(
        SUPPORT_ROUTING_PATH.read_text(encoding="utf-8")
    )
    symptom_claim_gate_owners = {
        module.SYMPTOM_SKILLS[symptom][0] for symptom in CLAIM_GATE_SYMPTOMS
    }

    assert "single source of truth for claim-gate" in skill_text
    assert symptom_claim_gate_owners == reference_claim_gate_owners


def test_suggest_support_skills_normalizes_absolute_repo_owned_paths() -> None:
    module = load_script_module()
    suggestions: dict[str, set[str]] = {}

    module.suggest_for_path(str(SKILL_PATH.resolve()), suggestions)

    assert "internal-skill-creator" in suggestions
