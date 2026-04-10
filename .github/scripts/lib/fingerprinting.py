from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

NORMALIZATION_VERSION = "v1"
HASH_ALGO = "sha256"
TEXT_EXTENSIONS = (".md", ".txt", ".yml", ".yaml", ".json", ".sh", ".py")


@dataclass(frozen=True)
class ResourceFingerprint:
    resource_id: str
    target_path: str
    source_ref: str | None
    kind: str
    normalization_version: str
    hash_algo: str
    source_hash: str
    content_hash: str
    metadata: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "resource_id": self.resource_id,
            "target_path": self.target_path,
            "source_ref": self.source_ref,
            "kind": self.kind,
            "normalization_version": self.normalization_version,
            "hash_algo": self.hash_algo,
            "source_hash": self.source_hash,
            "content_hash": self.content_hash,
            "metadata": self.metadata,
        }


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def collect_files(root: Path, raw_paths: list[Path]) -> list[Path]:
    files: set[Path] = set()
    for raw_path in raw_paths:
        path = raw_path if raw_path.is_absolute() else (root / raw_path)
        path = path.resolve()
        if path.is_file():
            files.add(path)
            continue
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    files.add(child.resolve())
            continue
        raise FileNotFoundError(f"Path not found: {raw_path}")
    return sorted(files)


def build_manifest(root: Path, files: list[Path], source_ref_base: str | None = None) -> dict[str, object]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": root.as_posix(),
        "normalization_version": NORMALIZATION_VERSION,
        "hash_algo": HASH_ALGO,
        "resources": [
            build_fingerprint(root, file_path, source_ref_base).to_dict()
            for file_path in files
        ],
    }


def build_fingerprint(root: Path, file_path: Path, source_ref_base: str | None = None) -> ResourceFingerprint:
    relative_path = file_path.relative_to(root).as_posix()
    raw_bytes = file_path.read_bytes()
    normalized_bytes = normalize_content(relative_path, raw_bytes)
    metadata = {
        "bytes": len(raw_bytes),
        "normalized_bytes": len(normalized_bytes),
    }
    return ResourceFingerprint(
        resource_id=relative_path,
        target_path=relative_path,
        source_ref=build_source_ref(source_ref_base, relative_path),
        kind=detect_kind(relative_path),
        normalization_version=NORMALIZATION_VERSION,
        hash_algo=HASH_ALGO,
        source_hash=sha256_bytes(raw_bytes),
        content_hash=sha256_bytes(normalized_bytes),
        metadata=metadata,
    )


def build_source_ref(source_ref_base: str | None, relative_path: str) -> str | None:
    if not source_ref_base:
        return None
    return source_ref_base.rstrip("/") + "/" + relative_path


def detect_kind(relative_path: str) -> str:
    if relative_path.startswith(".github/skills/") and relative_path.endswith("/SKILL.md"):
        return "skill"
    if relative_path.startswith(".github/agents/") and relative_path.endswith(".agent.md"):
        return "agent"
    if relative_path.startswith(".github/instructions/") and relative_path.endswith(".instructions.md"):
        return "instruction"
    if relative_path.startswith(".github/prompts/"):
        return "prompt"
    return "file"


def normalize_content(relative_path: str, raw_bytes: bytes) -> bytes:
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return raw_bytes

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized_lines = [line.rstrip() for line in normalized.split("\n")]
    while normalized_lines and normalized_lines[-1] == "":
        normalized_lines.pop()
    normalized = "\n".join(normalized_lines) + "\n"

    if relative_path.endswith(TEXT_EXTENSIONS):
        return normalized.encode("utf-8")
    return raw_bytes


def load_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def diff_manifests(old_manifest: dict[str, object], new_manifest: dict[str, object]) -> dict[str, object]:
    old_resources = index_resources(old_manifest)
    new_resources = index_resources(new_manifest)
    all_ids = sorted(set(old_resources) | set(new_resources))

    summary = {
        "created": 0,
        "removed": 0,
        "changed": 0,
        "noise_only": 0,
        "unchanged": 0,
    }
    resources: list[dict[str, object]] = []

    for resource_id in all_ids:
        old_item = old_resources.get(resource_id)
        new_item = new_resources.get(resource_id)
        if old_item is None:
            status = "created"
        elif new_item is None:
            status = "removed"
        elif old_item["content_hash"] != new_item["content_hash"]:
            status = "changed"
        elif old_item["source_hash"] != new_item["source_hash"]:
            status = "noise_only"
        else:
            status = "unchanged"

        summary[status] += 1
        resources.append(
            {
                "resource_id": resource_id,
                "status": status,
                "old": old_item,
                "new": new_item,
            }
        )

    return {
        "normalization_version": new_manifest.get("normalization_version"),
        "hash_algo": new_manifest.get("hash_algo"),
        "summary": summary,
        "resources": resources,
    }


def index_resources(manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        resource["resource_id"]: resource
        for resource in manifest.get("resources", [])
    }


def render_diff_text(result: dict[str, object]) -> str:
    summary = result["summary"]
    lines = [
        "summary:"
        f" created={summary['created']}"
        f" removed={summary['removed']}"
        f" changed={summary['changed']}"
        f" noise_only={summary['noise_only']}"
        f" unchanged={summary['unchanged']}"
    ]
    for resource in result["resources"]:
        status = resource["status"]
        if status == "unchanged":
            continue
        lines.append(f"{status:10s} {resource['resource_id']}")
    return "\n".join(lines)
