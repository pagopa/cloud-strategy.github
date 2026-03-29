from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "INTERNAL_CONTRACT.md"
SYNC_MODULE_PATH = REPO_ROOT / ".github" / "scripts" / "internal-sync-copilot-configs.py"


def load_sync_module():
    module_name = "internal_sync_copilot_configs"
    spec = importlib.util.spec_from_file_location(module_name, SYNC_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


SYNC_MODULE = load_sync_module()


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
            return line.split(":", 1)[1].strip().strip('"')
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


def resource_paths() -> list[Path]:
    paths = []
    paths.extend(sorted((REPO_ROOT / ".github" / "prompts").glob("*.prompt.md")))
    paths.extend(sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md")))
    paths.extend(sorted((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md")))
    paths.extend(sorted((REPO_ROOT / ".github" / "instructions").glob("*.instructions.md")))
    return paths


def has_supported_origin_prefix(identifier: str) -> bool:
    return identifier.startswith(("internal-", "local-", "claude-", "obra-", "terraform-"))


def test_contract_cases_are_known() -> None:
    expected = {
        "resource-governance-uses-supported-origin-naming",
        "resource-governance-named-resources-declare-name",
        "sync-plan-detects-root-agents-conflict",
        "sync-plan-selects-python-assets",
        "sync-plan-preserves-manual-target-assets",
        "sync-apply-writes-manifest-and-agents",
    }
    assert set(parse_tested_cases()) == expected


def test_resource_governance_uses_supported_origin_naming() -> None:
    for path in resource_paths():
        identifier = canonical_resource_identifier(path)
        assert identifier, f"Missing canonical identifier for {path}"
        assert has_supported_origin_prefix(identifier), f"Unsupported resource origin prefix for {path}: {identifier}"


def test_resource_governance_named_resources_declare_name() -> None:
    named_resource_paths = []
    named_resource_paths.extend(sorted((REPO_ROOT / ".github" / "prompts").glob("*.prompt.md")))
    named_resource_paths.extend(sorted((REPO_ROOT / ".github" / "agents").glob("*.agent.md")))
    named_resource_paths.extend(sorted((REPO_ROOT / ".github" / "skills").glob("*/SKILL.md")))

    for path in named_resource_paths:
        identifier = canonical_resource_identifier(path)
        actual_name = parse_frontmatter_name(path)
        assert identifier, f"Missing canonical identifier for {path}"
        assert actual_name, f"Missing explicit name for {path}"
        assert actual_name == identifier, f"Resource name mismatch for {path}: {actual_name} != {identifier}"


def test_sync_plan_detects_root_agents_conflict(tmp_path: Path) -> None:
    target_root = tmp_path / "conflict-target"
    build_conflict_target(target_root)

    plan, _planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)

    assert any(
        action.target_relative_path == "AGENTS.md" and action.status == "conflict"
        for action in plan.actions
    )


def test_sync_plan_selects_python_assets(tmp_path: Path) -> None:
    target_root = tmp_path / "python-target"
    build_python_target(target_root)

    plan, _planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)

    assert plan.analysis.profile_name == "backend-python"
    assert len(plan.selection.prompts) > 0


def test_sync_plan_preserves_manual_target_assets(tmp_path: Path) -> None:
    target_root = tmp_path / "manual-assets"
    build_python_target(target_root)
    custom_prompt_path = target_root / ".github" / "prompts" / "custom-thing.prompt.md"
    custom_prompt_content = "manual prompt\n"
    write_file(custom_prompt_path, custom_prompt_content)

    plan, planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)
    SYNC_MODULE.apply_plan(target_root, plan, planned_files, REPO_ROOT)

    assert custom_prompt_path.is_file()
    assert custom_prompt_path.read_text(encoding="utf-8") == custom_prompt_content


def test_sync_apply_writes_manifest_and_agents(tmp_path: Path) -> None:
    target_root = tmp_path / "fresh-target"
    build_python_target(target_root)

    plan, planned_files = SYNC_MODULE.build_plan(REPO_ROOT, target_root)
    assert not any(action.status == "conflict" for action in plan.actions if action.target_relative_path != "AGENTS.md")

    SYNC_MODULE.apply_plan(target_root, plan, planned_files, REPO_ROOT)

    manifest_path = target_root / ".github" / "internal-sync-copilot-configs.manifest.json"
    agents_path = target_root / "AGENTS.md"
    assert manifest_path.is_file()
    assert agents_path.is_file()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "AGENTS.md" in manifest["managed_files"]
    assert len(manifest["managed_files"]) > 1
