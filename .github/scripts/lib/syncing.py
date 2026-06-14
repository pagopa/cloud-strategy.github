from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from shutil import copy2

from .inventory import render_inventory_markdown, sections_from_catalog_paths
from .fingerprinting import HASH_ALGO, NORMALIZATION_VERSION, build_fingerprint
from .shared import (
    ARCHITECTURE_PATH,
    CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES,
    DOCS_README_PATH,
    INVENTORY_PATH,
    LEGACY_ARCHITECTURE_PATH,
    LEGACY_LOCAL_ARCHITECTURE_PATH,
    LEGACY_LOCAL_REPOSITORY_CONTEXT_PATH,
    LEGACY_REPOSITORY_CONTEXT_PATH,
    LEGACY_RUNTIME_FIT_PATH,
    LESSONS_PATH,
    MANAGED_ROOT_FILES,
    MANAGED_WORKFLOW_FILES,
    REPOSITORY_CONTEXT_PATH,
    RETIRED_RUNTIME_OPERATING_MODEL_PATH,
    STRUCTURE_PATH,
    TECH_PATH,
    VSCODE_COPILOT_SETTINGS,
    VSCODE_SETTINGS_PATH,
    SyncOperation,
    SyncPlan,
    action_sort_key,
    all_files_under,
    git_dirty_paths,
    git_revision,
    is_consumer_sync_excluded_path,
    is_git_dirty,
    is_ignored_sync_path,
    is_local_asset,
    read_text,
    sha256_file,
    write_text,
)

MANAGED_SKILL_DIR = ".github/skills"
SYNC_PLAN_PATH = "tmp/copilot-sync.plan.md"
SYNC_MANIFEST_PATH = ".github/copilot-sync.manifest.json"
VERSION_PATH = "VERSION"
LEGACY_SYNC_ARTIFACT_PATHS = (
    "tmp/internal-sync-copilot-configs.plan.md",
    ".github/internal-sync-copilot-configs.manifest.json",
)
TARGET_GITIGNORE_PATH = ".gitignore"
TARGET_SUPERPOWERS_IGNORE_ENTRY = "/tmp/superpowers/"
DEFAULT_NO_PENDING_LESSONS_MARKER = "No pending lessons currently require codification."
NO_PENDING_LESSONS_MARKERS = {
    "No pending lessons currently.",
    DEFAULT_NO_PENDING_LESSONS_MARKER,
}

ARCHITECTURE_LEGACY_PATHS = (
    LEGACY_LOCAL_ARCHITECTURE_PATH,
    LEGACY_ARCHITECTURE_PATH,
)
REPOSITORY_CONTEXT_LEGACY_PATHS = (
    LEGACY_LOCAL_REPOSITORY_CONTEXT_PATH,
    LEGACY_REPOSITORY_CONTEXT_PATH,
)


@dataclass(frozen=True)
class PendingLessonsTable:
    column_count: int
    data_start: int
    data_end: int
    section_end: int


@dataclass(frozen=True)
class JsoncObjectMember:
    key: str
    value_kind: str
    value_start: int
    value_end: int
    object_value: JsoncObjectInfo | None
    has_trailing_comma: bool


@dataclass(frozen=True)
class JsoncObjectInfo:
    start: int
    end: int
    members: tuple[JsoncObjectMember, ...]


class JsoncParseError(ValueError):
    pass


def append_vscode_settings_operation(
    target_root: Path,
    operations: list[SyncOperation],
) -> None:
    target_path = target_root / VSCODE_SETTINGS_PATH
    if not target_path.exists():
        desired_content = render_minimal_vscode_settings_jsonc()
        operations.append(
            SyncOperation(
                action="ensure",
                path=VSCODE_SETTINGS_PATH,
                reason=(
                    "Target VS Code settings file is missing; create it with managed Copilot-only settings."
                ),
                source_hash=sha256_text(desired_content),
                target_hash=None,
            )
        )
        return

    existing = read_text(target_path)
    try:
        updated = apply_managed_vscode_copilot_settings(existing)
    except JsoncParseError as error:
        operations.append(
            SyncOperation(
                action="manual",
                path=VSCODE_SETTINGS_PATH,
                reason=f"VS Code settings require manual reconciliation: {error}",
                source_hash=None,
                target_hash=sha256_file(target_path),
            )
        )
        return

    if updated == existing:
        operations.append(
            SyncOperation(
                action="unchanged",
                path=VSCODE_SETTINGS_PATH,
                reason="Target VS Code Copilot settings already match the managed field-level contract.",
                source_hash=sha256_text(updated),
                target_hash=sha256_file(target_path),
            )
        )
        return

    operations.append(
        SyncOperation(
            action="ensure",
            path=VSCODE_SETTINGS_PATH,
            reason="Target VS Code settings must be merged to enforce managed Copilot-only values.",
            source_hash=sha256_text(updated),
            target_hash=sha256_file(target_path),
        )
    )


def render_minimal_vscode_settings_jsonc() -> str:
    return (
        "{\n"
        '  "github.copilot.chat.codeGeneration.useInstructionFiles": false,\n'
        '  "chat.instructionsFilesLocations": {\n'
        '    ".github/instructions": false\n'
        "  }\n"
        "}\n"
    )


def skip_jsonc_space_and_comments(text: str, index: int) -> int:
    length = len(text)
    cursor = index
    while cursor < length:
        char = text[cursor]
        if char in {" ", "\t", "\n", "\r"}:
            cursor += 1
            continue
        if text.startswith("//", cursor):
            cursor += 2
            while cursor < length and text[cursor] not in {"\n", "\r"}:
                cursor += 1
            continue
        if text.startswith("/*", cursor):
            end = text.find("*/", cursor + 2)
            if end == -1:
                raise JsoncParseError("unterminated block comment")
            cursor = end + 2
            continue
        break
    return cursor


