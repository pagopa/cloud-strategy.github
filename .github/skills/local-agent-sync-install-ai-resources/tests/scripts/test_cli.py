import argparse
import json
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest
from home_syncing import HomeSyncOperation
from sync_home_ai_resources import install_auto_apply_blockers, parse_args

AGENTS_MD_RESOURCE = {
    "resource_id": "global-agents",
    "source_family": "agents-md",
    "source_path": "AGENTS.md",
    "include_targets": ["agents.md"],
    "target_support": "documented",
    "notes": "Portable global agent baseline.",
}
AGENTS_MD_ROW = {
    "target": "agents.md",
    "resource_family": "agents-md",
    "home_path": "~/.agents/AGENTS.md",
}
NO_SKILLS = {
    "include_internal_skills": False,
    "include_unlisted_skills": False,
    "skill_targets": [],
}
PORTABLE_AGENTS_MD = """# Global agent policy

Shared policy.

If `AGENTS.local.md` exists next to this file, load and apply it after this
baseline. If it does not exist, continue without error.
"""


def _agent_resource(resource_id: str, source_path: str, target: str) -> dict:
    return {
        "resource_id": resource_id,
        "source_family": "agents",
        "source_path": source_path,
        "include_targets": [target],
        "target_support": "documented",
        "notes": "test agent",
    }


def test_parse_args_rejects_removed_bisync_and_preserves_supported_modes() -> None:
    for command in ("sync", "plan", "apply", "audit", "doctor", "dry-run"):
        assert parse_args([command]).command == command

    with pytest.raises(SystemExit):
        parse_args(["bisync", "plan"])


def test_install_auto_apply_blockers_require_explicit_review() -> None:
    class DummyPlan:
        def __init__(self) -> None:
            self.operations = (
                HomeSyncOperation(
                    target="skills",
                    action="mkdir",
                    path="/tmp/home/.agents/skills",
                    reason="Missing runtime root.",
                ),
                HomeSyncOperation(
                    target="skills",
                    action="warning",
                    path="/tmp/home/.agents/skills/demo",
                    reason="Home drift persists.",
                    code="install-warning",
                ),
            )

        def blocked_codes(self) -> list[str]:
            return []

    blockers = install_auto_apply_blockers(
        DummyPlan(),
        argparse.Namespace(create_missing_dirs=False),
    )

    assert blockers == ["install-residual-drift", "needs-directory-create"]


