from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml


def find_repo_root(start: Path) -> Path:
    for candidate in start.resolve().parents:
        if (candidate / "AGENTS.md").is_file():
            return candidate
    raise FileNotFoundError(f"Unable to find repository root from {start}")


REPO_ROOT = find_repo_root(Path(__file__))
SKILL_SCRIPTS_ROOT = (
    REPO_ROOT / ".github/skills/local-agent-sync-install-ai-resources/scripts"
)


def load_skill_module():
    inserted_path = False
    if SKILL_SCRIPTS_ROOT.as_posix() not in sys.path:
        sys.path.insert(0, SKILL_SCRIPTS_ROOT.as_posix())
        inserted_path = True
    try:
        spec = importlib.util.spec_from_file_location(
            "_test_local_home_syncing",
            SKILL_SCRIPTS_ROOT / "home_syncing.py",
        )
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        if inserted_path:
            sys.path.remove(SKILL_SCRIPTS_ROOT.as_posix())


home_syncing = load_skill_module()
apply_home_sync_plan = home_syncing.apply_home_sync_plan
build_home_sync_plan = home_syncing.build_home_sync_plan
parse_targets = home_syncing.parse_targets


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def initialize_source_repo(root: Path) -> None:
    write_file(root / "AGENTS.md", "# AGENTS\n")
    write_file(
        root / ".github/skills/demo-skill/SKILL.md",
        "---\n"
        "name: demo-skill\n"
        "description: Use when a demo home-sync skill is needed.\n"
        "---\n\n"
        "# Demo Skill\n\n"
        "## When to use\n\n"
        "- Use when a demo home-sync skill is needed.\n",
    )
    write_file(
        root / ".github/skills/demo-skill/agents/openai.yaml",
        "interface:\n"
        '  display_name: "Demo Skill"\n'
        '  short_description: "Portable demo skill bundle"\n'
        '  default_prompt: "Use $demo-skill for demo work."\n',
    )
    write_file(
        root
        / ".github/skills/local-agent-sync-install-ai-resources/references/runtime-support-matrix.yaml",
        "version: 1\n"
        "rows:\n"
        "  - target: codex\n"
        "    resource_family: skills\n"
        "    support_level: Documented\n"
        "    home_path: ~/.codex/skills/<skill>/\n"
        "    direct_copy_possible: true\n"
        "    translation_required: false\n"
        "    include_in_v1: true\n"
        "    evidence: []\n"
        "    notes: Codex direct-copy skill support.\n"
        "  - target: opencode\n"
        "    resource_family: skills\n"
        "    support_level: User-provided / To verify\n"
        "    home_path: ~/.config/opencode/skills/<skill>/\n"
        "    direct_copy_possible: true\n"
        "    translation_required: false\n"
        "    include_in_v1: false\n"
        "    evidence: []\n"
        "    notes: Undocumented support.\n",
    )
    write_file(
        root
        / ".github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml",
        "version: 1\n"
        "defaults:\n"
        "  include_internal_skills: false\n"
        "  include_local_skills: false\n"
        "  include_unlisted_skills: false\n"
        "resources:\n"
        "  - resource_id: demo-skill\n"
        "    source_family: skills\n"
        "    source_path: .github/skills/demo-skill\n"
        "    include_targets:\n"
        "      - codex\n"
        "      - opencode\n"
        "    target_support: Documented\n"
        "    notes: Demo bundle.\n",
    )


def test_parse_targets_normalizes_known_values_and_rejects_unknowns() -> None:
    assert parse_targets(" opencode, codex , codex ") == ("codex", "opencode")
    assert parse_targets("all") == ("codex", "copilot", "claude", "opencode")

    with pytest.raises(ValueError, match="unknown-target"):
        parse_targets("codex,unknown")


def test_build_home_sync_plan_blocks_unmanaged_targets_and_docs_unverified_apply(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)

    unmanaged_target = home_root / ".agents/skills/demo-skill"
    write_file(unmanaged_target / "SKILL.md", "# unmanaged\n")

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex,opencode"),
        mode="apply",
    )
    operation_codes = {
        operation.code for operation in plan.operations if operation.code
    }

    assert "target-exists-unmanaged" in operation_codes
    assert "docs-unverified" in operation_codes