def consume_jsonc_string(text: str, index: int) -> tuple[str, int]:
    if index >= len(text) or text[index] != '"':
        raise JsoncParseError("expected string")
    cursor = index + 1
    chars: list[str] = []
    while cursor < len(text):
        char = text[cursor]
        if char == '"':
            return "".join(chars), cursor + 1
        if char == "\\":
            cursor += 1
            if cursor >= len(text):
                raise JsoncParseError("unterminated string escape")
            escaped = text[cursor]
            if escaped == "u":
                hex_chunk = text[cursor + 1 : cursor + 5]
                if len(hex_chunk) != 4 or not all(
                    glyph in "0123456789abcdefABCDEF" for glyph in hex_chunk
                ):
                    raise JsoncParseError("invalid unicode escape")
                chars.append(chr(int(hex_chunk, 16)))
                cursor += 5
                continue
            escaped_map = {
                '"': '"',
                "\\": "\\",
                "/": "/",
                "b": "\b",
                "f": "\f",
                "n": "\n",
                "r": "\r",
                "t": "\t",
            }
            if escaped not in escaped_map:
                raise JsoncParseError("invalid escape sequence")
            chars.append(escaped_map[escaped])
            cursor += 1
            continue
        chars.append(char)
        cursor += 1
    raise JsoncParseError("unterminated string")


def consume_jsonc_scalar(text: str, index: int) -> int:
    cursor = index
    while cursor < len(text):
        char = text[cursor]
        if char in {",", "}", "]"}:
            break
        if char in {" ", "\t", "\n", "\r"}:
            break
        if text.startswith("//", cursor) or text.startswith("/*", cursor):
            break
        cursor += 1
    if cursor == index:
        raise JsoncParseError("expected scalar value")
    return cursor


def parse_jsonc_value(
    text: str,
    index: int,
) -> tuple[str, int, int, JsoncObjectInfo | None, int]:
    cursor = skip_jsonc_space_and_comments(text, index)
    if cursor >= len(text):
        raise JsoncParseError("expected value")

    char = text[cursor]
    if char == '{':
        object_info, next_cursor = parse_jsonc_object(text, cursor)
        return "object", cursor, next_cursor, object_info, next_cursor
    if char == '[':
        next_cursor = parse_jsonc_array(text, cursor)
        return "array", cursor, next_cursor, None, next_cursor
    if char == '"':
        _, next_cursor = consume_jsonc_string(text, cursor)
        return "string", cursor, next_cursor, None, next_cursor

    next_cursor = consume_jsonc_scalar(text, cursor)
    token = text[cursor:next_cursor]
    if token in {"true", "false", "null"}:
        return "literal", cursor, next_cursor, None, next_cursor

    if re.fullmatch(r"-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?", token):
        return "number", cursor, next_cursor, None, next_cursor
    raise JsoncParseError(f"invalid token '{token}'")


def parse_jsonc_array(text: str, index: int) -> int:
    cursor = index + 1
    expect_value = True
    while True:
        cursor = skip_jsonc_space_and_comments(text, cursor)
        if cursor >= len(text):
            raise JsoncParseError("unterminated array")
        if text[cursor] == ']':
            return cursor + 1
        if not expect_value:
            raise JsoncParseError("expected ',' or ']' in array")

        _, _, _, _, cursor = parse_jsonc_value(text, cursor)
        cursor = skip_jsonc_space_and_comments(text, cursor)
        if cursor >= len(text):
            raise JsoncParseError("unterminated array")
        if text[cursor] == ',':
            cursor += 1
            expect_value = True
            continue
        if text[cursor] == ']':
            return cursor + 1
        raise JsoncParseError("expected ',' or ']' in array")


def parse_jsonc_object(text: str, index: int) -> tuple[JsoncObjectInfo, int]:
    cursor = index + 1
    members: list[JsoncObjectMember] = []

    while True:
        cursor = skip_jsonc_space_and_comments(text, cursor)
        if cursor >= len(text):
            raise JsoncParseError("unterminated object")
        if text[cursor] == '}':
            return JsoncObjectInfo(start=index, end=cursor, members=tuple(members)), cursor + 1

        key, after_key = consume_jsonc_string(text, cursor)
        cursor = skip_jsonc_space_and_comments(text, after_key)
        if cursor >= len(text) or text[cursor] != ':':
            raise JsoncParseError("expected ':' after object key")
        cursor += 1

        value_kind, value_start, value_end, value_object, cursor = parse_jsonc_value(
            text, cursor
        )
        cursor = skip_jsonc_space_and_comments(text, cursor)
        has_trailing_comma = False
        if cursor < len(text) and text[cursor] == ',':
            has_trailing_comma = True
            cursor += 1

        members.append(
            JsoncObjectMember(
                key=key,
                value_kind=value_kind,
                value_start=value_start,
                value_end=value_end,
                object_value=value_object,
                has_trailing_comma=has_trailing_comma,
            )
        )

        if has_trailing_comma:
            continue

        cursor = skip_jsonc_space_and_comments(text, cursor)
        if cursor >= len(text):
            raise JsoncParseError("unterminated object")
        if text[cursor] == '}':
            return JsoncObjectInfo(start=index, end=cursor, members=tuple(members)), cursor + 1
        raise JsoncParseError("expected ',' or '}' in object")


def parse_jsonc_root_object(text: str) -> JsoncObjectInfo:
    cursor = skip_jsonc_space_and_comments(text, 0)
    if cursor >= len(text) or text[cursor] != '{':
        raise JsoncParseError("settings content must start with a JSON object")
    root, next_cursor = parse_jsonc_object(text, cursor)
    trailing = skip_jsonc_space_and_comments(text, next_cursor)
    if trailing != len(text):
        raise JsoncParseError("unexpected trailing content after root object")
    return root


def object_members_by_key(object_info: JsoncObjectInfo, key: str) -> list[JsoncObjectMember]:
    return [member for member in object_info.members if member.key == key]