def test_skill_run_sh_should_quiet_only_for_compact_modes(script_dir: Path) -> None:
    run_sh = (script_dir / "run.sh").resolve().as_posix()
    script = textwrap.dedent(
        f"""\
        source "{run_sh}"
        set +e
        should_quiet --format compact
        compact_status="$?"
        should_quiet --format text
        text_status="$?"
        printf '%s,%s\\n' "$compact_status" "$text_status"
        """
    )

    result = subprocess.run(
        ["bash", "-c", script],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == "0,1"


def test_temporary_home_sync_links_skills_preserves_home_only_and_copies_agents(
    tmp_path: Path, capsys, write_refs, run_cli
) -> None:
    write_refs(
        tmp_path,
        defaults={"excluded_skills": ["graphify"]},
        resources=[
            _agent_resource("demo-agent", ".github/agents/demo-agent.agent.md", "codex")
        ],
        rows=[
            {
                "target": "skills",
                "resource_family": "skills",
                "home_path": "~/.agents/skills/<skill>/",
            },
            {
                "target": "codex",
                "resource_family": "skills",
                "home_path": "~/.agents/skills/<skill>/",
            },
            {
                "target": "codex",
                "resource_family": "agents",
                "home_path": "~/.codex/agents/",
                "direct_copy_possible": False,
                "translation_required": True,
            },
        ],
    )
    source_skill = tmp_path / ".github/skills/demo"
    source_skill.mkdir(parents=True)
    (source_skill / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    for skill_id in ("graphify", "local-private"):
        skill = tmp_path / ".github/skills" / skill_id
        skill.mkdir()
        (skill / "SKILL.md").write_text(f"# {skill_id}\n", encoding="utf-8")
    agent = tmp_path / ".github/agents/demo-agent.agent.md"
    agent.parent.mkdir(parents=True)
    agent.write_text(
        "---\nname: demo-agent\ndescription: test\n---\nTest agent.\n", encoding="utf-8"
    )

    home = tmp_path / "home"
    divergent = home / ".agents/skills/demo"
    divergent.mkdir(parents=True)
    (divergent / "SKILL.md").write_text("# divergent\n", encoding="utf-8")
    for skill_id in ("graphify", "home-only"):
        skill = home / ".agents/skills" / skill_id
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(f"# {skill_id}\n", encoding="utf-8")
    common = ("--source-root", tmp_path, "--home-root", home, "--targets")

    assert run_cli("sync", *common, "skills,codex", "--create-missing-dirs") == 0

    target_skill = home / ".agents/skills/demo"
    assert target_skill.is_symlink()
    assert target_skill.resolve() == source_skill.resolve()
    assert (home / ".agents/skills/graphify/SKILL.md").is_file()
    assert (home / ".agents/skills/home-only/SKILL.md").is_file()
    assert (home / ".codex/agents/demo-agent.toml").is_file()
    (source_skill / "SKILL.md").write_text("# repo edit\n", encoding="utf-8")
    assert (target_skill / "SKILL.md").read_text(encoding="utf-8") == "# repo edit\n"
    (target_skill / "SKILL.md").write_text("# home write\n", encoding="utf-8")
    assert (source_skill / "SKILL.md").read_text(encoding="utf-8") == "# home write\n"

    shutil.rmtree(source_skill)
    assert run_cli("sync", *common, "skills,codex", "--create-missing-dirs") == 0
    capsys.readouterr()
    assert not target_skill.exists()
    assert not target_skill.is_symlink()
    for mode in ("plan", "audit", "doctor"):
        assert run_cli(mode, *common, "skills,codex") == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload.get("blocked_codes", []) == []
        assert payload["counts"]["linked"] == 0
        assert payload["counts"]["unlinked"] == 0
        assert payload["counts"]["blocked"] == 0
        assert payload["counts"]["residual"] == 0


def test_agents_md_sync_keeps_optional_local_reference_and_overwrites_home_copy(
    tmp_path: Path, capsys, write_refs, run_cli
) -> None:
    write_refs(
        tmp_path,
        defaults=NO_SKILLS,
        resources=[AGENTS_MD_RESOURCE],
        rows=[{**AGENTS_MD_ROW, "notes": "Portable global agent baseline."}],
    )
    (tmp_path / "AGENTS.md").write_text(PORTABLE_AGENTS_MD, encoding="utf-8")
    (tmp_path / "AGENTS.local.md").write_text(
        "# Repository-local policy\n\nRepository-only policy.\n",
        encoding="utf-8",
    )
    home = tmp_path / "home"
    target = home / ".agents/AGENTS.md"
    target.parent.mkdir(parents=True)
    target.write_text("old local policy\n", encoding="utf-8")

    exit_code = run_cli(
        "sync", "--source-root", tmp_path, "--home-root", home, "--targets", "agents.md"
    )
    capsys.readouterr()

    assert exit_code == 0
    assert target.read_text(encoding="utf-8") == PORTABLE_AGENTS_MD
    manifest = json.loads(
        (
            home / ".sync/cloud-strategy-governance/home-ai-resources/manifest.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["managed_resources"][0]["target"] == "agents.md"
    assert manifest["managed_resources"][0]["resource_family"] == "agents-md"


def test_agents_md_sync_accepts_missing_optional_local_policy(
    tmp_path: Path, capsys, write_refs, run_cli
) -> None:
    write_refs(
        tmp_path,
        defaults=NO_SKILLS,
        resources=[AGENTS_MD_RESOURCE],
        rows=[{**AGENTS_MD_ROW, "notes": "Portable global agent baseline."}],
    )
    (tmp_path / "AGENTS.md").write_text(PORTABLE_AGENTS_MD, encoding="utf-8")
    home = tmp_path / "home"
    (home / ".agents").mkdir(parents=True)

    exit_code = run_cli(
        "sync", "--source-root", tmp_path, "--home-root", home, "--targets", "agents.md"
    )
    capsys.readouterr()

    assert exit_code == 0
    assert (
        (home / ".agents/AGENTS.md")
        .read_text(encoding="utf-8")
        .endswith("If it does not exist, continue without error.\n")
    )


def test_copilot_agents_are_symlinked_with_write_through(
    tmp_path: Path, capsys, write_refs, run_cli
) -> None:
    write_refs(
        tmp_path,
        defaults={"skill_targets": ["copilot"]},
        resources=[
            _agent_resource(
                "demo-agent", ".github/agents/demo-agent.agent.md", "copilot"
            )
        ],
        rows=[
            {
                "target": "copilot",
                "resource_family": "agents",
                "home_path": "~/.copilot/agents/",
            }
        ],
    )
    source = tmp_path / ".github/agents/demo-agent.agent.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "---\nname: demo-agent\n---\nRepository agent.\n", encoding="utf-8"
    )
    home = tmp_path / "home"

    exit_code = run_cli(
        "sync",
        "--source-root",
        tmp_path,
        "--home-root",
        home,
        "--targets",
        "copilot",
        "--create-missing-dirs",
    )
    capsys.readouterr()

    assert exit_code == 0
    target = home / ".copilot/agents/demo-agent.agent.md"
    assert target.is_symlink()
    assert target.resolve() == source.resolve()
    source.write_text(
        "---\nname: demo-agent\n---\nUpdated in repository.\n", encoding="utf-8"
    )
    assert target.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")
    target.write_text(
        "---\nname: demo-agent\n---\nUpdated through home.\n", encoding="utf-8"
    )
    assert (
        source.read_text(encoding="utf-8")
        == "---\nname: demo-agent\n---\nUpdated through home.\n"
    )


@pytest.mark.parametrize(
    ("target", "source_path", "home_path", "home_file", "content", "updated"),
    [
        pytest.param(
            "codex",
            ".codex/agents/native-agent.toml",
            "~/.codex/agents/",
            ".codex/agents/native-agent.toml",
            'name = "native-agent"\nmodel = "gpt-5.6-luna"\n',
            'name = "native-agent"\nmodel = "gpt-5.6-luna-updated"\n',
            id="codex",
        ),
        pytest.param(
            "opencode",
            ".opencode/agents/native-agent.md",
            "~/.config/opencode/agents/",
            ".config/opencode/agents/native-agent.md",
            "---\ndescription: native opencode\nmode: subagent\n---\nNative body.\n",
            "---\ndescription: native opencode\nmode: subagent\n---\nUpdated body.\n",
            id="opencode",
        ),
    ],
)
def test_native_agent_is_symlinked_without_translation(
    tmp_path: Path,
    capsys,
    write_refs,
    run_cli,
    target: str,
    source_path: str,
    home_path: str,
    home_file: str,
    content: str,
    updated: str,
) -> None:
    write_refs(
        tmp_path,
        defaults=NO_SKILLS,
        resources=[_agent_resource("native-agent", source_path, target)],
        rows=[{"target": target, "resource_family": "agents", "home_path": home_path}],
    )
    source = tmp_path / source_path
    source.parent.mkdir(parents=True)
    source.write_text(content, encoding="utf-8")
    home = tmp_path / "home"

    exit_code = run_cli(
        "sync",
        "--source-root",
        tmp_path,
        "--home-root",
        home,
        "--targets",
        target,
        "--create-missing-dirs",
    )
    capsys.readouterr()

    assert exit_code == 0
    home_target = home / home_file
    assert home_target.is_symlink()
    assert home_target.resolve() == source.resolve()
    source.write_text(updated, encoding="utf-8")
    assert home_target.read_text(encoding="utf-8") == updated
