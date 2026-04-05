from __future__ import annotations

from contextlib import contextmanager
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "INTERNAL_CONTRACT.md"
SYNC_MODULE_PATH = REPO_ROOT / ".github" / "scripts" / "internal-sync-copilot-configs.py"
VALIDATOR_MODULE_PATH = REPO_ROOT / ".github" / "scripts" / "validate-copilot-customizations.py"


def load_sync_module():
    module_name = "internal_sync_copilot_configs"
    spec = importlib.util.spec_from_file_location(module_name, SYNC_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_validator_module():
    module_name = "validate_copilot_customizations_for_contract_tests"
    spec = importlib.util.spec_from_file_location(module_name, VALIDATOR_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


SYNC_MODULE = load_sync_module()
VALIDATOR = load_validator_module()


@contextmanager
def validator_repo(root: Path):
    original_root = VALIDATOR.REPO_ROOT
    VALIDATOR.REPO_ROOT = root
    try:
        yield
    finally:
        VALIDATOR.REPO_ROOT = original_root


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_copilot_config(target_root: Path) -> None:
    shutil.copytree(REPO_ROOT / ".github", target_root / ".github")
    write_file(target_root / "AGENTS.md", (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8"))


def build_python_target(path: Path) -> None:
    write_file(path / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(path / "src" / "app.py", 'def main() -> None:\n    print("hello")\n')


def build_conflict_target(path: Path) -> None:
    build_python_target(path)
    write_file(path / "AGENTS.md", "# Manual AGENTS\n")
    write_file(path / "infra" / "main.tf", 'resource "null_resource" "infra" {}\n')


def build_finops_like_target(path: Path) -> None:
    write_file(path / ".github" / "PULL_REQUEST_TEMPLATE.md", "# PR template\n")
    write_file(path / ".github" / "workflows" / "ci.yml", "name: ci\non: [push]\njobs: {}\n")
    write_file(path / "Makefile", "help:\n\t@echo hi\n")
    write_file(path / "azure" / "rel" / "rel_finops.py", 'def main() -> None:\n    print("hello")\n')
    write_file(path / "azure" / "rel" / "rel_finops.sh", "#!/usr/bin/env bash\necho hi\n")
    write_file(path / "aws" / "dashboard" / "main.tf", 'resource "null_resource" "dashboard" {}\n')


def parse_tested_cases() -> list[str]:
    content = CONTRACT_PATH.read_text(encoding="utf-8").splitlines()
    cases: list[str] = []
    for line in content:
        if line.startswith("#### "):
            cases.append(line.removeprefix("#### ").strip().strip("`"))
    return cases


def parse_frontmatter_name(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return ""

    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return ""


def canonical_resource_identifier(path: Path) -> str:
    if path.name.endswith(".prompt.md"):
        return path.name[: -len(".prompt.md")]
    if path.name.endswith(".agent.md"):
        return path.name[: -len(".agent.md")]
    if path.name == "SKILL.md":
        return path.parent.name
    if path.name.endswith(".instructions.md"):
        return path.name[: -len(".instructions.md")]
    return ""


def extract_markdown_h2_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    inside_section = False
    collected: list[str] = []

    for line in lines:
        if re.match(r"^##\s+", line):
            if line.strip() == heading:
                inside_section = True
                collected = []
                continue
            if inside_section:
                break

        if inside_section:
            collected.append(line)

    if not inside_section:
        return None

    return "\n".join(collected).strip()


def extract_skill_list(text: str, heading: str) -> list[str] | None:
    section = extract_markdown_h2_section(text, heading)
    if section is None:
        return None

    declared_skills: list[str] = []
    for raw_line in section.splitlines():
        match = re.fullmatch(r"\s*-\s+`([^`]+)`\s*", raw_line)
        if match:
            declared_skills.append(match.group(1))

    return declared_skills


def has_standalone_identifier(text: str, identifier: str) -> bool:
    pattern = rf"(?<![a-z0-9-]){re.escape(identifier)}(?![a-z0-9-])"
    return re.search(pattern, text) is not None


def extract_internal_identifiers(text: str) -> list[str]:
    return sorted(
        {
            match.group(0).lower()
            for match in re.finditer(r"(?<![a-z0-9-])internal-[a-z0-9-]+(?![a-z0-9-])", text, re.IGNORECASE)
        }
    )


def retired_operational_reference_paths() -> list[Path]:
    paths: set[Path] = set()
    for relative_path in (
        Path("AGENTS.md"),
        Path(".github/copilot-instructions.md"),
        Path(".github/agents/README.md"),
    ):
        paths.add(REPO_ROOT / relative_path)

    for directory, pattern in (
        (REPO_ROOT / ".github" / "agents", "*.md"),
        (REPO_ROOT / ".github" / "prompts", "*.md"),
        (REPO_ROOT / ".github" / "instructions", "*.md"),
        (REPO_ROOT / ".github" / "skills", "*.md"),
    ):
        if not directory.exists():
            continue
        paths.update(directory.rglob(pattern))

    return sorted(path for path in paths if path.exists())


def resource_paths() -> list[Path]:
    paths = []
    paths.extend(sorted((REPO_ROOT / ".github" / "prompts").glob("*.prompt.md")))
    paths.extend(sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md")))
    paths.extend(sorted((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md")))
    paths.extend(sorted((REPO_ROOT / ".github" / "instructions").glob("*.instructions.md")))
    return paths


def has_supported_origin_prefix(identifier: str) -> bool:
    if identifier.startswith(("internal-", "local-")):
        return True
    return re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", identifier) is not None


def test_contract_cases_are_known() -> None:
    expected = {
        "resource-governance-uses-supported-origin-naming",
        "resource-governance-named-resources-declare-name",
        "resource-governance-agents-preferred-optional-skills-are-well-formed",
        "resource-governance-agent-preferred-optional-skills-resolve-on-disk",
        "resource-governance-canonical-operational-agents-publish-engine-contracts",
        "resource-governance-retired-operational-agents-do-not-regrow",
        "reporting-operation-completion-report-contract-is-documented",
        "reporting-sync-agents-publish-completion-report-categories",
        "sync-plan-regenerates-root-agents",
        "sync-plan-mirrors-source-catalog",
        "sync-plan-preserves-local-target-assets",
        "sync-plan-writes-tracking-file",
        "sync-apply-writes-manifest-and-agents",
        "sync-apply-mirrors-skill-support-files",
        "sync-apply-removes-tracking-file-when-complete",
        "sync-apply-keeps-tracking-file-for-local-follow-up",
    }
    assert set(parse_tested_cases()) == expected


def test_resource_governance_uses_supported_origin_naming() -> None:
    for path in resource_paths():
        identifier = canonical_resource_identifier(path)
        assert identifier, f"Missing canonical identifier for {path}"
        assert has_supported_origin_prefix(identifier), f"Unsupported resource origin prefix for {path}: {identifier}"


def test_resource_governance_named_resources_declare_name() -> None:
    named_resource_paths = []
    named_resource_paths.extend(
        sorted((REPO_ROOT / ".github" / "prompts").glob("internal-*.prompt.md"))
    )
    named_resource_paths.extend(
        sorted((REPO_ROOT / ".github" / "agents").glob("internal-*.agent.md"))
    )
    named_resource_paths.extend(
        sorted((REPO_ROOT / ".github" / "skills").glob("internal-*/SKILL.md"))
    )

    for path in named_resource_paths:
        identifier = canonical_resource_identifier(path)
        actual_name = parse_frontmatter_name(path)
        assert identifier, f"Missing canonical identifier for {path}"
        assert actual_name, f"Missing explicit name for {path}"
        assert actual_name == identifier, f"Resource name mismatch for {path}: {actual_name} != {identifier}"


def test_resource_governance_agents_preferred_optional_skills_are_well_formed() -> None:
    for path in sorted((REPO_ROOT / ".github" / "agents").glob("internal-*.agent.md")):
        content = path.read_text(encoding="utf-8")
        preferred_skills = extract_markdown_h2_section(content, "## Preferred/Optional Skills")

        assert "## Primary Skill Stack" not in content, f"Deprecated skill section heading still present in {path}"
        if preferred_skills is None:
            continue

        declared_skill_lines = [
            line
            for line in preferred_skills.splitlines()
            if re.fullmatch(r"\s*-\s+`[^`]+`\s*", line)
        ]
        assert declared_skill_lines, (
            f"Preferred/Optional Skills section must include at least one skill for {path}"
        )


def test_resource_governance_agent_preferred_optional_skills_resolve_on_disk() -> None:
    available_skills = {
        skill_path.parent.name for skill_path in sorted((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md"))
    }

    for path in sorted((REPO_ROOT / ".github" / "agents").glob("internal-*.agent.md")):
        content = path.read_text(encoding="utf-8")
        preferred_skills = extract_markdown_h2_section(content, "## Preferred/Optional Skills")
        if preferred_skills is None:
            continue

        for line in preferred_skills.splitlines():
            match = re.fullmatch(r"\s*-\s+`([^`]+)`\s*", line)
            if not match:
                continue
            skill_name = match.group(1)
            assert skill_name in available_skills, (
                f"Preferred or optional skill {skill_name} in {path} does not resolve to "
                ".github/skills/<name>/SKILL.md"
            )


def test_resource_governance_canonical_operational_agents_publish_engine_contracts() -> None:
    available_skills = {
        skill_path.parent.name
        for skill_path in sorted((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md"))
    }
    copilot_instructions_text = (REPO_ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")

    assert VALIDATOR.MANDATORY_ENGINE_BASELINE_POLICY_LINE in copilot_instructions_text

    for agent_name, expected_engine_skills in VALIDATOR.CANONICAL_OPERATIONAL_AGENT_ENGINES.items():
        path = REPO_ROOT / ".github" / "agents" / f"{agent_name}.agent.md"
        assert path.is_file(), f"Missing canonical operational agent {path}"

        text = path.read_text(encoding="utf-8")
        mandatory_engine_skills = extract_skill_list(text, VALIDATOR.MANDATORY_ENGINE_SECTION_HEADING)
        optional_support_skills = extract_skill_list(text, VALIDATOR.OPTIONAL_SUPPORT_SECTION_HEADING)

        assert mandatory_engine_skills is not None, f"Missing mandatory engine section in {path}"
        assert set(mandatory_engine_skills) == expected_engine_skills, (
            f"Unexpected mandatory engine skills in {path}: {mandatory_engine_skills}"
        )
        assert optional_support_skills, f"Missing optional support skills in {path}"
        assert VALIDATOR.PREFERRED_OPTIONAL_SECTION_HEADING not in text, (
            f"Canonical operational agent should not use legacy preferred/optional heading in {path}"
        )

        if agent_name == "internal-router":
            assert "## Escalation / Routing" in text, f"Missing routing section in {path}"
            escalation_section = extract_markdown_h2_section(text, VALIDATOR.ESCALATION_SECTION_HEADING)
            assert escalation_section is not None, f"Missing routing section in {path}"
            escalation_targets = extract_internal_identifiers(escalation_section)
            assert escalation_targets, f"Missing canonical routing targets in {path}"

            for target in escalation_targets:
                assert target in VALIDATOR.CANONICAL_OPERATIONAL_AGENT_ENGINES, (
                    f"Non-canonical routing target {target} found in {path}"
                )
                assert target != agent_name, f"Self-route {target} found in {path}"
                assert (REPO_ROOT / ".github" / "agents" / f"{target}.agent.md").is_file(), (
                    f"Routing target {target} missing on disk for {path}"
                )
        else:
            assert "## Escalation / Routing" not in text, (
                f"Non-router canonical agent must not publish routing targets in {path}"
            )
            boundary_section = extract_markdown_h2_section(text, VALIDATOR.BOUNDARY_SECTION_HEADING)
            assert boundary_section is not None, f"Missing boundary section in {path}"
            assert boundary_section.strip(), f"Empty boundary section in {path}"

        for skill_name in mandatory_engine_skills + optional_support_skills:
            assert skill_name in available_skills, (
                f"Skill {skill_name} in {path} does not resolve to .github/skills/<name>/SKILL.md"
            )


def test_resource_governance_retired_operational_agents_do_not_regrow() -> None:
    for retired_path in VALIDATOR.RETIRED_OPERATIONAL_AGENT_PATHS:
        assert not (REPO_ROOT / retired_path).exists(), f"Retired agent still exists: {retired_path}"

    for path in retired_operational_reference_paths():
        relative_path = path.relative_to(REPO_ROOT)
        if relative_path in VALIDATOR.ALLOWED_RETIRED_OPERATIONAL_REFERENCE_PATHS:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        for identifier in VALIDATOR.RETIRED_OPERATIONAL_AGENT_IDENTIFIERS:
            assert not has_standalone_identifier(text, identifier), (
                f"Stale retired operational agent reference {identifier} found in {relative_path}"
            )

        for pattern in VALIDATOR.RETIRED_CODE_REVIEW_AGENT_PATTERNS:
            assert pattern not in text, (
                f"Stale retired operational agent reference internal-code-review found in {relative_path}: {pattern}"
            )


def test_reporting_operation_completion_report_contract_is_documented() -> None:
    copilot_instructions_text = (REPO_ROOT / ".github" / "copilot-instructions.md").read_text(encoding="utf-8")
    agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    readme_text = (REPO_ROOT / ".github" / "README.md").read_text(encoding="utf-8")

    assert "## Operation Completion Report" in copilot_instructions_text
    assert "If a category was not used, explicitly say so and explain why." in copilot_instructions_text
    assert "Completion-report details live in `.github/copilot-instructions.md`" in agents_text
    assert "## Completion Report Contract" in readme_text

    for heading in (
        "### ✅ Outcome",
        "### 🤖 Agents",
        "### 📘 Instructions",
        "### 🧩 Skills",
    ):
        assert heading in copilot_instructions_text
        assert heading in readme_text


def test_reporting_sync_agents_publish_completion_report_categories() -> None:
    for path in (
        REPO_ROOT / ".github" / "agents" / "internal-sync-control-center.agent.md",
        REPO_ROOT / ".github" / "agents" / "internal-sync-global-copilot-configs-into-repo.agent.md",
    ):
        text = path.read_text(encoding="utf-8")
        assert "## Output Expectations" in text
        assert "If a category was not used, explicitly say so and explain why." in text
        for heading in (
            "### ✅ Outcome",
            "### 🤖 Agents",
            "### 📘 Instructions",
            "### 🧩 Skills",
        ):
            assert heading in text

    control_center_text = (
        REPO_ROOT / ".github" / "agents" / "internal-sync-control-center.agent.md"
    ).read_text(encoding="utf-8")
    assert "Governance files reviewed" in control_center_text


def test_sync_plan_regenerates_root_agents(tmp_path: Path) -> None:
    target_root = tmp_path / "conflict-target"
    build_conflict_target(target_root)

    plan, _planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)

    assert any(
        action.target_relative_path == "AGENTS.md" and action.status == "update"
        for action in plan.actions
    )


def test_sync_plan_mirrors_source_catalog(tmp_path: Path) -> None:
    target_root = tmp_path / "python-target"
    build_python_target(target_root)

    plan, _planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)

    assert plan.analysis.profile_name == "backend-python"
    assert plan.selection.instructions == SYNC_MODULE.source_asset_paths(REPO_ROOT, "instructions")
    assert plan.selection.prompts == SYNC_MODULE.source_asset_paths(REPO_ROOT, "prompts")
    assert plan.selection.skills == SYNC_MODULE.source_asset_paths(REPO_ROOT, "skills")
    assert plan.selection.agents == SYNC_MODULE.source_asset_paths(REPO_ROOT, "agents")
    assert plan.selection.supporting_files == SYNC_MODULE.source_skill_support_paths(REPO_ROOT)

    expected_engine_skill_paths = {
        f".github/skills/{skill_name}/SKILL.md"
        for skill_name in set().union(*VALIDATOR.CANONICAL_OPERATIONAL_AGENT_ENGINES.values())
    }
    assert expected_engine_skill_paths.issubset(set(plan.selection.preferred_skills))


def test_sync_plan_keeps_finops_like_selection_stack_specific(tmp_path: Path) -> None:
    target_root = tmp_path / "finops-target"
    build_finops_like_target(target_root)

    plan, _planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)

    assert plan.analysis.profile_name == "infrastructure-heavy"
    assert plan.selection.instructions == SYNC_MODULE.source_asset_paths(REPO_ROOT, "instructions")
    assert plan.selection.prompts == SYNC_MODULE.source_asset_paths(REPO_ROOT, "prompts")
    assert plan.selection.skills == SYNC_MODULE.source_asset_paths(REPO_ROOT, "skills")
    assert plan.selection.agents == SYNC_MODULE.source_asset_paths(REPO_ROOT, "agents")


def test_sync_plan_preserves_local_target_assets(tmp_path: Path) -> None:
    target_root = tmp_path / "manual-assets"
    build_python_target(target_root)
    custom_prompt_path = target_root / ".github" / "prompts" / "local-thing.prompt.md"
    custom_prompt_content = "manual prompt\n"
    write_file(custom_prompt_path, custom_prompt_content)

    plan, planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)

    assert not any(
        action.target_relative_path == ".github/prompts/local-thing.prompt.md" and action.status in {"delete", "update"}
        for action in plan.actions
    )

    SYNC_MODULE.apply_plan(target_root, plan, planned_files, REPO_ROOT)

    assert custom_prompt_path.is_file()
    assert custom_prompt_path.read_text(encoding="utf-8") == custom_prompt_content


def test_sync_plan_writes_tracking_file(tmp_path: Path) -> None:
    target_root = tmp_path / "tracking-plan"
    build_python_target(target_root)

    result = SYNC_MODULE.main(["--target", str(target_root)])

    tracking_path = target_root / SYNC_MODULE.PLAN_RELATIVE_PATH
    assert result == 0
    assert SYNC_MODULE.PLAN_RELATIVE_PATH.startswith("tmp/")
    assert tracking_path.parent == target_root / "tmp"
    assert tracking_path.parent.is_dir()
    assert tracking_path.is_file()
    tracking_text = tracking_path.read_text(encoding="utf-8")
    assert "## Pending synchronization actions" in tracking_text
    assert "## Pending validation checks" in tracking_text


def test_sync_apply_writes_manifest_and_agents(tmp_path: Path) -> None:
    target_root = tmp_path / "fresh-target"
    build_python_target(target_root)

    plan, planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)
    assert not any(action.status == "conflict" for action in plan.actions)

    SYNC_MODULE.apply_plan(target_root, plan, planned_files, REPO_ROOT)

    manifest_path = target_root / ".github" / "internal-sync-copilot-configs.manifest.json"
    agents_path = target_root / "AGENTS.md"
    assert manifest_path.is_file()
    assert agents_path.is_file()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["version"] == 2
    assert "AGENTS.md" in manifest["managed_files"]
    assert len(manifest["managed_files"]) > 1


def test_sync_apply_mirrors_skill_support_files(tmp_path: Path) -> None:
    target_root = tmp_path / "skill-support-target"
    build_python_target(target_root)

    plan, planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)
    support_file = ".github/skills/openai-gh-address-comments/assets/github.png"

    assert support_file in plan.selection.supporting_files

    SYNC_MODULE.apply_plan(target_root, plan, planned_files, REPO_ROOT)

    assert (target_root / support_file).read_bytes() == (REPO_ROOT / support_file).read_bytes()


def test_sync_apply_preserves_shell_wrapper_permissions(tmp_path: Path) -> None:
    target_root = tmp_path / "wrapper-permissions"
    build_python_target(target_root)

    plan, planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)
    SYNC_MODULE.apply_plan(target_root, plan, planned_files, REPO_ROOT)

    for relative_path in (
        ".github/scripts/internal-python-runner.sh",
        ".github/scripts/validate-copilot-customizations.sh",
    ):
        assert (target_root / relative_path).stat().st_mode & 0o111, f"{relative_path} should remain executable"


def test_sync_apply_removes_tracking_file_when_complete(tmp_path: Path) -> None:
    target_root = tmp_path / "tracking-complete"
    build_python_target(target_root)

    result = SYNC_MODULE.main(["--target", str(target_root), "--mode", "apply"])

    assert result == 0
    assert not (target_root / SYNC_MODULE.PLAN_RELATIVE_PATH).exists()


def test_sync_apply_keeps_tracking_file_for_local_follow_up(tmp_path: Path) -> None:
    target_root = tmp_path / "tracking-follow-up"
    build_python_target(target_root)
    write_file(
        target_root / ".github" / "prompts" / "local-broken.prompt.md",
        """---
description: Broken local prompt.
name: local-broken
---

# Local Broken
""",
    )

    result = SYNC_MODULE.main(["--target", str(target_root), "--mode", "apply"])

    tracking_path = target_root / SYNC_MODULE.PLAN_RELATIVE_PATH
    assert result == 0
    assert tracking_path.is_file()
    tracking_text = tracking_path.read_text(encoding="utf-8")
    assert "## Pending manual follow-up" in tracking_text
    assert ".github/prompts/local-broken.prompt.md" in tracking_text


def test_sync_apply_finops_like_target_passes_validation(tmp_path: Path) -> None:
    target_root = tmp_path / "finops-validated"
    build_finops_like_target(target_root)

    plan, planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)
    SYNC_MODULE.apply_plan(target_root, plan, planned_files, REPO_ROOT)

    with validator_repo(target_root):
        report = VALIDATOR.build_report("root", "strict")

    assert report.valid, "\n".join(report.errors)


def test_resource_governance_inventory_covers_catalog() -> None:
    inventory_paths = set(VALIDATOR.extract_inventory_paths())
    actual_paths = {
        str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        for path in resource_paths()
    }

    assert actual_paths <= inventory_paths


def test_resource_governance_repo_profiles_resolve_on_disk() -> None:
    repo_profiles_path = REPO_ROOT / ".github" / "repo-profiles.yml"
    for raw_line in repo_profiles_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.split("#", 1)[0].strip()
        if not stripped.startswith("- "):
            continue

        candidate = stripped[2:].strip().strip("\"'")
        if not candidate.startswith(("instructions/", "prompts/", "skills/")):
            continue

        assert (REPO_ROOT / ".github" / candidate).exists(), candidate


def test_resource_governance_obra_source_of_truth_matches_local_catalog() -> None:
    source_of_truth_path = REPO_ROOT / ".github" / "obra-superpowers-source-of-truth.json"
    source_of_truth = json.loads(source_of_truth_path.read_text(encoding="utf-8"))
    expected_mappings = {
        (entry["upstream"], entry["local"])
        for entry in source_of_truth["managed_skills"]
    }
    expected_locals = {local for _upstream, local in expected_mappings}
    actual_locals = {
        path.parent.name
        for path in sorted((REPO_ROOT / ".github" / "skills").glob("obra-*/SKILL.md"))
    }

    assert expected_locals == actual_locals

    control_center_text = (
        REPO_ROOT / ".github" / "agents" / "internal-sync-control-center.agent.md"
    ).read_text(encoding="utf-8")
    declared_mappings = set(
        VALIDATOR.extract_managed_skill_mappings(
            control_center_text,
            VALIDATOR.OBRA_MANAGED_RESOURCE_SECTION,
        )
        or []
    )

    assert expected_mappings == declared_mappings