def object_indent(text: str, object_info: JsoncObjectInfo) -> str:
    line_start = text.rfind("\n", 0, object_info.start) + 1
    prefix = text[line_start:object_info.start]
    return re.match(r"[ \t]*", prefix).group(0) if prefix else ""


def member_indent(text: str, object_info: JsoncObjectInfo) -> str:
    for member in object_info.members:
        line_start = text.rfind("\n", 0, member.value_start) + 1
        indent = re.match(r"[ \t]*", text[line_start:member.value_start]).group(0)
        if indent:
            return indent
    return f"{object_indent(text, object_info)}  "


def insert_object_member(text: str, object_info: JsoncObjectInfo, member_text: str) -> str:
    indent = member_indent(text, object_info)
    if not object_info.members:
        base_indent = object_indent(text, object_info)
        insertion = f"\n{indent}{member_text}\n{base_indent}"
        return text[: object_info.start + 1] + insertion + text[object_info.end :]

    last_member = object_info.members[-1]
    separator = "" if last_member.has_trailing_comma else ","
    insertion = f"{separator}\n{indent}{member_text}"
    return text[: object_info.end] + insertion + text[object_info.end :]


def ensure_root_boolean_setting(
    text: str,
    root: JsoncObjectInfo,
    key: str,
) -> str:
    matches = object_members_by_key(root, key)
    if len(matches) > 1:
        raise JsoncParseError(f"duplicate key '{key}' is not safe to auto-merge")
    if not matches:
        return insert_object_member(text, root, f'"{key}": false')

    member = matches[0]
    value = text[member.value_start : member.value_end].strip()
    if value == "false":
        return text
    if value != "true":
        raise JsoncParseError(
            f"managed key '{key}' must be a boolean for safe merge"
        )
    return text[: member.value_start] + "false" + text[member.value_end :]


def ensure_nested_boolean_setting(
    text: str,
    root: JsoncObjectInfo,
    object_key: str,
    nested_key: str,
) -> str:
    matches = object_members_by_key(root, object_key)
    if len(matches) > 1:
        raise JsoncParseError(
            f"duplicate key '{object_key}' is not safe to auto-merge"
        )

    if not matches:
        nested_object = f'"{object_key}": {{\n    "{nested_key}": false\n  }}'
        return insert_object_member(text, root, nested_object)

    member = matches[0]
    if member.value_kind != "object" or member.object_value is None:
        raise JsoncParseError(
            f"managed key '{object_key}' must be an object for safe merge"
        )

    nested_matches = object_members_by_key(member.object_value, nested_key)
    if len(nested_matches) > 1:
        raise JsoncParseError(
            f"duplicate key '{nested_key}' inside '{object_key}' is not safe to auto-merge"
        )

    if not nested_matches:
        return insert_object_member(text, member.object_value, f'"{nested_key}": false')

    nested_member = nested_matches[0]
    nested_value = text[nested_member.value_start : nested_member.value_end].strip()
    if nested_value == "false":
        return text
    if nested_value != "true":
        raise JsoncParseError(
            f"managed key '{object_key}.{nested_key}' must be a boolean for safe merge"
        )
    return text[: nested_member.value_start] + "false" + text[nested_member.value_end :]


def apply_managed_vscode_copilot_settings(content: str) -> str:
    updated = content
    root = parse_jsonc_root_object(updated)
    updated = ensure_root_boolean_setting(
        updated,
        root,
        VSCODE_COPILOT_SETTINGS[0][0][0],
    )

    root = parse_jsonc_root_object(updated)
    updated = ensure_nested_boolean_setting(
        updated,
        root,
        VSCODE_COPILOT_SETTINGS[1][0][0],
        VSCODE_COPILOT_SETTINGS[1][0][1],
    )
    return updated


