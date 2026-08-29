from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str
    suggestion: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "suggestion": self.suggestion,
        }


@dataclass(frozen=True)
class SyncOperation:
    action: str
    path: str
    reason: str
    source_hash: str | None = None
    target_hash: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "action": self.action,
            "path": self.path,
            "reason": self.reason,
            "source_hash": self.source_hash,
            "target_hash": self.target_hash,
        }


@dataclass(frozen=True)
class SyncPlan:
    source_root: Path
    target_root: Path
    source_revision: str | None
    source_version: str | None
    target_manifest_source_version: str | None
    target_dirty: bool
    stacks: tuple[str, ...]
    operations: tuple[SyncOperation, ...]
    local_assets: tuple[str, ...]
    generated_inventory: str
    generated_lessons: str | None = None
    generated_gitignore: str | None = None
    dirty_paths: tuple[str, ...] = ()
    managed_mutation_paths: tuple[str, ...] = ()
    dirty_managed_overlap: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "source_root": self.source_root.as_posix(),
            "target_root": self.target_root.as_posix(),
            "source_revision": self.source_revision,
            "source_version": self.source_version,
            "target_manifest_source_version": self.target_manifest_source_version,
            "target_dirty": self.target_dirty,
            "stacks": list(self.stacks),
            "local_assets": list(self.local_assets),
            "dirty_paths": list(self.dirty_paths),
            "managed_mutation_paths": list(self.managed_mutation_paths),
            "dirty_managed_overlap": list(self.dirty_managed_overlap),
            "operations": [operation.to_dict() for operation in self.operations],
        }


def action_sort_key(action: str) -> int:
    ordering = {
        "create": 0,
        "update": 1,
        "rename": 2,
        "ensure": 3,
        "rebuild": 4,
        "delete": 5,
        "manual": 6,
        "preserve": 7,
        "unchanged": 8,
    }
    return ordering.get(action, 99)


def finding_sort_key(finding: Finding) -> tuple[int, str, str]:
    severity_order = {"blocking": 0, "non-blocking": 1}
    return (severity_order.get(finding.severity, 99), finding.path, finding.code)
