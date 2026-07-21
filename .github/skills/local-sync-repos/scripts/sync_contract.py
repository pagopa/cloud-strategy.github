from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

MANAGED_COPY_PATHS: tuple[str, ...] = (
    "AGENTS.md",
    ".python-version",
    ".pre-commit-config.yaml",
    ".editorconfig",
    ".github/copilot-instructions.md",
    ".github/workflows/_pre-commit.yml",
)

_INSTRUCTION_ROOT = ".github/instructions"
_AGENTS_LOCAL = "AGENTS.local.md"
_TEMPLATE_RELATIVE = Path(__file__).resolve().parent.parent / "templates" / "AGENTS.local.md"


class SourceContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class Operation:
    action: Literal["create", "update", "delete", "preserve"]
    path: str
    reason: str
    source_sha256: str | None = None
    target_sha256: str | None = None

    @property
    def is_mutation(self) -> bool:
        return self.action in {"create", "update", "delete"}


@dataclass(frozen=True)
class SyncPlan:
    source_root: Path
    target_root: Path
    operations: tuple[Operation, ...]
    dirty_managed_overlap: tuple[str, ...]
    fingerprint: str

    @property
    def managed_mutation_paths(self) -> tuple[str, ...]:
        return tuple(item.path for item in self.operations if item.is_mutation)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _normalize_posix(path: str) -> str:
    return str(Path(path)).replace("\\", "/")


def dirty_paths(target_root: Path) -> frozenset[str]:
    result = subprocess.run(
        ["git", "-C", str(target_root), "status", "--porcelain=v1", "-z"],
        check=True,
        capture_output=True,
    )
    raw = result.stdout
    if not raw:
        return frozenset()
    paths: set[str] = set()
    for entry in raw.split(b"\x00"):
        if not entry:
            continue
        path_part = entry[3:].decode("utf-8", errors="replace")
        if not path_part:
            continue
        paths.add(_normalize_posix(path_part))
    return frozenset(paths)


def _discover_source_instructions(source_root: Path) -> list[str]:
    instruction_dir = source_root / _INSTRUCTION_ROOT
    if not instruction_dir.is_dir():
        return []
    found: list[str] = []
    for path in sorted(instruction_dir.rglob("*")):
        if path.is_file():
            found.append(_normalize_posix(path.relative_to(source_root).as_posix()))
    return found


def _discover_target_instructions(target_root: Path) -> list[str]:
    instruction_dir = target_root / _INSTRUCTION_ROOT
    if not instruction_dir.is_dir():
        return []
    found: list[str] = []
    for path in sorted(instruction_dir.rglob("*")):
        if path.is_file():
            found.append(_normalize_posix(path.relative_to(target_root).as_posix()))
    return found


def _is_local_instruction(path: str) -> bool:
    return Path(path).name.startswith("local-")


def build_plan(source_root: Path, target_root: Path) -> SyncPlan:
    source = source_root.resolve()
    target = target_root.resolve()
    if source == target:
        raise SourceContractError("source and target resolve to the same directory")

    for relative in MANAGED_COPY_PATHS:
        candidate = source / relative
        if not candidate.is_file():
            raise SourceContractError(f"missing required source path: {relative}")

    template_path = _TEMPLATE_RELATIVE
    if not template_path.is_file():
        raise SourceContractError(f"missing AGENTS.local.md template: {template_path}")

    operations: list[Operation] = []

    for relative in MANAGED_COPY_PATHS:
        source_file = source / relative
        target_file = target / relative
        source_hash = _sha256_path(source_file)
        if target_file.is_file():
            target_hash = _sha256_path(target_file)
            if source_hash == target_hash:
                operations.append(
                    Operation(
                        action="preserve",
                        path=_normalize_posix(relative),
                        reason="target matches source",
                        source_sha256=source_hash,
                        target_sha256=target_hash,
                    )
                )
            else:
                operations.append(
                    Operation(
                        action="update",
                        path=_normalize_posix(relative),
                        reason="target differs from source",
                        source_sha256=source_hash,
                        target_sha256=target_hash,
                    )
                )
        else:
            operations.append(
                Operation(
                    action="create",
                    path=_normalize_posix(relative),
                    reason="missing in target",
                    source_sha256=source_hash,
                )
            )

    source_instructions = _discover_source_instructions(source)
    target_instructions = _discover_target_instructions(target)
    source_instruction_set = set(source_instructions)
    target_instruction_set = set(target_instructions)

    for rel in sorted(source_instruction_set | target_instruction_set):
        if _is_local_instruction(rel):
            target_file = target / rel
            target_hash = _sha256_path(target_file) if target_file.is_file() else None
            operations.append(
                Operation(
                    action="preserve",
                    path=_normalize_posix(rel),
                    reason="target-local instruction",
                    target_sha256=target_hash,
                )
            )
        elif rel in source_instruction_set and rel in target_instruction_set:
            source_hash = _sha256_path(source / rel)
            target_hash = _sha256_path(target / rel)
            if source_hash == target_hash:
                operations.append(
                    Operation(
                        action="preserve",
                        path=_normalize_posix(rel),
                        reason="target matches source",
                        source_sha256=source_hash,
                        target_sha256=target_hash,
                    )
                )
            else:
                operations.append(
                    Operation(
                        action="update",
                        path=_normalize_posix(rel),
                        reason="target differs from source",
                        source_sha256=source_hash,
                        target_sha256=target_hash,
                    )
                )
        elif rel in source_instruction_set:
            source_hash = _sha256_path(source / rel)
            operations.append(
                Operation(
                    action="create",
                    path=_normalize_posix(rel),
                    reason="missing in target",
                    source_sha256=source_hash,
                )
            )
        else:
            target_hash = _sha256_path(target / rel)
            operations.append(
                Operation(
                    action="delete",
                    path=_normalize_posix(rel),
                    reason="target-only non-local instruction",
                    target_sha256=target_hash,
                )
            )

    agents_local_target = target / _AGENTS_LOCAL
    if agents_local_target.is_file():
        target_hash = _sha256_path(agents_local_target)
        operations.append(
            Operation(
                action="preserve",
                path=_AGENTS_LOCAL,
                reason="consumer-owned local policy",
                target_sha256=target_hash,
            )
        )
    else:
        template_bytes = template_path.read_bytes()
        source_hash = _sha256_bytes(template_bytes)
        operations.append(
            Operation(
                action="create",
                path=_AGENTS_LOCAL,
                reason="create-once from template",
                source_sha256=source_hash,
            )
        )

    operations.sort(key=lambda op: (op.path, op.action))

    mutations = tuple(op for op in operations if op.is_mutation)
    fingerprint = plan_fingerprint(mutations)

    target_dirty = dirty_paths(target)
    mutation_paths = {op.path for op in operations if op.is_mutation}
    overlap = tuple(sorted(target_dirty & mutation_paths))

    return SyncPlan(
        source_root=source,
        target_root=target,
        operations=tuple(operations),
        dirty_managed_overlap=overlap,
        fingerprint=fingerprint,
    )


def plan_fingerprint(operations: tuple[Operation, ...]) -> str:
    records: list[dict[str, str | None]] = []
    for op in sorted(operations, key=lambda o: (o.path, o.action)):
        records.append(
            {
                "action": op.action,
                "path": _normalize_posix(op.path),
                "source_sha256": op.source_sha256,
                "target_sha256": op.target_sha256,
            }
        )
    canonical = json.dumps(
        records,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return _sha256_bytes(canonical.encode("utf-8"))
