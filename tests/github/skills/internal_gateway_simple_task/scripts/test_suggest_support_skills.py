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
    ".github/skills/internal-demo/references/usage.md",
    ".github/skills/internal-yaml/SKILL.md",
    ".github/skills/internal-yaml/references/example.md",
    ".github/skills/internal-yaml/scripts/helper.py",
    ".github/scripts/tool.py",
    "src/app.py",
    "tools/check.py",
    "scripts/demo.sh",
    "bin/check.sh",
    "infra/main.tf",
    "services/api/main.go",
    "src/index.ts",
    "package.json",
    "pom.xml",
    "src/main/java/App.java",
    "Makefile",
    "docs/guide.md",
    "data/registry.json",
    "azure-pipelines.yml",
    ".github/CODEOWNERS",
    ".github/workflows/ci.yml",
    ".github/actions/test/action.yml",
    "Dockerfile",
    "compose.yaml",
    "k8s/app/deployment.yaml",
    "config/app.yaml",
    "config/app.json",
    "src/payment_lambda.py",
)

EXPECTED_SKILLS_BY_PATH = {
    ".github/skills/internal-demo/SKILL.md": {"internal-skill-creator"},
    ".github/agents/internal-demo.agent.md": {"internal-agent-creator"},
    ".github/skills/internal-demo/references/usage.md": {"internal-skill-creator"},
    ".github/skills/internal-yaml/SKILL.md": {"internal-skill-creator"},
    ".github/skills/internal-yaml/references/example.md": {"internal-skill-creator"},
    ".github/skills/internal-yaml/scripts/helper.py": {"internal-skill-creator"},
    ".github/scripts/tool.py": {"internal-script-python"},
    "src/app.py": {"internal-project-python"},
    "tools/check.py": {"internal-python"},
    "scripts/demo.sh": {"internal-script-bash"},
    "bin/check.sh": {"internal-bash"},
    "infra/main.tf": {"internal-terraform"},
    "services/api/main.go": {"internal-go"},
    "src/index.ts": {"internal-project-nodejs"},
    "package.json": {"internal-nodejs"},
    "pom.xml": {"internal-java"},
    "src/main/java/App.java": {"internal-project-java"},
    "Makefile": {"internal-makefile"},
    "docs/guide.md": {"internal-markdown"},
    "data/registry.json": {"internal-json"},
    "azure-pipelines.yml": {"internal-azure-devops"},
    ".github/CODEOWNERS": {"internal-github-governance"},
    ".github/workflows/ci.yml": {"internal-github-actions"},
    ".github/actions/test/action.yml": {"internal-github-action-composite"},
    "Dockerfile": {"internal-docker"},
    "compose.yaml": {"internal-docker"},
    "k8s/app/deployment.yaml": {"internal-kubernetes"},
    "config/app.yaml": {"internal-yaml"},
    "config/app.json": {"internal-json"},
    "src/payment_lambda.py": {"internal-aws-lambda"},
}

EXPECTED_PATH_SKILLS = {skill for skills in EXPECTED_SKILLS_BY_PATH.values() for skill in skills}

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


def test_suggest_support_skills_prefers_single_narrowest_owner_per_path() -> None:
    module = load_script_module()

    for path_text, expected_skills in EXPECTED_SKILLS_BY_PATH.items():
        suggestions: dict[str, set[str]] = {}

        module.suggest_for_path(path_text, suggestions)

        assert set(suggestions) == expected_skills


def test_suggest_support_skills_keeps_simple_yaml_edit_on_yaml_owner_only() -> None:
    module = load_script_module()
    suggestions: dict[str, set[str]] = {}

    module.suggest_for_path("config/app.yaml", suggestions)

    assert set(suggestions) == {"internal-yaml"}


def test_suggest_support_skills_keeps_generic_json_edit_on_json_owner_only() -> None:
    module = load_script_module()
    suggestions: dict[str, set[str]] = {}

    module.suggest_for_path("config/app.json", suggestions)

    assert set(suggestions) == {"internal-json"}


def test_suggest_support_skills_keeps_generic_python_and_bash_on_base_owner_only() -> None:
    module = load_script_module()

    python_suggestions: dict[str, set[str]] = {}
    bash_suggestions: dict[str, set[str]] = {}

    module.suggest_for_path("tools/check.py", python_suggestions)
    module.suggest_for_path("bin/check.sh", bash_suggestions)

    assert set(python_suggestions) == {"internal-python"}
    assert set(bash_suggestions) == {"internal-bash"}


def test_suggest_support_skills_routes_bundle_siblings_to_skill_creator() -> None:
    module = load_script_module()

    for path_text in (
        ".github/skills/internal-yaml/SKILL.md",
        ".github/skills/internal-yaml/references/example.md",
        ".github/skills/internal-yaml/scripts/helper.py",
    ):
        suggestions: dict[str, set[str]] = {}

        module.suggest_for_path(path_text, suggestions)

        assert set(suggestions) == {"internal-skill-creator"}


def test_suggest_support_skills_keeps_generic_markdown_on_markdown_owner_only() -> None:
    module = load_script_module()
    suggestions: dict[str, set[str]] = {}

    module.suggest_for_path("docs/guide.md", suggestions)

    assert set(suggestions) == {"internal-markdown"}


def test_suggest_support_skills_routes_internal_agent_paths_to_agent_creator() -> None:
    module = load_script_module()
    suggestions: dict[str, set[str]] = {}

    module.suggest_for_path(".github/agents/internal-demo.agent.md", suggestions)

    assert set(suggestions) == {"internal-agent-creator"}


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