def test_apply_home_sync_plan_creates_missing_dirs_with_flag_and_writes_manifest(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    write_file(
        source_root / ".github/skills/demo-skill/scripts/.venv/marker.txt", "runtime\n"
    )
    write_file(
        source_root / ".github/skills/demo-skill/__pycache__/demo.pyc", "runtime\n"
    )
    write_file(
        source_root / ".github/skills/demo-skill/.pytest_cache/CACHEDIR.TAG",
        "runtime\n",
    )

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="apply",
    )

    with pytest.raises(RuntimeError, match="needs-directory-create"):
        apply_home_sync_plan(plan)

    manifest_path = apply_home_sync_plan(plan, create_missing_dirs=True)
    copied_skill = home_root / ".agents/skills/demo-skill/SKILL.md"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert copied_skill.is_file()
    assert not (home_root / ".agents/skills/demo-skill/scripts/.venv").exists()
    assert not (home_root / ".agents/skills/demo-skill/__pycache__").exists()
    assert not (home_root / ".agents/skills/demo-skill/.pytest_cache").exists()
    assert manifest["targets"] == ["codex"]
    assert manifest["managed_resources"][0]["resource_id"] == "demo-skill"


def test_skill_bundle_sync_scripts_can_load_bundled_references(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    write_file(source_root / "AGENTS.md", "# AGENTS\n")
    write_file(
        source_root / ".github/skills/demo-skill/SKILL.md",
        "---\n"
        "name: demo-skill\n"
        "description: Use when a demo home-sync skill is needed.\n"
        "---\n\n"
        "# Demo Skill\n\n"
        "## When to use\n\n"
        "- Use when a demo home-sync skill is needed.\n",
    )

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="plan",
    )

    assert plan.source_resources_considered >= 1


def test_stale_manifest_path_escapes_home_is_blocked(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="apply",
    )
    manifest_path = apply_home_sync_plan(plan, create_missing_dirs=True)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["managed_resources"][0]["target_path"] = "/tmp/escaped/path"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    catalog_path = (
        source_root
        / ".github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml"
    )
    catalog_path.write_text(
        "version: 1\n"
        "defaults:\n"
        "  include_internal_skills: false\n"
        "  include_local_skills: false\n"
        "  include_unlisted_skills: false\n"
        "resources: []\n",
        encoding="utf-8",
    )

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="apply",
        prune_managed=True,
    )
    blocked_ops = [op for op in plan.operations if op.action == "blocked"]
    assert any(
        op.code in {"unsafe-home-path", "symlink-not-allowed"} for op in blocked_ops
    )


def test_stale_managed_content_drift_blocks_delete(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="apply",
    )
    manifest_path = apply_home_sync_plan(plan, create_missing_dirs=True)

    copied_skill = home_root / ".agents/skills/demo-skill/SKILL.md"
    copied_skill.write_text("# drifted content\n", encoding="utf-8")

    catalog_path = (
        source_root
        / ".github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml"
    )
    catalog_path.write_text(
        "version: 1\n"
        "defaults:\n"
        "  include_internal_skills: false\n"
        "  include_local_skills: false\n"
        "  include_unlisted_skills: false\n"
        "resources: []\n",
        encoding="utf-8",
    )

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="apply",
        prune_managed=True,
    )
    blocked_ops = [op for op in plan.operations if op.action == "blocked"]
    assert any(op.code == "stale-content-drifted" for op in blocked_ops)


def test_doctor_checks_include_agent_roots(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)

    checks, blocked_codes = home_syncing.run_doctor(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
    )

    codex_checks = [c for c in checks if c.get("name") == "target-root:codex"]
    assert len(codex_checks) == 2
    paths = {c["path"] for c in codex_checks}
    assert any(".agents/skills" in p for p in paths)
    assert any(".codex/agents" in p for p in paths)


