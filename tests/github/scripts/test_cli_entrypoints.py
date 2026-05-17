from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path
from types import SimpleNamespace

import audit_copilot_catalog
import build_inventory
import check_catalog_consistency
import detect_token_risks
import github_catalog_validation
import sync_copilot_catalog
import validate_internal_skills


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def initialize_governance_repo(root: Path, *, with_inventory: bool = True) -> None:
    write_file(
        root / "AGENTS.md",
        "# AGENTS\n\n"
        "- Use `.github/copilot-instructions.md`.\n"
        "- Use `.github/INVENTORY.md`.\n",
    )
    write_file(
        root / ".github/copilot-instructions.md",
        "# Copilot Instructions\n\nSee `AGENTS.md` and `.github/INVENTORY.md`.\n",
    )
    write_file(
        root
        / ".github/skills/local-agent-sync-external-resources/references/superpowers-normalization.yaml",
        textwrap.dedent(
            """
            version: 1
            source_family: obra/superpowers
            local_prefix: superpowers-
            managed_skills:
              - upstream: demo
                legacy_local: obra-demo
                local: superpowers-demo
            live_scan:
              include:
                - .github/skills
              ignored_files:
                - superpowers-normalization.yaml
            """
        ).lstrip(),
    )
    if with_inventory:
        sync_inventory(root)


def sync_inventory(root: Path) -> None:
    write_file(
        root / ".github/INVENTORY.md", build_inventory.build_inventory_markdown(root)
    )


def write_valid_internal_skill(skill_dir: Path, skill_name: str) -> None:
    write_file(
        skill_dir / "SKILL.md",
        "---\n"
        f"name: {skill_name}\n"
        "description: Use when validating repository-owned skill metadata safely.\n"
        "---\n\n"
        f"# {skill_name}\n\n"
        "## When to use\n"
        "- Use when validating repository-owned skill metadata safely.\n\n"
        "Use `AGENTS.md` for bridge context.\n",
    )
    write_file(
        skill_dir / "agents/openai.yaml",
        "interface:\n"
        f"  display_name: {skill_name}\n"
        "  short_description: Validate internal skill metadata safely\n"
        f"  default_prompt: Use ${skill_name} for validation.\n",
    )


