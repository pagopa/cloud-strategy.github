from __future__ import annotations

import pytest
from lib.jsonc import (
    JsoncParseError,
    apply_managed_vscode_copilot_settings,
    consume_jsonc_string,
    parse_jsonc_root_object,
)


def test_parse_jsonc_root_object_handles_comments_and_nested_members() -> None:
    text = (
        "{\n"
        "  // Root comment\n"
        '  "github.copilot.chat.codeGeneration.useInstructionFiles": true,\n'
        '  "chat.instructionsFilesLocations": {\n'
        "    /* nested comment */\n"
        '    ".github/instructions": true\n'
        "  }\n"
        "}\n"
    )

    root = parse_jsonc_root_object(text)

    assert [member.key for member in root.members] == [
        "github.copilot.chat.codeGeneration.useInstructionFiles",
        "chat.instructionsFilesLocations",
    ]
    assert root.members[1].object_value is not None
    assert [member.key for member in root.members[1].object_value.members] == [
        ".github/instructions"
    ]


def test_consume_jsonc_string_decodes_escape_sequences() -> None:
    value, end = consume_jsonc_string('"line\\n\\u0041\\/end"', 0)

    assert value == "line\nA/end"
    assert end == len('"line\\n\\u0041\\/end"')


def test_apply_managed_vscode_copilot_settings_merges_boolean_values() -> None:
    original = (
        "{\n"
        '  "github.copilot.chat.codeGeneration.useInstructionFiles": true,\n'
        '  "chat.instructionsFilesLocations": {}\n'
        "}\n"
    )

    updated = apply_managed_vscode_copilot_settings(original)

    assert '"github.copilot.chat.codeGeneration.useInstructionFiles": false' in updated
    assert '".github/instructions": false' in updated


def test_apply_managed_vscode_copilot_settings_rejects_duplicate_keys() -> None:
    duplicate = (
        "{\n"
        '  "github.copilot.chat.codeGeneration.useInstructionFiles": true,\n'
        '  "github.copilot.chat.codeGeneration.useInstructionFiles": false\n'
        "}\n"
    )

    with pytest.raises(JsoncParseError, match="duplicate key"):
        apply_managed_vscode_copilot_settings(duplicate)