def test_triple_apply_skip_plan_sequence_is_convergent(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)

    plan1 = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="apply",
    )
    manifest_path = apply_home_sync_plan(plan1, create_missing_dirs=True)
    manifest1 = json.loads(manifest_path.read_text(encoding="utf-8"))

    plan2 = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="apply",
    )
    manifest_path2 = apply_home_sync_plan(plan2)
    manifest2 = json.loads(manifest_path2.read_text(encoding="utf-8"))

    plan3 = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="plan",
    )
    skip_ops = [op for op in plan3.operations if op.action == "skip"]
    assert len(skip_ops) == 1

    assert (
        manifest1["managed_resources"][0]["content_hash"]
        == manifest2["managed_resources"][0]["content_hash"]
    )


def test_home_sync_plan_includes_internal_graphify_when_present_in_source(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    write_file(
        source_root / ".github/skills/internal-graphify/SKILL.md",
        "---\nname: internal-graphify\n---\n\n# Internal Graphify\n",
    )
    write_file(
        source_root / ".github/skills/internal-graphify/agents/openai.yaml",
        "interface:\n  display_name: Internal Graphify\n",
    )

    catalog_path = (
        source_root
        / ".github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml"
    )
    catalog_path.write_text(
        "version: 1\n"
        "defaults:\n"
        "  include_internal_skills: false\n"
        "  include_local_skills: false\n"
        "  include_unlisted_skills: false\n"
        "resources:\n"
        "  - resource_id: demo-skill\n"
        "    source_family: skills\n"
        "    source_path: .github/skills/demo-skill\n"
        "    include_targets:\n"
        "      - codex\n"
        "  - resource_id: internal-graphify\n"
        "    source_family: skills\n"
        "    source_path: .github/skills/internal-graphify\n"
        "    include_targets:\n"
        "      - codex\n",
        encoding="utf-8",
    )

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="plan",
    )

    resource_ids = {
        op.resource_id for op in plan.operations if hasattr(op, "resource_id")
    }
    planned_paths = {op.path for op in plan.operations if hasattr(op, "path")}

    assert "internal-graphify" in resource_ids or any(
        ".agents/skills/internal-graphify" in str(op.path) for op in plan.operations
    )


def test_removed_source_bundle_becomes_stale_managed_instead_of_source_missing(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="apply",
    )
    apply_home_sync_plan(plan, create_missing_dirs=True)

    skill_dir = source_root / ".github/skills/demo-skill"
    for path in sorted(skill_dir.rglob("*"), reverse=True):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()
    skill_dir.rmdir()

    plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex"),
        mode="apply",
        prune_managed=True,
    )
    codes = {op.code for op in plan.operations if op.code}
    delete_paths = {op.path for op in plan.operations if op.action == "delete"}

    assert "source-missing" not in codes
    assert str(home_root / ".agents/skills/demo-skill") in delete_paths


