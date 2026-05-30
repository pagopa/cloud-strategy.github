from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def find_repo_root(start: Path) -> Path:
    for candidate in start.resolve().parents:
        if (candidate / "AGENTS.md").is_file():
            return candidate
    raise FileNotFoundError(f"Unable to find repository root from {start}")


REPO_ROOT = find_repo_root(Path(__file__))
SKILL_SCRIPTS_ROOT = (
    REPO_ROOT / ".github/skills/local-agent-sync-home-ai-resources/scripts"
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
        / ".github/skills/local-agent-sync-home-ai-resources/references/runtime-support-matrix.yaml",
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
        / ".github/skills/local-agent-sync-home-ai-resources/references/home-sync-catalog.yaml",
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
        / ".github/skills/local-agent-sync-home-ai-resources/references/home-sync-catalog.yaml"
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
        / ".github/skills/local-agent-sync-home-ai-resources/references/home-sync-catalog.yaml"
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
