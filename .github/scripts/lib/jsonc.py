from __future__ import annotations

import re
from dataclasses import dataclass

from .shared import VSCODE_COPILOT_SETTINGS


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
    if char == "{":
        object_info, next_cursor = parse_jsonc_object(text, cursor)
        return "object", cursor, next_cursor, object_info, next_cursor
    if char == "[":
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


def ensure_root_boolean_setting(text: str, root: JsoncObjectInfo, key: str) -> str:
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
