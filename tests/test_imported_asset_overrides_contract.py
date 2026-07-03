from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str((Path(".") / ".github/scripts").resolve()))

from lib.fingerprinting import build_fingerprint  # noqa: E402

REGISTRY_PATH = Path(
    ".github/skills/local-agent-sync-external-resources/references/imported-asset-overrides.yaml"
)
SKILL_ROOT = REGISTRY_PATH.parent.parent


def load_registry() -> dict[str, object]:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_imported_asset_override_registry_tracks_expected_imported_targets() -> None:
    payload = load_registry()
    overrides = payload["overrides"]
    targets = {entry["target_path"] for entry in overrides}

    assert payload["policy"]["default_rule"] == "keep imported upstream assets verbatim"
    assert targets == {
        ".github/skills/grill-me/SKILL.md",
        ".github/skills/openai-spreadsheet/SKILL.md",
    }
    assert all(
        entry["approval"] == "explicit-user-counter-validated" for entry in overrides
    )
    assert all(entry["lifecycle_mode"] == "post-refresh-patch" for entry in overrides)
    assert all(entry["apply_strategy"] == "git-apply-3way" for entry in overrides)
    assert all((SKILL_ROOT / entry["patch_path"]).is_file() for entry in overrides)


def test_imported_asset_override_registry_hashes_match_live_targets() -> None:
    payload = load_registry()
    repo_root = Path(".").resolve()

    for entry in payload["overrides"]:
        target_path = repo_root / entry["target_path"]
        assert (
            build_fingerprint(repo_root, target_path).content_hash
            == entry["expected_content_hash"]
        )


def test_imported_asset_override_policy_is_visible_in_canonical_and_sync_assets() -> (
    None
):
    agents_text = Path("AGENTS.md").read_text(encoding="utf-8")
    copilot_text = Path(".github/copilot-instructions.md").read_text(encoding="utf-8")
    sync_agent_text = Path(
        ".github/agents/local-sync-external-resources.agent.md"
    ).read_text(encoding="utf-8")
    sync_skill_text = Path(
        ".github/skills/local-agent-sync-external-resources/SKILL.md"
    ).read_text(encoding="utf-8")
    target_sync_agent_text = Path(
        ".github/agents/local-sync-global-copilot-configs-into-repo.agent.md"
    ).read_text(encoding="utf-8")
    target_sync_skill_text = Path(
        ".github/skills/local-agent-sync-global-copilot-configs-into-repo/SKILL.md"
    ).read_text(encoding="utf-8")

    assert (
        "Source-side sync command centers and sync support skills own propagation behavior."
        in agents_text
    )
    assert "Keep consumer-facing defaults target-agnostic." in agents_text
    assert "Do not treat this file as instructions for coding agents" in copilot_text
    assert (
        "Do not edit imported upstream assets in place unless the need is strong"
        not in copilot_text
    )
    assert "Every approved imported in-place override must be mapped" in sync_agent_text
    assert (
        "Allow a direct in-place override only for a strong repo-specific need"
        in sync_agent_text
    )
    assert "scripts/apply_imported_asset_overrides.py" in sync_skill_text
    assert (
        "approved imported-asset override registries or replay patches"
        in target_sync_agent_text
    )
    assert (
        "approved imported-asset override registry plus replay patches"
        in target_sync_skill_text
    )


def test_external_refresh_skill_points_to_execution_guardrails() -> None:
    skill = Path(
        ".github/skills/local-agent-sync-external-resources/SKILL.md"
    ).read_text(encoding="utf-8")

    assert "references/refresh-execution-guardrails.md" in skill
    assert "check_external_refresh_workspace.py" in skill


def test_external_refresh_agent_reports_workspace_and_graphify_guard() -> None:
    agent = Path(
        ".github/agents/local-sync-external-resources.agent.md"
    ).read_text(encoding="utf-8")

    assert "Workspace guard" in agent
    assert "Graphify guard" in agent
    assert "Scoped validation" in agent