def test_build_inventory_main_rebuilds_inventory_file(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    initialize_governance_repo(tmp_path, with_inventory=False)
    monkeypatch.setattr(
        build_inventory,
        "parse_args",
        lambda: argparse.Namespace(root=str(tmp_path), check=False),
    )

    exit_code = build_inventory.main()

    assert exit_code == 0
    assert (tmp_path / ".github/INVENTORY.md").read_text(
        encoding="utf-8"
    ) == build_inventory.build_inventory_markdown(tmp_path)
    assert "Inventory rebuilt successfully." in capsys.readouterr().out


def test_github_catalog_validation_main_runs_required_targets_then_token_risks(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    initialize_governance_repo(tmp_path, with_inventory=False)
    called_targets: list[str] = []

    def fake_run(command: list[str], cwd: Path, check: bool) -> SimpleNamespace:
        assert check is False
        assert Path(cwd) == tmp_path
        assert command[0] == "make"
        called_targets.append(command[1])
        if command[1] == "token-risks":
            return SimpleNamespace(returncode=1)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(
        github_catalog_validation,
        "parse_args",
        lambda: argparse.Namespace(
            root=str(tmp_path),
            skip_token_risks=False,
            token_risks_only=False,
        ),
    )
    monkeypatch.setattr(github_catalog_validation.subprocess, "run", fake_run)

    exit_code = github_catalog_validation.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert called_targets == [
        "catalog-lint",
        "test",
        "skill-lint",
        "catalog-check",
        "docs-lint",
        "token-risks",
    ]
    assert (
        "continuing to match .github/workflows/_github-catalog-validation.yml" in output
    )


def test_github_catalog_validation_main_honors_token_risks_only(
    monkeypatch, tmp_path: Path
) -> None:
    initialize_governance_repo(tmp_path, with_inventory=False)
    called_targets: list[str] = []

    def fake_run(command: list[str], cwd: Path, check: bool) -> SimpleNamespace:
        assert check is False
        assert Path(cwd) == tmp_path
        called_targets.append(command[1])
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(
        github_catalog_validation,
        "parse_args",
        lambda: argparse.Namespace(
            root=str(tmp_path),
            skip_token_risks=False,
            token_risks_only=True,
        ),
    )
    monkeypatch.setattr(github_catalog_validation.subprocess, "run", fake_run)

    exit_code = github_catalog_validation.main()

    assert exit_code == 0
    assert called_targets == ["token-risks"]


def test_build_inventory_main_check_detects_inventory_drift(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    initialize_governance_repo(tmp_path)
    write_file(tmp_path / ".github/INVENTORY.md", "# stale\n")
    monkeypatch.setattr(
        build_inventory,
        "parse_args",
        lambda: argparse.Namespace(root=str(tmp_path), check=True),
    )

    exit_code = build_inventory.main()

    assert exit_code == 1
    assert "Inventory drift detected." in capsys.readouterr().out


def test_check_catalog_consistency_main_emits_json_and_fails_on_blocking_findings(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    initialize_governance_repo(tmp_path, with_inventory=False)
    write_file(
        tmp_path / ".github/agents/internal-empty.agent.md",
        "---\nname: internal-empty\ntools: []\n---\n\n# Empty\n",
    )
    sync_inventory(tmp_path)
    monkeypatch.setattr(
        check_catalog_consistency,
        "parse_args",
        lambda: argparse.Namespace(
            root=str(tmp_path),
            include_token_risks=False,
            strict=False,
            format="json",
        ),
    )

    exit_code = check_catalog_consistency.main()
    payload = json.loads(capsys.readouterr().out)
    finding_codes = {item["code"] for item in payload}

    assert exit_code == 1
    assert "internal-agent-missing-tools" in finding_codes


def test_detect_token_risks_main_respects_strict_mode(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    repeated_lines = "\n".join(
        [
            "- Keep policy separate from inventory.",
            "- Keep AGENTS.md strategic and stable.",
            "- Keep .github/copilot-instructions.md as the projection layer.",
            "- Keep .github/INVENTORY.md as the exact catalog.",
            "- Preserve explicit precedence rules.",
            "- Remove overlap instead of keeping compatibility copies.",
        ]
    )

    write_file(tmp_path / "AGENTS.md", f"# AGENTS\n\n{repeated_lines}\n")
    write_file(
        tmp_path / ".github/copilot-instructions.md",
        f"# Copilot\n\n{repeated_lines}\n",
    )
    write_file(tmp_path / ".github/INVENTORY.md", "# Inventory\n")
    monkeypatch.setattr(
        detect_token_risks,
        "parse_args",
        lambda: argparse.Namespace(root=str(tmp_path), strict=True, format="json"),
    )

    exit_code = detect_token_risks.main()
    payload = json.loads(capsys.readouterr().out)
    finding_codes = {item["code"] for item in payload}

    assert exit_code == 1
    assert "bridge-overlap" in finding_codes


def test_audit_copilot_catalog_main_groups_blocking_findings(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    initialize_governance_repo(tmp_path, with_inventory=False)
    monkeypatch.setattr(
        audit_copilot_catalog,
        "parse_args",
        lambda: argparse.Namespace(root=str(tmp_path), format="text"),
    )

    exit_code = audit_copilot_catalog.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "BLOCKING" in output
    assert ".github/INVENTORY.md" in output


def test_validate_internal_skills_main_honors_skill_selection(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    initialize_governance_repo(tmp_path, with_inventory=False)
    write_valid_internal_skill(
        tmp_path / ".github/skills/internal-good", "internal-good"
    )
    (tmp_path / ".github/skills/internal-bad").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        validate_internal_skills,
        "parse_args",
        lambda: argparse.Namespace(
            root=str(tmp_path),
            skill=["internal-good"],
            strict=True,
            format="text",
        ),
    )

    exit_code = validate_internal_skills.main()

    assert exit_code == 0
    assert "validation passed with no findings" in capsys.readouterr().out


def test_sync_copilot_catalog_plan_mode_outputs_json_and_creates_plan(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    initialize_governance_repo(source_root)
    initialize_governance_repo(target_root, with_inventory=False)
    write_file(
        source_root / ".github/agents/internal-fast.agent.md",
        "---\nname: internal-fast\ntools: [read]\n---\n\n# Fast\n",
    )
    sync_inventory(source_root)
    monkeypatch.setattr(
        sync_copilot_catalog,
        "parse_args",
        lambda: argparse.Namespace(
            command="plan",
            source_root=str(source_root),
            target_repo=str(target_root),
            allow_dirty_target=False,
            format="json",
        ),
    )

    exit_code = sync_copilot_catalog.main()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["mode"] == "plan"
    assert payload["plan_path"].endswith("tmp/copilot-sync.plan.md")
    assert (target_root / "tmp/copilot-sync.plan.md").exists()


def test_sync_copilot_catalog_apply_aborts_when_source_has_blocking_findings(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    source_root = tmp_path / "source"
    target_root = tmp_path / "target"
    initialize_governance_repo(source_root, with_inventory=False)
    initialize_governance_repo(target_root, with_inventory=False)
    monkeypatch.setattr(
        sync_copilot_catalog,
        "parse_args",
        lambda: argparse.Namespace(
            command="apply",
            source_root=str(source_root),
            target_repo=str(target_root),
            allow_dirty_target=False,
            format="text",
        ),
    )

    exit_code = sync_copilot_catalog.main()

    assert exit_code == 1
    assert not (target_root / ".github/copilot-sync.manifest.json").exists()
    assert (
        "Source repository has blocking governance findings" in capsys.readouterr().out
    )
