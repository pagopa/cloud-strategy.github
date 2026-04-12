from __future__ import annotations

import json
from pathlib import Path

from lib.fingerprinting import (
    build_fingerprint,
    build_manifest,
    collect_files,
    diff_manifests,
    load_manifest,
    normalize_content,
    render_diff_text,
)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_collect_files_expands_directories_and_builds_manifest(tmp_path: Path) -> None:
    root = tmp_path
    write_file(root / ".github/agents/internal-fast.agent.md", "# fast\n")
    write_file(root / "README.md", "# readme\n")

    files = collect_files(root, [Path(".github/agents"), Path("README.md")])
    manifest = build_manifest(
        root, files, source_ref_base="https://example.test/source"
    )
    resources = {
        resource["resource_id"]: resource for resource in manifest["resources"]
    }

    assert [path.relative_to(root).as_posix() for path in files] == [
        ".github/agents/internal-fast.agent.md",
        "README.md",
    ]
    assert resources[".github/agents/internal-fast.agent.md"]["kind"] == "agent"
    assert resources[".github/agents/internal-fast.agent.md"]["source_ref"] == (
        "https://example.test/source/.github/agents/internal-fast.agent.md"
    )


def test_build_fingerprint_normalizes_text_and_leaves_binary_content_unchanged(
    tmp_path: Path,
) -> None:
    root = tmp_path
    text_path = root / ".github/instructions/internal-python.instructions.md"
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_bytes(b"line one\r\nline two\r\n\r\n")

    fingerprint = build_fingerprint(root, text_path, source_ref_base="source-root")

    assert fingerprint.kind == "instruction"
    assert (
        fingerprint.source_ref
        == "source-root/.github/instructions/internal-python.instructions.md"
    )
    assert fingerprint.metadata["bytes"] == len(b"line one\r\nline two\r\n\r\n")
    assert fingerprint.metadata["normalized_bytes"] == len(b"line one\nline two\n")
    assert normalize_content("binary.bin", b"\xff\x00") == b"\xff\x00"


def test_diff_manifests_tracks_changed_noise_only_created_and_removed(
    tmp_path: Path,
) -> None:
    old_manifest = {
        "normalization_version": "v1",
        "hash_algo": "sha256",
        "resources": [
            {"resource_id": "same.md", "source_hash": "a", "content_hash": "same"},
            {"resource_id": "noise.md", "source_hash": "old", "content_hash": "same"},
            {"resource_id": "changed.md", "source_hash": "old", "content_hash": "old"},
            {
                "resource_id": "removed.md",
                "source_hash": "gone",
                "content_hash": "gone",
            },
        ],
    }
    new_manifest = {
        "normalization_version": "v1",
        "hash_algo": "sha256",
        "resources": [
            {"resource_id": "same.md", "source_hash": "a", "content_hash": "same"},
            {"resource_id": "noise.md", "source_hash": "new", "content_hash": "same"},
            {"resource_id": "changed.md", "source_hash": "new", "content_hash": "new"},
            {"resource_id": "created.md", "source_hash": "new", "content_hash": "new"},
        ],
    }

    result = diff_manifests(old_manifest, new_manifest)
    diff_text = render_diff_text(result)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(new_manifest), encoding="utf-8")

    assert result["summary"] == {
        "created": 1,
        "removed": 1,
        "changed": 1,
        "noise_only": 1,
        "unchanged": 1,
    }
    assert "created    created.md" in diff_text
    assert "changed    changed.md" in diff_text
    assert load_manifest(manifest_path) == new_manifest
