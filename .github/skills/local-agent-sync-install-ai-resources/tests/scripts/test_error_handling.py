from pathlib import Path

import pytest
from home_sync_contract import load_home_sync_catalog
from home_syncing import build_home_sync_plan


def test_load_catalog_raises_valueerror_on_malformed_yaml(
    tmp_path: Path, write_refs
) -> None:
    write_refs(tmp_path, catalog_text="not: a: valid: yaml: [")

    with pytest.raises(
        ValueError, match="manifest-corrupt: failed to parse home sync catalog"
    ):
        load_home_sync_catalog(tmp_path)


def test_load_catalog_raises_keyerror_on_resource_missing_resource_id(
    tmp_path: Path, write_refs
) -> None:
    write_refs(
        tmp_path,
        catalog_text=(
            "version: 1\n"
            "defaults:\n"
            "  include_internal_skills: true\n"
            "resources:\n"
            "  - source_path: foo\n"
        ),
    )

    with pytest.raises(KeyError, match="resource_id"):
        load_home_sync_catalog(tmp_path)


def test_build_plan_raises_reverse_sync_blocked(tmp_path: Path, write_refs) -> None:
    write_refs(tmp_path)
    home_root = tmp_path / "home"
    state_root = home_root / ".sync" / "cloud-strategy-governance" / "home-ai-resources"
    source_under_state = state_root / "fake-source"
    (source_under_state / ".github").mkdir(parents=True)

    with pytest.raises(RuntimeError, match="reverse-sync-blocked"):
        build_home_sync_plan(source_under_state, home_root, ("skills",), mode="plan")