def test_apply_can_retire_selected_targets_without_touching_remaining_targets(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    home_root = tmp_path / "home"
    initialize_source_repo(source_root)
    monkeypatch.setattr(
        home_syncing,
        "translate_agent_for_target",
        lambda source_path, target, config_path=None: f"# translated for {target}\n",
    )

    support_matrix_path = (
        source_root
        / ".github/skills/local-agent-sync-install-ai-resources/references/runtime-support-matrix.yaml"
    )
    support_matrix_path.write_text(
        "version: 1\n"
        "rows:\n"
        "  - target: codex\n"
        "    resource_family: skills\n"
        "    support_level: Documented\n"
        "    home_path: ~/.agents/skills/<skill>/\n"
        "    direct_copy_possible: true\n"
        "    translation_required: false\n"
        "    include_in_v1: true\n"
        "    evidence: []\n"
        "    notes: Codex direct-copy skill support.\n"
        "  - target: copilot\n"
        "    resource_family: skills\n"
        "    support_level: Documented\n"
        "    home_path: ~/.agents/skills/<skill>/\n"
        "    direct_copy_possible: true\n"
        "    translation_required: false\n"
        "    include_in_v1: true\n"
        "    evidence: []\n"
        "    notes: Copilot direct-copy skill support.\n"
        "  - target: claude\n"
        "    resource_family: skills\n"
        "    support_level: Documented\n"
        "    home_path: ~/.agents/skills/<skill>/\n"
        "    direct_copy_possible: true\n"
        "    translation_required: false\n"
        "    include_in_v1: true\n"
        "    evidence: []\n"
        "    notes: Claude direct-copy skill support.\n"
        "  - target: codex\n"
        "    resource_family: agents\n"
        "    support_level: Documented\n"
        "    home_path: ~/.codex/agents/<agent>.md\n"
        "    direct_copy_possible: false\n"
        "    translation_required: true\n"
        "    include_in_v1: true\n"
        "    evidence: []\n"
        "    notes: Codex agent translation support.\n"
        "  - target: copilot\n"
        "    resource_family: agents\n"
        "    support_level: Documented\n"
        "    home_path: ~/.copilot/agents/<agent>.md\n"
        "    direct_copy_possible: true\n"
        "    translation_required: false\n"
        "    include_in_v1: true\n"
        "    evidence: []\n"
        "    notes: Copilot agent direct-copy support.\n"
        "  - target: claude\n"
        "    resource_family: agents\n"
        "    support_level: Documented\n"
        "    home_path: ~/.claude/agents/<agent>.md\n"
        "    direct_copy_possible: false\n"
        "    translation_required: true\n"
        "    include_in_v1: true\n"
        "    evidence: []\n"
        "    notes: Claude agent translation support.\n",
        encoding="utf-8",
    )
    catalog_path = (
        source_root
        / ".github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml"
    )
    catalog_path.write_text(
        "version: 1\n"
        "defaults:\n"
        "  include_internal_skills: false\n"
        "  include_local_skills: false\n"
        "  include_unlisted_skills: false\n"
        "resources:\n"
        "  - resource_id: demo-skill\n"
        "    source_family: skills\n"
        "    source_path: .github/skills/demo-skill\n"
        "    include_targets:\n"
        "      - codex\n"
        "      - copilot\n"
        "      - claude\n"
        "    target_support: Documented\n"
        "    notes: Demo bundle.\n",
        encoding="utf-8",
    )
    agent_path = source_root / ".github/agents/demo.agent.md"
    write_file(
        agent_path,
        "---\nname: demo\ndescription: Demo agent.\n---\n\n# Demo agent\n",
    )
    catalog_payload = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    catalog_payload["resources"].append(
        {
            "resource_id": "demo",
            "source_family": "agents",
            "source_path": ".github/agents/demo.agent.md",
            "include_targets": ["codex", "copilot", "claude"],
            "target_support": "Documented",
            "notes": "Demo agent.",
        }
    )
    catalog_path.write_text(
        yaml.safe_dump(catalog_payload, sort_keys=False), encoding="utf-8"
    )

    initial_plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex,copilot,claude"),
        mode="apply",
    )
    manifest_path = apply_home_sync_plan(initial_plan, create_missing_dirs=True)

    retire_plan = build_home_sync_plan(
        source_root=source_root,
        home_root=home_root,
        targets=parse_targets("codex,copilot"),
        retired_targets=parse_targets("claude"),
        mode="apply",
        prune_managed=True,
    )
    apply_home_sync_plan(retire_plan, prune_managed=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["targets"] == ["codex", "copilot"]
    assert not (home_root / ".claude/agents/demo.md").exists()
    assert (home_root / ".copilot/agents/demo.agent.md").is_file()
    assert (home_root / ".agents/skills/demo-skill").is_dir()
    assert all(entry["target"] != "claude" for entry in manifest["managed_resources"])


def test_home_sync_catalog_contains_internal_graphify_in_real_repo() -> None:
    catalog_path = (
        REPO_ROOT
        / ".github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml"
    )
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    resource_ids = {r["resource_id"] for r in catalog.get("resources", [])}
    assert "internal-graphify" in resource_ids


def test_home_sync_catalog_contains_internal_ai_resource_review_in_real_repo() -> None:
    catalog_path = (
        REPO_ROOT
        / ".github/skills/local-agent-sync-install-ai-resources/references/home-sync-catalog.yaml"
    )
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    resource_ids = {r["resource_id"] for r in catalog.get("resources", [])}
    assert "internal-ai-resource-review" in resource_ids