def build_sync_plan(source_root: Path, target_root: Path) -> SyncPlan:
    source_root = source_root.resolve()
    target_root = target_root.resolve()
    source_version = read_source_version(source_root)
    target_manifest_source_version = read_target_manifest_source_version(target_root)

    source_files = discover_source_sync_files(source_root)
    target_files = discover_target_managed_files(target_root)
    target_excluded_files = discover_target_excluded_sync_files(target_root)
    operations: list[SyncOperation] = []
    local_assets: list[str] = []
    generated_lessons: str | None = None

    append_consumer_local_knowledge_operations(
        source_root=source_root,
        target_root=target_root,
        operations=operations,
        local_assets=local_assets,
    )
    append_vscode_settings_operation(target_root=target_root, operations=operations)

    for relative_path in sorted(source_files):
        source_path = source_root / relative_path
        target_path = target_root / relative_path
        if relative_path == LESSONS_PATH:
            generated_lessons = render_synced_lessons(
                read_text(source_path),
                read_text(target_path) if target_path.exists() else None,
            )
            desired_hash = sha256_text(generated_lessons)
            if not target_path.exists():
                operations.append(
                    SyncOperation(
                        action="create",
                        path=relative_path,
                        reason="Target learning ledger missing; create it from the source structure.",
                        source_hash=desired_hash,
                        target_hash=None,
                    )
                )
                continue

            target_hash = sha256_file(target_path)
            action = "unchanged" if target_hash == desired_hash else "update"
            reason = (
                "Target learning ledger already matches the source structure and preserved lessons."
                if action == "unchanged"
                else "Target learning ledger must align with the source structure while preserving target-authored lessons."
            )
            operations.append(
                SyncOperation(
                    action=action,
                    path=relative_path,
                    reason=reason,
                    source_hash=desired_hash,
                    target_hash=target_hash,
                )
            )
            continue

        source_hash = sha256_file(source_path)
        if not target_path.exists():
            operations.append(
                SyncOperation(
                    action="create",
                    path=relative_path,
                    reason="Source-managed file missing from target.",
                    source_hash=source_hash,
                    target_hash=None,
                )
            )
            continue

        target_hash = sha256_file(target_path)
        action = "unchanged" if source_hash == target_hash else "update"
        reason = (
            "Already aligned with source."
            if action == "unchanged"
            else "Target file differs from source."
        )
        operations.append(
            SyncOperation(
                action=action,
                path=relative_path,
                reason=reason,
                source_hash=source_hash,
                target_hash=target_hash,
            )
        )

    for relative_path in sorted(target_files - source_files - {INVENTORY_PATH}):
        if is_local_asset(relative_path):
            local_assets.append(relative_path)
            operations.append(
                SyncOperation(
                    action="preserve",
                    path=relative_path,
                    reason="Preserved target-owned local extension.",
                    source_hash=None,
                    target_hash=sha256_file(target_root / relative_path),
                )
            )
            continue
        operations.append(
            SyncOperation(
                action="delete",
                path=relative_path,
                reason="Target-only non-local asset inside a source-managed category.",
                source_hash=None,
                target_hash=sha256_file(target_root / relative_path),
            )
        )

    for relative_path in sorted(target_excluded_files):
        operations.append(
            SyncOperation(
                action="delete",
                path=relative_path,
                reason="Target internal-sync resource must be removed from consumer repositories.",
                source_hash=None,
                target_hash=sha256_file(target_root / relative_path),
            )
        )

    for relative_path in LEGACY_SYNC_ARTIFACT_PATHS:
        legacy_path = target_root / relative_path
        if not legacy_path.exists():
            continue
        operations.append(
            SyncOperation(
                action="delete",
                path=relative_path,
                reason="Legacy internal-sync tracking artifact must be removed from consumer repositories.",
                source_hash=None,
                target_hash=sha256_file(legacy_path),
            )
        )

    retired_runtime_documents = {
        LEGACY_RUNTIME_FIT_PATH: (
            "Legacy runtime-fit document is retired; runtime workflow guidance "
            "now lives in root guidance and skills."
        ),
        RETIRED_RUNTIME_OPERATING_MODEL_PATH: (
            "Retired source-managed runtime operating model document; runtime "
            "workflow guidance now lives in root guidance and skills."
        ),
    }
    for relative_path, reason in retired_runtime_documents.items():
        retired_runtime_path = target_root / relative_path
        if not retired_runtime_path.exists():
            continue
        operations.append(
            SyncOperation(
                action="delete",
                path=relative_path,
                reason=reason,
                source_hash=None,
                target_hash=sha256_file(retired_runtime_path),
            )
        )

    future_inventory_paths = sorted(
        catalog_path
        for catalog_path in source_files
        if catalog_path.startswith(
            (
                ".github/agents/",
                ".github/instructions/",
                ".github/prompts/",
                ".github/skills/",
            )
        )
    )
    future_inventory_paths.extend(
        catalog_path
        for catalog_path in local_assets
        if catalog_path.startswith(
            (
                ".github/agents/",
                ".github/instructions/",
                ".github/prompts/",
                ".github/skills/",
            )
        )
    )
    generated_inventory = render_inventory_markdown(
        sections_from_catalog_paths(future_inventory_paths)
    )

    inventory_path = target_root / INVENTORY_PATH
    current_inventory = read_text(inventory_path) if inventory_path.exists() else None
    inventory_action = (
        "unchanged" if current_inventory == generated_inventory else "rebuild"
    )
    inventory_reason = (
        "Inventory already reflects target state."
        if inventory_action == "unchanged"
        else "Inventory must be rebuilt from target filesystem state."
    )
    operations.append(
        SyncOperation(
            action=inventory_action,
            path=INVENTORY_PATH,
            reason=inventory_reason,
            source_hash=None,
            target_hash=(
                sha256_file(inventory_path) if inventory_path.exists() else None
            ),
        )
    )

    gitignore_path = target_root / TARGET_GITIGNORE_PATH
    current_gitignore = read_text(gitignore_path) if gitignore_path.exists() else None
    generated_gitignore = ensure_superpowers_gitignore_entry(current_gitignore)
    gitignore_action = (
        "unchanged" if current_gitignore == generated_gitignore else "ensure"
    )
    gitignore_reason = (
        "Target .gitignore already ignores tmp/superpowers."
        if gitignore_action == "unchanged"
        else "Target .gitignore must ignore tmp/superpowers for Superpowers-generated working artifacts."
    )
    operations.append(
        SyncOperation(
            action=gitignore_action,
            path=TARGET_GITIGNORE_PATH,
            reason=gitignore_reason,
            source_hash=None,
            target_hash=(
                sha256_file(gitignore_path) if gitignore_path.exists() else None
            ),
        )
    )

    ordered_operations = tuple(
        sorted(
            operations,
            key=lambda operation: (action_sort_key(operation.action), operation.path),
        )
    )
    planned_paths = {operation.path for operation in ordered_operations}
    dirty_paths = tuple(
        path for path in git_dirty_paths(target_root) if path in planned_paths
    )
    managed_mutation_paths = tuple(
        sorted(
            {
                operation.path
                for operation in ordered_operations
                if operation.action
                in {
                    "create",
                    "update",
                    "rename",
                    "ensure",
                    "rebuild",
                    "delete",
                    "manual",
                }
            }
        )
    )
    dirty_managed_overlap = tuple(
        path for path in dirty_paths if path in managed_mutation_paths
    )
    return SyncPlan(
        source_root=source_root,
        target_root=target_root,
        source_revision=git_revision(source_root),
        source_version=source_version,
        target_manifest_source_version=target_manifest_source_version,
        target_dirty=is_git_dirty(target_root),
        stacks=tuple(detect_target_stacks(target_root)),
        operations=ordered_operations,
        local_assets=tuple(sorted(local_assets)),
        generated_inventory=generated_inventory,
        generated_lessons=generated_lessons,
        generated_gitignore=generated_gitignore,
        dirty_paths=dirty_paths,
        managed_mutation_paths=managed_mutation_paths,
        dirty_managed_overlap=dirty_managed_overlap,
    )


