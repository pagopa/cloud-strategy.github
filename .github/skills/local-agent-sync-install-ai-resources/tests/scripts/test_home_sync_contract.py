from pathlib import Path

from home_sync_contract import (
    discover_agent_resources,
    load_home_sync_catalog,
    load_home_sync_policy,
)


def test_live_catalog_scopes_native_paired_agents_to_owning_runtimes(
    repo_root: Path,
) -> None:
    resources = {
        resource.source_path: resource
        for resource in load_home_sync_catalog(repo_root)
        if resource.source_family == "agents"
    }

    assert resources[
        ".github/agents/internal-luna-executor.agent.md"
    ].include_targets == ("copilot",)
    assert resources[".codex/agents/internal-luna-executor.toml"].include_targets == (
        "codex",
    )
    assert resources[
        ".codex/agents/internal-gateway-critical-master.toml"
    ].include_targets == ("codex",)
    assert resources[
        ".github/agents/internal-gateway-critical-master.agent.md"
    ].include_targets == ("copilot",)
    assert resources[
        ".opencode/agents/internal-gateway-critical-master.md"
    ].include_targets == ("opencode",)


def test_agent_discovery_finds_native_codex_agents_only_for_codex(
    tmp_path: Path,
) -> None:
    copilot_root = tmp_path / ".github/agents"
    copilot_root.mkdir(parents=True)
    (copilot_root / "review.agent.md").write_text(
        "---\nname: review\n---\n", encoding="utf-8"
    )
    codex_root = tmp_path / ".codex/agents"
    codex_root.mkdir(parents=True)
    (codex_root / "native.toml").write_text('name = "native"\n', encoding="utf-8")
    opencode_root = tmp_path / ".opencode/agents"
    opencode_root.mkdir(parents=True)
    (opencode_root / "native.md").write_text(
        "---\ndescription: native opencode\n---\n", encoding="utf-8"
    )

    resources = discover_agent_resources(tmp_path)

    assert {
        resource["source_path"]: resource["include_targets"] for resource in resources
    } == {
        ".github/agents/review.agent.md": ["codex", "copilot", "opencode"],
        ".codex/agents/native.toml": ["codex"],
        ".opencode/agents/native.md": ["opencode"],
    }


def test_agent_discovery_excludes_local_agents_and_keeps_runtime_targets(
    tmp_path: Path, write_refs
) -> None:
    write_refs(
        tmp_path,
        catalog_text=(
            "version: 1\ndefaults:\n  include_unlisted_skills: false\nresources: []\n"
        ),
    )
    agents_root = tmp_path / ".github/agents"
    agents_root.mkdir(parents=True)
    (agents_root / "review.agent.md").write_text(
        "---\nname: review\n---\n", encoding="utf-8"
    )
    (agents_root / "local-review.agent.md").write_text(
        "---\nname: local-review\n---\n", encoding="utf-8"
    )

    resources = load_home_sync_catalog(tmp_path)

    assert [resource.source_path for resource in resources] == [
        ".github/agents/review.agent.md"
    ]
    assert resources[0].include_targets == ("codex", "copilot", "opencode")


def test_load_home_sync_catalog_autodiscovers_skills_and_honors_policy(
    tmp_path: Path, write_refs
) -> None:
    write_refs(
        tmp_path,
        defaults={
            "excluded_skills": ["graphify"],
            "skill_targets": ["codex", "copilot"],
        },
    )
    skills_root = tmp_path / ".github" / "skills"
    for skill_name in ("alpha-skill", "internal-gamma", "local-beta", "graphify"):
        skill_dir = skills_root / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill_name}\n", encoding="utf-8")

    policy = load_home_sync_policy(tmp_path)
    catalog = load_home_sync_catalog(tmp_path)

    assert policy.unmanaged_existing_skills_policy == "repo-wins"
    assert policy.excluded_skills == ("graphify",)
    assert {resource.resource_id for resource in catalog} == {
        "alpha-skill",
        "internal-gamma",
    }
    assert all(resource.include_targets == ("codex", "copilot") for resource in catalog)
