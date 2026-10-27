import json
from pathlib import Path

import pytest
from home_syncing import ManagedResource, build_manifest_payload, load_manifest


def test_empty_manifest_defaults_to_schema_v2(tmp_path: Path) -> None:
    payload, error = load_manifest(tmp_path / "manifest.json")

    assert error is None
    assert payload == {"schema_version": 2, "managed_resources": []}


def test_v1_manifest_rows_are_normalized_as_copy_without_rewrite(
    tmp_path: Path,
) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "managed_resources": [
                    {
                        "target": "skills",
                        "resource_family": "skills",
                        "resource_id": "demo",
                        "source_path": ".github/skills/demo",
                        "target_path": str(tmp_path / "home/demo"),
                        "source_hash": "source",
                        "content_hash": "content",
                        "last_action": "copy",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    payload, error = load_manifest(path)

    assert error is None
    assert payload["managed_resources"][0]["materialization"] == "copy"
    assert payload["managed_resources"][0]["link_target"] is None
    assert path.read_text(encoding="utf-8").startswith('{"schema_version": 1')


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {
                "schema_version": 2,
                "managed_resources": [
                    {
                        "target": "skills",
                        "resource_family": "skills",
                        "materialization": "copy",
                        "link_target": None,
                        "content_hash": None,
                        "target_path": "/home/.agents/skills/demo",
                    }
                ],
            },
            id="copy-without-content-hash",
        ),
        pytest.param(
            {
                "schema_version": 2,
                "managed_resources": [
                    {
                        "target": "skills",
                        "resource_family": "skills",
                        "materialization": "symlink",
                        "link_target": None,
                        "content_hash": None,
                        "target_path": "/home/.agents/skills/demo",
                    }
                ],
            },
            id="symlink-without-link-target",
        ),
        pytest.param(
            {
                "schema_version": 2,
                "managed_resources": [
                    {
                        "target": "codex",
                        "resource_family": "agents",
                        "materialization": "copy",
                        "link_target": "/repo/.github/agents/demo.agent.md",
                        "content_hash": "hash",
                        "target_path": "/home/.codex/agents/demo.toml",
                    }
                ],
            },
            id="copy-with-link-target",
        ),
        pytest.param(
            {"schema_version": 99, "managed_resources": []},
            id="unsupported-schema-version",
        ),
    ],
)
def test_manifest_rejects_corrupt_payload(
    tmp_path: Path, payload: dict[str, object]
) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    _, error = load_manifest(path)

    assert error == "manifest-corrupt"


def test_valid_v2_manifest_rows_load_unchanged(tmp_path: Path) -> None:
    rows = [
        {
            "target": "skills",
            "resource_family": "skills",
            "materialization": "symlink",
            "link_target": (tmp_path / "repo/.github/skills/demo").as_posix(),
            "content_hash": None,
            "target_path": (tmp_path / "home/.agents/skills/demo").as_posix(),
        },
        {
            "target": "codex",
            "resource_family": "agents",
            "materialization": "copy",
            "link_target": None,
            "content_hash": "agent-content",
            "target_path": (tmp_path / "home/.codex/agents/review.toml").as_posix(),
        },
        {
            "target": "codex",
            "resource_family": "agents",
            "source_path": ".codex/agents/native.toml",
            "materialization": "symlink",
            "link_target": (tmp_path / ".codex/agents/native.toml").as_posix(),
            "content_hash": None,
            "target_path": (tmp_path / "home/.codex/agents/native.toml").as_posix(),
        },
        {
            "target": "copilot",
            "resource_family": "agents",
            "materialization": "symlink",
            "link_target": (
                tmp_path / "repo/.github/agents/review.agent.md"
            ).as_posix(),
            "content_hash": None,
            "target_path": (
                tmp_path / "home/.copilot/agents/review.agent.md"
            ).as_posix(),
        },
    ]
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps({"schema_version": 2, "managed_resources": rows}), encoding="utf-8"
    )

    payload, error = load_manifest(path)

    assert error is None
    assert payload["schema_version"] == 2
    assert payload["managed_resources"] == rows


def test_manifest_serialization_emits_v2_link_and_copy_rows(
    tmp_path: Path, make_plan
) -> None:
    skill = ManagedResource(
        target="skills",
        resource_id="demo",
        resource_family="skills",
        source_path=".github/skills/demo",
        target_path=str(tmp_path / "home/.agents/skills/demo"),
        source_hash="source",
        materialization="symlink",
        link_target=str(tmp_path / ".github/skills/demo"),
        content_hash=None,
        last_action="link",
    )
    agent = ManagedResource(
        target="codex",
        resource_id="review",
        resource_family="agents",
        source_path=".github/agents/review.agent.md",
        target_path=str(tmp_path / "home/.codex/agents/review.toml"),
        source_hash="source-agent",
        materialization="copy",
        link_target=None,
        content_hash="content-agent",
        last_action="copy",
    )
    native_agent = ManagedResource(
        target="codex",
        resource_id="native",
        resource_family="agents",
        source_path=".codex/agents/native.toml",
        target_path=str(tmp_path / "home/.codex/agents/native.toml"),
        source_hash="source-native",
        materialization="symlink",
        link_target=str(tmp_path / ".codex/agents/native.toml"),
        content_hash=None,
        last_action="link",
    )
    plan = make_plan(
        selected_targets=("skills", "codex"),
        source_revision=None,
        source_resources_considered=3,
        desired_resources=(skill, agent, native_agent),
    )

    payload = build_manifest_payload(plan)

    assert payload["schema_version"] == 2
    assert payload["managed_resources"] == [
        skill.to_dict(),
        agent.to_dict(),
        native_agent.to_dict(),
    ]