def append_consumer_local_knowledge_operations(
    source_root: Path,
    target_root: Path,
    operations: list[SyncOperation],
    local_assets: list[str],
) -> None:
    append_docs_readme_operations(source_root, target_root, operations, local_assets)
    append_architecture_operations(source_root, target_root, operations, local_assets)
    append_repository_context_operations(
        source_root, target_root, operations, local_assets
    )
    append_tech_operations(source_root, target_root, operations, local_assets)
    append_structure_operations(source_root, target_root, operations, local_assets)


def append_docs_readme_operations(
    source_root: Path,
    target_root: Path,
    operations: list[SyncOperation],
    local_assets: list[str],
) -> None:
    template_path = source_root / CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES[DOCS_README_PATH]
    target_path = target_root / DOCS_README_PATH

    if target_path.exists():
        local_assets.append(DOCS_README_PATH)
        operations.append(
            SyncOperation(
                action="preserve",
                path=DOCS_README_PATH,
                reason="Preserved consumer-local docs guide after scaffold materialization.",
                source_hash=(
                    sha256_file(template_path) if template_path.exists() else None
                ),
                target_hash=sha256_file(target_path),
            )
        )
        return

    if template_path.exists():
        operations.append(
            SyncOperation(
                action="create",
                path=DOCS_README_PATH,
                reason="Consumer-local docs guide missing; create scaffold from the source template.",
                source_hash=sha256_file(template_path),
                target_hash=None,
            )
        )


def append_architecture_operations(
    source_root: Path,
    target_root: Path,
    operations: list[SyncOperation],
    local_assets: list[str],
) -> None:
    template_path = source_root / CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES[ARCHITECTURE_PATH]
    target_path = target_root / ARCHITECTURE_PATH
    legacy_paths = [
        legacy_path
        for legacy_path in ARCHITECTURE_LEGACY_PATHS
        if (target_root / legacy_path).exists()
    ]

    if target_path.exists() and legacy_paths:
        local_assets.append(ARCHITECTURE_PATH)
        operations.append(
            SyncOperation(
                action="manual",
                path=ARCHITECTURE_PATH,
                reason=(
                    f"Both canonical {ARCHITECTURE_PATH} and legacy {', '.join(legacy_paths)} exist; reconcile manually before apply."
                ),
                source_hash=(
                    sha256_file(template_path) if template_path.exists() else None
                ),
                target_hash=sha256_file(target_path),
            )
        )
        return

    if target_path.exists():
        local_assets.append(ARCHITECTURE_PATH)
        operations.append(
            SyncOperation(
                action="preserve",
                path=ARCHITECTURE_PATH,
                reason="Preserved consumer-local architecture contract after scaffold materialization.",
                source_hash=(
                    sha256_file(template_path) if template_path.exists() else None
                ),
                target_hash=sha256_file(target_path),
            )
        )
        return

    if len(legacy_paths) > 1:
        operations.append(
            SyncOperation(
                action="manual",
                path=ARCHITECTURE_PATH,
                reason=(
                    f"Multiple legacy paths for {ARCHITECTURE_PATH} exist ({', '.join(legacy_paths)}); reconcile manually before apply."
                ),
                source_hash=(
                    sha256_file(template_path) if template_path.exists() else None
                ),
                target_hash=sha256_file(target_root / legacy_paths[0]),
            )
        )
        return

    if legacy_paths:
        legacy_path = legacy_paths[0]
        operations.append(
            SyncOperation(
                action="rename",
                path=ARCHITECTURE_PATH,
                reason=f"Legacy {legacy_path} should move to consumer-local {ARCHITECTURE_PATH}.",
                source_hash=None,
                target_hash=sha256_file(target_root / legacy_path),
            )
        )
        return

    if template_path.exists():
        operations.append(
            SyncOperation(
                action="create",
                path=ARCHITECTURE_PATH,
                reason="Consumer-local architecture contract missing; create scaffold from the source template.",
                source_hash=sha256_file(template_path),
                target_hash=None,
            )
        )


def append_repository_context_operations(
    source_root: Path,
    target_root: Path,
    operations: list[SyncOperation],
    local_assets: list[str],
) -> None:
    template_path = (
        source_root / CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES[REPOSITORY_CONTEXT_PATH]
    )
    target_path = target_root / REPOSITORY_CONTEXT_PATH
    legacy_paths = [
        legacy_path
        for legacy_path in REPOSITORY_CONTEXT_LEGACY_PATHS
        if (target_root / legacy_path).exists()
    ]

    if target_path.exists() and legacy_paths:
        local_assets.append(REPOSITORY_CONTEXT_PATH)
        operations.append(
            SyncOperation(
                action="manual",
                path=REPOSITORY_CONTEXT_PATH,
                reason=(
                    f"Both canonical {REPOSITORY_CONTEXT_PATH} and legacy {', '.join(legacy_paths)} exist; reconcile manually before apply."
                ),
                source_hash=(
                    sha256_file(template_path) if template_path.exists() else None
                ),
                target_hash=sha256_file(target_path),
            )
        )
        return

    if target_path.exists():
        local_assets.append(REPOSITORY_CONTEXT_PATH)
        operations.append(
            SyncOperation(
                action="preserve",
                path=REPOSITORY_CONTEXT_PATH,
                reason="Preserved consumer-local repository context after scaffold materialization.",
                source_hash=(
                    sha256_file(template_path) if template_path.exists() else None
                ),
                target_hash=sha256_file(target_path),
            )
        )
        return

    if len(legacy_paths) > 1:
        operations.append(
            SyncOperation(
                action="manual",
                path=REPOSITORY_CONTEXT_PATH,
                reason=(
                    f"Multiple legacy paths for {REPOSITORY_CONTEXT_PATH} exist ({', '.join(legacy_paths)}); reconcile manually before apply."
                ),
                source_hash=(
                    sha256_file(template_path) if template_path.exists() else None
                ),
                target_hash=sha256_file(target_root / legacy_paths[0]),
            )
        )
        return

    if legacy_paths:
        legacy_path = legacy_paths[0]
        operations.append(
            SyncOperation(
                action="rename",
                path=REPOSITORY_CONTEXT_PATH,
                reason=f"Legacy {legacy_path} should move to consumer-local {REPOSITORY_CONTEXT_PATH}.",
                source_hash=None,
                target_hash=sha256_file(target_root / legacy_path),
            )
        )
        return

    if template_path.exists():
        operations.append(
            SyncOperation(
                action="create",
                path=REPOSITORY_CONTEXT_PATH,
                reason="Consumer-local repository context missing; create scaffold from the source template.",
                source_hash=sha256_file(template_path),
                target_hash=None,
            )
        )


