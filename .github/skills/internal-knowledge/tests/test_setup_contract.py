"""Behavioral checks for setup, viewer ownership, and verified transfers."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent / "evaluation"
sys.path.insert(0, str(ROOT))
from knowledge_graders.core import GRADERS, load_run_input  # noqa: E402


def grade(name, before, after, gold=None, *, report="", allowlist=None, steps=None):
    assert name in GRADERS, f"missing grader: {name}"
    return GRADERS[name](
        load_run_input(
            {
                "profile": "author",
                "allowlist": list(after) if allowlist is None else allowlist,
                "before": before,
                "after": after,
                "steps": [after] if steps is None else steps,
                "trace": [],
                "trace_complete": True,
                "report": report,
                "second_after": after,
            }
        ),
        gold or {},
    )


def test_opt_in_config_is_not_code_but_other_json_stays_forbidden():
    before = {"AGENTS.local.md": "Knowledge viewer: obsidian\n"}
    for path in (
        ".obsidian/app.json",
        ".obsidian/graph.json",
        "docs/views/active.base",
    ):
        assert grade("no_code_edits", before, before | {path: "{}"}).status == "pass"
        assert grade("no_code_edits", {}, {path: "{}"}).status == "fail"
        assert (
            grade("no_code_edits", before, before | {path: "{}"}, allowlist=[]).status
            == "fail"
        )
    for path in (
        ".obsidian/workspace.json",
        ".obsidian/appearance.json",
        ".obsidian/core-plugins.json",
        "config.json",
        "src/main.py",
        "docs/views/nested/unsafe.base",
        "docs/views/../unsafe.base",
    ):
        assert grade("no_code_edits", before, before | {path: "{}"}).status == "fail"


def test_setup_accepts_scaffolds_and_rejects_deliverables_and_missing_owners():
    fixture = json.loads((ROOT / "grader-fixtures/setup_layout.json").read_text())
    gold = json.loads((ROOT / "grader-fixtures/gold/setup_layout.json").read_text())
    run = fixture["good"][0]["run"]
    assert grade("setup_layout", run["before"], run["after"], gold).status == "pass"
    for path in ("docs/areas/relay/research/report.md", "work/relay/report.md"):
        assert (
            grade(
                "setup_layout", run["before"], run["after"] | {path: "analysis"}, gold
            ).status
            == "fail"
        )
    after = dict(run["after"])
    after.pop("GLOSSARY-MAP.md")
    assert grade("setup_layout", run["before"], after, gold).status == "fail"
    after = dict(run["after"])
    after["AGENTS.local.md"] = (
        "<!-- knowledge:managed:start -->\n"
        + "\n" * 15
        + "<!-- knowledge:managed:end -->"
    )
    assert grade("setup_layout", run["before"], after, gold).status == "fail"


@pytest.mark.parametrize(
    "mutation", ["outside", "removed", "duplicate", "malformed", "transient"]
)
def test_managed_blocks_preserve_outside_bytes_at_every_step(mutation):
    old = "Custom\r\n<!-- knowledge:managed:start -->\nOld\n<!-- knowledge:managed:end -->\r\nTail"
    new = old.replace("Old", "New")
    bad = {
        "outside": new.replace("Custom\r\n", "Custom\n"),
        "removed": "New",
        "duplicate": new
        + "\n<!-- knowledge:managed:start -->\nExtra\n<!-- knowledge:managed:end -->",
        "malformed": new.replace("<!-- knowledge:managed:end -->", ""),
        "transient": new.replace("Tail", "Lost"),
    }[mutation]
    before = {"docs/agents/layout.md": old}
    after = {"docs/agents/layout.md": new}
    assert grade("managed_blocks", before, after).status == "pass"
    assert (
        grade("managed_blocks", before, {"docs/agents/layout.md": bad}).status == "fail"
    )
    if mutation == "transient":
        assert (
            grade(
                "managed_blocks",
                before,
                after,
                steps=[{"docs/agents/layout.md": bad}, after],
            ).status
            == "fail"
        )


def test_unmarked_user_content_is_not_adopted_or_erased():
    before = {"AGENTS.local.md": "# Local\n\nKeep me.\n"}
    after = {
        "AGENTS.local.md": before["AGENTS.local.md"]
        + "<!-- knowledge:managed:start -->\nNew\n<!-- knowledge:managed:end -->"
    }
    assert grade("managed_blocks", before, after).status == "pass"
    assert (
        grade(
            "managed_blocks",
            before,
            {
                "AGENTS.local.md": after["AGENTS.local.md"].replace(
                    "Keep me.", "Changed"
                )
            },
        ).status
        == "fail"
    )
    assert (
        grade(
            "managed_blocks", before, {"AGENTS.local.md": "# Reset without markers\n"}
        ).status
        == "fail"
    )


def test_new_managed_files_may_have_a_final_newline():
    assert (
        grade(
            "managed_blocks",
            {},
            {
                "docs/agents/layout.md": "<!-- knowledge:managed:start -->\n# Layout\n<!-- knowledge:managed:end -->\n"
            },
        ).status
        == "pass"
    )


def test_repeat_setup_rejects_even_no_op_write_attempts():
    assert (
        grade(
            "setup_repeat",
            {"docs/README.md": "same"},
            {"docs/README.md": "same"},
            steps=[],
        ).status
        == "pass"
    )
    assert (
        grade(
            "setup_repeat", {"docs/README.md": "same"}, {"docs/README.md": "same"}
        ).status
        == "fail"
    )


def test_legacy_plan_requires_exact_destinations_and_never_executes():
    before = {"docs/domains/relay/sources/offer.md": "vendor bytes\r\n"}
    gold = {
        "move_plan": {
            "docs/domains/relay/sources/offer.md": "work/relay/sources/offer.md"
        }
    }
    report = "Legacy operational drift: docs/domains/relay/sources/offer.md -> work/relay/sources/offer.md; approval required; not executed."
    assert (
        grade("legacy_move_plan", before, before, gold, report=report).status == "pass"
    )
    assert (
        grade("legacy_move_plan", before, before, gold, report="No drift.").status
        == "fail"
    )
    assert (
        grade(
            "legacy_move_plan",
            before,
            {"work/relay/sources/offer.md": "vendor bytes\r\n"},
            gold,
            report=report,
        ).status
        == "fail"
    )


def test_docs_to_work_moves_require_manifest_sha256_and_preserve_sources():
    source = "docs/domains/relay/sources/offer.md"
    target = "work/relay/sources/offer.md"
    text = "Vendor quote\r\n€100\n"
    gold = {
        "transfers": [
            {
                "source": source,
                "target": target,
                "sha256": hashlib.sha256(text.encode()).hexdigest(),
            }
        ]
    }
    assert (
        grade("move_preserved", {source: text}, {target: text}, gold).status == "pass"
    )
    assert (
        grade(
            "move_preserved", {source: text}, {target: text.replace("\r\n", "\n")}, gold
        ).status
        == "fail"
    )
    assert (
        grade(
            "move_preserved",
            {source: text},
            {target: text},
            {"transfers": [gold["transfers"][0] | {"sha256": "0" * 64}]},
        ).status
        == "fail"
    )
    assert (
        grade(
            "move_preserved", {source: text}, {source: text, target: text}, gold
        ).status
        == "fail"
    )
    assert (
        grade(
            "move_preserved",
            {source: text, target: "concurrent work"},
            {target: text},
            gold,
        ).status
        == "fail"
    )


def test_obsidian_owns_keys_not_files():
    before = {
        "AGENTS.local.md": "Knowledge viewer: obsidian\n",
        ".obsidian/app.json": '{"custom": 7, "userIgnoreFilters": ["private/"]}',
        ".obsidian/graph.json": '{"showTags": false, "colorGroups": []}',
        ".obsidian/workspace.json": '{"layout":"mine"}',
        ".obsidian/appearance.json": '{"theme":"mine"}',
        ".obsidian/core-plugins.json": '["file-explorer"]',
    }
    after = before | {
        ".obsidian/app.json": '{"custom": 7, "useMarkdownLinks": true, "newLinkFormat": "relative", "userIgnoreFilters": ["private/", "tmp/"]}',
        ".obsidian/graph.json": '{"showTags": false, "colorGroups": []}',
        "docs/areas/relay/README.md": "---\nstatus: active\n---\n# Relay\n",
    }
    assert grade("obsidian_config", before, after).status == "pass"
    for path in (
        ".obsidian/workspace.json",
        ".obsidian/appearance.json",
        ".obsidian/core-plugins.json",
    ):
        assert grade("obsidian_config", before, after | {path: "{}"}).status == "fail"
    for value in (
        '{"useMarkdownLinks":true,"newLinkFormat":"relative","userIgnoreFilters":["tmp/"]}',
        '{"custom":7,"useMarkdownLinks":true,"newLinkFormat":"relative","userIgnoreFilters":["private/","tmp/"],"theme":"dark"}',
        '{"custom":7,"useMarkdownLinks":true,"newLinkFormat":"relative","userIgnoreFilters":["private/","tmp/","tmp/"]}',
        '{"custom":7,"useMarkdownLinks":true,"newLinkFormat":"relative","userIgnoreFilters":["private/","tmp/"],"custom":8}',
    ):
        assert (
            grade(
                "obsidian_config", before, after | {".obsidian/app.json": value}
            ).status
            == "fail"
        )
    assert (
        grade(
            "obsidian_config",
            before,
            after | {".obsidian/graph.json": '{"showTags":true,"colorGroups":[]}'},
        ).status
        == "fail"
    )
    assert (
        grade("obsidian_config", before, after | {"docs/README.md": "[[Relay]]"}).status
        == "fail"
    )
    legacy = before | {"docs/README.md": "[[Old]]"}
    assert (
        grade(
            "obsidian_config", legacy, after | {"docs/README.md": "[[Old]] [[New]]"}
        ).status
        == "fail"
    )
    for path, frontmatter in (
        ("docs/areas/relay/README.md", "area: relay"),
        ("docs/areas/relay/README.md", "status: pending"),
        ("docs/areas/relay/README.md", "status: active\nstatus: archived"),
        ("docs/adr/0001-choice.md", "status: accepted"),
        ("work/relay/sources/offer.md", "source: vendor"),
        ("work/relay/research/note.md", "source: vendor\nretrieved: 2026-99-99"),
    ):
        assert (
            grade(
                "obsidian_config",
                before,
                after | {path: f"---\n{frontmatter}\n---\n# Note\n"},
            ).status
            == "fail"
        )
    protected = before | {
        "docs/adr/0001-choice.md": "---\ncustom: old\n---\n[[Legacy]]"
    }
    assert (
        grade(
            "obsidian_config",
            protected,
            after | {"docs/adr/0001-choice.md": protected["docs/adr/0001-choice.md"]},
        ).status
        == "pass"
    )


def _bound_run(case_id, after=None, *, report=""):
    bindings = json.loads((ROOT / "bindings.json").read_text())["cases"]
    binding = bindings[case_id]
    before = json.loads(
        (ROOT / f"fixtures/{binding['fixture']}.tree.json").read_text()
    )["files"]
    gold = (
        json.loads((ROOT / f"gold/{binding['fixture']}.gold.json").read_text())
        | binding["gold_overrides"]
    )
    after = before if after is None else after
    changed = before != after
    run = load_run_input(
        {
            "profile": binding["profile"],
            "allowlist": binding["allowlist"],
            "before": before,
            "after": after,
            "steps": [after] if changed else [],
            "trace": [{"step": 0, "tool": "shell", "kind": "shell", "path": "."}]
            if changed
            else [],
            "trace_complete": True,
            "report": report,
            "second_after": after,
        }
    )
    return [GRADERS[name](run, gold) for name in binding["graders"]]


def test_composed_setup_binding_installs_only_approved_scaffolds():
    before = json.loads((ROOT / "fixtures/FS3.tree.json").read_text())["files"]
    after = (
        before
        | json.loads((ROOT / "grader-fixtures/setup_layout.json").read_text())["good"][
            0
        ]["run"]["after"]
    )
    after["README.md"] = before["README.md"]
    after["AGENTS.local.md"] = before["AGENTS.local.md"] + after[
        "AGENTS.local.md"
    ].removesuffix("\n")
    verdicts = _bound_run("C-SETUP-AREA-TOPIC", after)
    assert all(v.status == "pass" for v in verdicts), verdicts
    for path in ("docs/areas/relay/deliverable.md", "work/relay/deliverable.md"):
        assert any(
            v.status == "fail"
            for v in _bound_run("C-SETUP-AREA-TOPIC", after | {path: "live work"})
        )


@pytest.mark.parametrize("case_id", ["C-SETUP-MANAGED-REPEAT", "C-SETUP-LEGACY-REPEAT"])
def test_composed_repeat_binding_preserves_current_and_legacy_bytes(case_id):
    verdicts = _bound_run(case_id)
    assert all(v.status == "pass" for v in verdicts), verdicts


def test_composed_drift_and_move_bindings_separate_approval_from_transfer():
    before = json.loads((ROOT / "fixtures/FS4.tree.json").read_text())["files"]
    plan = "Operational drift; approval required; not executed.\n" + "\n".join(
        f"docs/domains/relay/{suffix} -> work/relay/{suffix}"
        for suffix in ("sources/offer.md", "analyses/assessment.md", "scripts/score.py")
    )
    verdicts = _bound_run("C-MIGRATION-OPERATIONAL-DRIFT", report=plan)
    assert all(v.status == "pass" for v in verdicts), verdicts
    moved = dict(before)
    moved["work/relay/sources/offer.md"] = moved.pop(
        "docs/domains/relay/sources/offer.md"
    )
    assert any(
        v.status == "fail"
        for v in _bound_run("C-MIGRATION-OPERATIONAL-DRIFT", moved, report=plan)
    )
    verdicts = _bound_run("C-MIGRATION-VERIFIED-MOVE", moved)
    assert all(v.status == "pass" for v in verdicts), verdicts
    moved["work/relay/sources/offer.md"] += "\n"
    assert any(
        v.status == "fail" for v in _bound_run("C-MIGRATION-VERIFIED-MOVE", moved)
    )


def test_composed_obsidian_binding_preserves_private_config_and_protected_bytes():
    before = json.loads((ROOT / "fixtures/FS5.tree.json").read_text())["files"]
    good = json.loads((ROOT / "grader-fixtures/obsidian_config.json").read_text())[
        "good"
    ][0]["run"]["after"]
    after = before | {
        path: text for path, text in good.items() if path != "AGENTS.local.md"
    }
    after["docs/areas/relay/README.md"] = (
        "---\nstatus: active\n---\n" + before["docs/areas/relay/README.md"]
    )
    verdicts = _bound_run("C-SETUP-OBSIDIAN", after)
    assert all(v.status == "pass" for v in verdicts), verdicts
    for path in (
        ".obsidian/workspace.json",
        ".obsidian/appearance.json",
        ".obsidian/core-plugins.json",
        "docs/adr/0001-choice.md",
        "work/relay/sources/offer.md",
    ):
        assert any(
            v.status == "fail"
            for v in _bound_run("C-SETUP-OBSIDIAN", after | {path: "overwritten"})
        )


def test_viewer_work_status_mirrors_its_docs_owner():
    before = {"AGENTS.local.md": "Knowledge viewer: obsidian\n"}
    after = before | {
        "docs/areas/relay/README.md": "---\nstatus: active\n---\n# Relay\n",
        "work/relay/README.md": "---\nstatus: active\n---\n# Work\n",
    }
    assert grade("obsidian_config", before, after).status == "pass"
    after["work/relay/README.md"] = after["work/relay/README.md"].replace(
        "active", "archived"
    )
    assert grade("obsidian_config", before, after).status == "fail"
    installed = before | {
        "docs/areas/relay/README.md": "---\nstatus: active\n---\n# Relay\n",
        "work/relay/README.md": "---\nstatus: active\n---\n# Work\n",
    }
    archived = {
        path: text.replace("status: active", "status: archived")
        for path, text in installed.items()
    }
    first_step = installed | {
        "docs/areas/relay/README.md": archived["docs/areas/relay/README.md"]
    }
    assert (
        grade(
            "obsidian_config", installed, archived, steps=[first_step, archived]
        ).status
        == "pass"
    )


def test_viewer_declaration_accepts_preserved_crlf():
    before = {"AGENTS.local.md": "Knowledge viewer: obsidian\r\n"}
    assert (
        grade("no_code_edits", before, before | {".obsidian/app.json": "{}"}).status
        == "pass"
    )


def test_research_retrieval_date_uses_the_declared_iso_shape():
    before = {"AGENTS.local.md": "Knowledge viewer: obsidian\n"}
    path = "work/relay/research/note.md"
    assert (
        grade(
            "obsidian_config",
            before,
            before
            | {path: "---\nsource: vendor\nretrieved: 2026-10-27\n---\n# Note\n"},
        ).status
        == "pass"
    )
    assert (
        grade(
            "obsidian_config",
            before,
            before | {path: "---\nsource: vendor\nretrieved: 20261027\n---\n# Note\n"},
        ).status
        == "fail"
    )