def append_tech_operations(
    source_root: Path,
    target_root: Path,
    operations: list[SyncOperation],
    local_assets: list[str],
) -> None:
    template_path = source_root / CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES[TECH_PATH]
    target_path = target_root / TECH_PATH

    if target_path.exists():
        local_assets.append(TECH_PATH)
        operations.append(
            SyncOperation(
                action="preserve",
                path=TECH_PATH,
                reason="Preserved consumer-local technology document after scaffold materialization.",
                source_hash=(
                    sha256_file(template_path) if template_path.exists() else None
                ),
                target_hash=sha256_file(target_path),
            )
        )
        return

    if template_path.exists():
        operations.append(
            SyncOperation(
                action="create",
                path=TECH_PATH,
                reason="Consumer-local technology document missing; create scaffold from the source template.",
                source_hash=sha256_file(template_path),
                target_hash=None,
            )
        )


def append_structure_operations(
    source_root: Path,
    target_root: Path,
    operations: list[SyncOperation],
    local_assets: list[str],
) -> None:
    template_path = source_root / CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES[STRUCTURE_PATH]
    target_path = target_root / STRUCTURE_PATH

    if target_path.exists():
        local_assets.append(STRUCTURE_PATH)
        operations.append(
            SyncOperation(
                action="preserve",
                path=STRUCTURE_PATH,
                reason="Preserved consumer-local structure document after scaffold materialization.",
                source_hash=(
                    sha256_file(template_path) if template_path.exists() else None
                ),
                target_hash=sha256_file(target_path),
            )
        )
        return

    if template_path.exists():
        operations.append(
            SyncOperation(
                action="create",
                path=STRUCTURE_PATH,
                reason="Consumer-local structure document missing; create scaffold from the source template.",
                source_hash=sha256_file(template_path),
                target_hash=None,
            )
        )


def render_synced_lessons(source_content: str, target_content: str | None) -> str:
    source_lines = source_content.splitlines()
    pending_table = find_pending_lessons_table(source_lines)
    if pending_table is None:
        return ensure_trailing_newline(source_content)

    target_rows = extract_pending_lessons_rows(target_content)
    normalized_rows = [
        normalize_pending_lessons_row(row, pending_table.column_count)
        for row in target_rows
    ]
    section_suffix = [
        line
        for line in source_lines[pending_table.data_end : pending_table.section_end]
        if line.strip() not in NO_PENDING_LESSONS_MARKERS
    ]
    pending_section_lines = [format_markdown_table_row(row) for row in normalized_rows]
    if not normalized_rows:
        marker = (
            find_no_pending_lessons_marker(target_content)
            or find_no_pending_lessons_marker(source_content)
            or DEFAULT_NO_PENDING_LESSONS_MARKER
        )
        if not section_suffix or section_suffix[-1].strip():
            section_suffix.append("")
        section_suffix.append(marker)

    merged_lines = (
        source_lines[: pending_table.data_start]
        + pending_section_lines
        + section_suffix
        + source_lines[pending_table.section_end :]
    )
    return ensure_trailing_newline("\n".join(merged_lines))


def find_no_pending_lessons_marker(content: str | None) -> str | None:
    if not content:
        return None
    for line in content.splitlines():
        stripped = line.strip()
        if stripped in NO_PENDING_LESSONS_MARKERS:
            return stripped
    return None


def extract_pending_lessons_rows(content: str | None) -> list[list[str]]:
    if not content:
        return []
    lines = content.splitlines()
    pending_table = find_pending_lessons_table(lines)
    if pending_table is None:
        return []

    rows: list[list[str]] = []
    for line in lines[pending_table.data_start : pending_table.section_end]:
        stripped = line.strip()
        if not stripped:
            continue
        if not line.lstrip().startswith("|"):
            break
        cells = parse_markdown_table_row(line)
        if any(cell for cell in cells):
            rows.append(cells)
    return rows


def find_pending_lessons_table(lines: list[str]) -> PendingLessonsTable | None:
    section_start: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == "## Pending Rules":
            section_start = index + 1
            break
    if section_start is None:
        return None

    section_end = len(lines)
    for index in range(section_start, len(lines)):
        if lines[index].startswith("## "):
            section_end = index
            break

    header_index: int | None = None
    for index in range(section_start, section_end):
        if lines[index].lstrip().startswith("|"):
            header_index = index
            break
    if header_index is None or header_index + 1 >= section_end:
        return None
    if not is_markdown_table_separator(lines[header_index + 1]):
        return None

    data_start = header_index + 2
    data_end = data_start
    while data_end < section_end and lines[data_end].lstrip().startswith("|"):
        data_end += 1

    return PendingLessonsTable(
        column_count=len(parse_markdown_table_row(lines[header_index])),
        data_start=data_start,
        data_end=data_end,
        section_end=section_end,
    )


def is_markdown_table_separator(line: str) -> bool:
    cells = parse_markdown_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_markdown_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    core = stripped.strip("|")
    return [cell.strip() for cell in core.split("|")]


def normalize_pending_lessons_row(row: list[str], column_count: int) -> list[str]:
    if len(row) >= column_count:
        return row[:column_count]
    return row + [""] * (column_count - len(row))


def format_markdown_table_row(cells: list[str]) -> str:
    return f"| {' | '.join(cells)} |"


def ensure_trailing_newline(content: str) -> str:
    return content if content.endswith("\n") else f"{content}\n"


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def discover_source_sync_files(root: Path) -> set[str]:
    files = {
        relative_path
        for relative_path in MANAGED_ROOT_FILES
        if (root / relative_path).exists()
    }
    files.update(
        relative_path
        for relative_path in MANAGED_WORKFLOW_FILES
        if (root / relative_path).exists()
    )
    files.update(all_files_under(root, ".github/agents"))
    files.update(all_files_under(root, ".github/instructions"))
    files.update(all_files_under(root, ".github/prompts"))
    files.update(all_files_under(root, MANAGED_SKILL_DIR))
    for template_path in CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES.values():
        files.discard(template_path)
    return {
        relative_path
        for relative_path in files
        if not is_ignored_sync_path(relative_path)
        and not is_consumer_sync_excluded_path(relative_path)
        and not is_local_asset(relative_path)
    }


def discover_target_managed_files(root: Path) -> set[str]:
    files = {
        relative_path
        for relative_path in MANAGED_ROOT_FILES
        if (root / relative_path).exists()
    }
    files.update(
        relative_path
        for relative_path in MANAGED_WORKFLOW_FILES
        if (root / relative_path).exists()
    )
    if (root / INVENTORY_PATH).exists():
        files.add(INVENTORY_PATH)
    files.update(all_files_under(root, ".github/agents"))
    files.update(all_files_under(root, ".github/instructions"))
    files.update(all_files_under(root, ".github/prompts"))
    files.update(all_files_under(root, MANAGED_SKILL_DIR))
    return {
        relative_path
        for relative_path in files
        if not is_ignored_sync_path(relative_path)
        and not is_consumer_sync_excluded_path(relative_path)
    }


def discover_target_excluded_sync_files(root: Path) -> set[str]:
    files: set[str] = set()
    files.update(all_files_under(root, ".github/agents"))
    files.update(all_files_under(root, ".github/instructions"))
    files.update(all_files_under(root, ".github/prompts"))
    files.update(all_files_under(root, MANAGED_SKILL_DIR))
    return {
        relative_path
        for relative_path in files
        if not is_ignored_sync_path(relative_path)
        and is_consumer_sync_excluded_path(relative_path)
    }


def detect_target_stacks(root: Path) -> list[str]:
    stacks: list[str] = []
    if (root / "pyproject.toml").exists() or any(root.rglob("*.py")):
        stacks.append("python")
    if (
        (root / "package.json").exists()
        or any(root.rglob("*.ts"))
        or any(root.rglob("*.js"))
    ):
        stacks.append("node")
    if (root / "go.mod").exists() or any(root.rglob("*.go")):
        stacks.append("go")
    if any(root.rglob("*.tf")):
        stacks.append("terraform")
    if any(root.rglob("*.java")) or any(root.rglob("*.kt")):
        stacks.append("java")
    return stacks or ["unknown"]


def render_sync_plan_markdown(plan: SyncPlan) -> str:
    lines = [
        "# Copilot Sync Plan",
        "",
        f"- Source root: `{plan.source_root.as_posix()}`",
        f"- Target root: `{plan.target_root.as_posix()}`",
        f"- Source revision: `{plan.source_revision or 'unknown'}`",
        f"- Source version: `{plan.source_version or 'unknown'}`",
        f"- Target manifest source version: `{plan.target_manifest_source_version or 'unknown'}`",
        f"- Target dirty: `{'yes' if plan.target_dirty else 'no'}`",
        f"- Detected stacks: `{', '.join(plan.stacks)}`",
        "",
        "## Preserved Local Assets",
        "",
    ]
    if plan.local_assets:
        lines.extend(f"- `{path}`" for path in plan.local_assets)
    else:
        lines.append("No preserved `local-*` assets detected.")
    lines.append("")

    action_groups: dict[str, list[SyncOperation]] = {}
    for operation in plan.operations:
        action_groups.setdefault(operation.action, []).append(operation)

    lines.append("## Planned Operations")
    lines.append("")
    for action in [
        "create",
        "update",
        "rename",
        "ensure",
        "rebuild",
        "delete",
        "manual",
        "preserve",
        "unchanged",
    ]:
        group = action_groups.get(action, [])
        if not group:
            continue
        lines.append(f"### {action.title()}")
        lines.append("")
        for operation in group:
            lines.append(f"- `{operation.path}`: {operation.reason}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_sync_plan(plan: SyncPlan) -> Path:
    plan_path = plan.target_root / SYNC_PLAN_PATH
    write_text(plan_path, render_sync_plan_markdown(plan))
    return plan_path


def ensure_superpowers_gitignore_entry(current_content: str | None) -> str:
    if current_content is None:
        return f"{TARGET_SUPERPOWERS_IGNORE_ENTRY}\n"

    lines = current_content.splitlines()
    normalized_entries = {line.strip() for line in lines}
    accepted_entries = {
        "tmp/superpowers",
        "tmp/superpowers/",
        "/tmp/superpowers",
        "/tmp/superpowers/",
    }
    if normalized_entries & accepted_entries:
        return (
            current_content
            if current_content.endswith("\n")
            else f"{current_content}\n"
        )

    updated = current_content
    if updated and not updated.endswith("\n"):
        updated += "\n"
    updated += f"{TARGET_SUPERPOWERS_IGNORE_ENTRY}\n"
    return updated


def read_source_version(source_root: Path) -> str | None:
    version_path = source_root / VERSION_PATH
    if not version_path.exists():
        return None
    version = read_text(version_path).strip()
    return version or None


def read_target_manifest_source_version(target_root: Path) -> str | None:
    manifest_path = target_root / SYNC_MANIFEST_PATH
    if not manifest_path.exists():
        return None
    try:
        payload = json.loads(read_text(manifest_path))
    except (OSError, json.JSONDecodeError):
        return None

    source_version = payload.get("source_version")
    if not isinstance(source_version, str):
        return None
    normalized = source_version.strip()
    return normalized or None


def write_sync_manifest(plan: SyncPlan) -> Path:
    manifest_path = plan.target_root / SYNC_MANIFEST_PATH
    managed_hashes: dict[str, str] = {}
    managed_fingerprints: list[dict[str, object]] = []
    managed_settings = {
        "/".join(setting_path): value
        for setting_path, value in VSCODE_COPILOT_SETTINGS
    }
    for operation in plan.operations:
        if operation.action in {"delete", "manual", "preserve"}:
            continue
        if operation.path == VSCODE_SETTINGS_PATH:
            continue
        target_path = plan.target_root / operation.path
        if target_path.exists():
            managed_hashes[operation.path] = sha256_file(target_path)
            managed_fingerprints.append(
                build_fingerprint(
                    plan.target_root,
                    target_path,
                    source_ref_base=plan.source_root.as_posix(),
                ).to_dict()
            )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": plan.source_root.as_posix(),
        "target_root": plan.target_root.as_posix(),
        "source_revision": plan.source_revision,
        "source_version": plan.source_version,
        "normalization_version": NORMALIZATION_VERSION,
        "hash_algo": HASH_ALGO,
        "local_assets": list(plan.local_assets),
        "managed_settings": managed_settings,
        "managed_hashes": managed_hashes,
        "managed_fingerprints": managed_fingerprints,
    }
    write_text(manifest_path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return manifest_path


def apply_sync_plan(plan: SyncPlan, allow_dirty_target: bool = False) -> Path:
    manual_operations = [
        operation.path for operation in plan.operations if operation.action == "manual"
    ]
    if manual_operations:
        paths = ", ".join(manual_operations)
        raise RuntimeError(
            f"Sync plan requires manual reconciliation before apply: {paths}."
        )

    if (
        plan.target_dirty
        and not allow_dirty_target
        and any(
            operation.action
            in {"create", "update", "rename", "ensure", "rebuild", "delete"}
            for operation in plan.operations
        )
    ):
        raise RuntimeError(
            "Target repository is dirty. Re-run with --allow-dirty-target if this is intentional."
        )

    for operation in plan.operations:
        target_path = plan.target_root / operation.path
        if operation.action in {"create", "update"}:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if operation.path == LESSONS_PATH:
                if plan.generated_lessons is None:
                    raise RuntimeError(
                        "Generated LESSONS_LEARNED.md content missing from sync plan."
                    )
                write_text(target_path, plan.generated_lessons)
            elif operation.path in CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES:
                source_path = (
                    plan.source_root
                    / CONSUMER_LOCAL_KNOWLEDGE_TEMPLATES[operation.path]
                )
                copy2(source_path, target_path)
            else:
                source_path = plan.source_root / operation.path
                copy2(source_path, target_path)
        elif operation.action == "rename" and operation.path in {
            ARCHITECTURE_PATH,
            REPOSITORY_CONTEXT_PATH,
        }:
            legacy_candidates = {
                ARCHITECTURE_PATH: ARCHITECTURE_LEGACY_PATHS,
                REPOSITORY_CONTEXT_PATH: REPOSITORY_CONTEXT_LEGACY_PATHS,
            }[operation.path]
            existing_legacy_paths = [
                plan.target_root / legacy_path
                for legacy_path in legacy_candidates
                if (plan.target_root / legacy_path).exists()
            ]
            if len(existing_legacy_paths) != 1:
                raise RuntimeError(
                    f"Sync plan requested rename for {operation.path}, but no unique legacy source path is available."
                )
            if target_path.exists():
                raise RuntimeError(
                    f"Sync plan requested rename for {operation.path}, but the canonical target path already exists."
                )
            legacy_path = existing_legacy_paths[0]
            target_path.parent.mkdir(parents=True, exist_ok=True)
            legacy_path.rename(target_path)
            cleanup_empty_parents(legacy_path, plan.target_root)
        elif operation.action == "delete":
            if target_path.exists():
                target_path.unlink()
                cleanup_empty_parents(target_path, plan.target_root)
        elif operation.action == "ensure" and operation.path == TARGET_GITIGNORE_PATH:
            if plan.generated_gitignore is None:
                raise RuntimeError(
                    "Generated .gitignore content missing from sync plan."
                )
            write_text(target_path, plan.generated_gitignore)
        elif operation.action == "ensure" and operation.path == VSCODE_SETTINGS_PATH:
            if target_path.exists():
                current = read_text(target_path)
                updated = apply_managed_vscode_copilot_settings(current)
            else:
                updated = render_minimal_vscode_settings_jsonc()
            write_text(target_path, updated)
        elif operation.action == "rebuild" and operation.path == INVENTORY_PATH:
            write_text(target_path, plan.generated_inventory)

    manifest_path = write_sync_manifest(plan)
    clear_sync_plan(plan)
    return manifest_path


def clear_sync_plan(plan: SyncPlan) -> None:
    plan_path = plan.target_root / SYNC_PLAN_PATH
    if not plan_path.exists():
        return
    plan_path.unlink()
    cleanup_empty_parents(plan_path, plan.target_root)


def cleanup_empty_parents(path: Path, stop_at: Path) -> None:
    current = path.parent
    while current != stop_at and current.exists():
        if any(current.iterdir()):
            return
        current.rmdir()
        current = current.parent
