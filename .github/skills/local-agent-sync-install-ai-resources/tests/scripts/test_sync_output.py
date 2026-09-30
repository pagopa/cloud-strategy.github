import json

from sync_output import (
    build_compact_install_output,
    dump_compact_json,
    render_doctor_report,
    render_install_report,
    render_sync_report,
)

DONE_NEXT_ACTION = {
    "action": "done",
    "allowed": True,
    "requires_explicit_approval": False,
    "command": "",
    "reason": "No work.",
}


def test_install_payload_reports_linked_and_unlinked_without_bisync() -> None:
    compact = build_compact_install_output(
        {
            "mode": "plan",
            "validation": "ok",
            "linked": ["/home/.agents/skills/alpha"],
            "unlinked": ["/home/.agents/skills/removed"],
            "operations": [],
        }
    )

    assert compact["counts"]["linked"] == 1
    assert compact["counts"]["unlinked"] == 1
    assert "bisync" not in compact


def test_render_install_report_omits_empty_sections_and_uses_emoji_headings() -> None:
    report = render_install_report(
        {
            "mode": "plan",
            "selected_targets": ["skills"],
            "status": "ok",
            "validation": "ok",
            "blocked_codes": [],
            "operations": [],
            "source_resources_considered": 0,
            "state_path": "/tmp/state",
            "next_action": DONE_NEXT_ACTION,
        }
    )

    assert "🚦 Status:" in report
    assert "## 🧭 Summary" in report
    assert "## 🛠️ Changes" not in report
    assert "## ✅ Completed" not in report
    assert "## ⚠️ Attention" not in report
    assert "## 🔎 Validation" in report
    assert "## ➡️ Next" in report


def test_render_doctor_report_omits_readiness_when_everything_is_ok() -> None:
    report = render_doctor_report(
        {
            "selected_targets": ["skills"],
            "status": "ok",
            "validation": "ok",
            "checks": [
                {
                    "name": "runtime root",
                    "path": "/tmp/home/.agents/skills",
                    "status": "ok",
                }
            ],
            "state_path": "/tmp/state",
            "next_action": DONE_NEXT_ACTION,
        }
    )

    assert "🚦 Status:" in report
    assert "## 🧭 Summary" in report
    assert "## 🩺 Readiness" not in report
    assert "## 🔎 Validation" in report
    assert "## ➡️ Next" in report


def test_render_sync_report_omits_empty_action_sections() -> None:
    report = render_sync_report(
        {
            "status": "done",
            "reason": "No work.",
            "install": {
                "selected_targets": ["skills"],
                "operations": [],
                "validation": "ok",
                "state_path": "/tmp/state",
                "manifest_path": "/tmp/manifest",
            },
            "next_action": DONE_NEXT_ACTION,
        }
    )

    assert "🚦 Status:" in report
    assert "## 🧭 Summary" in report
    assert "## 🚀 Auto-applied" not in report
    assert "## 📋 Planned changes" not in report
    assert "## ⛔ Stopped on" not in report
    assert "## 🔎 Validation" in report
    assert "## ➡️ Next" in report
    assert "bisync" not in report


def test_compact_install_output_is_single_line_and_bounded() -> None:
    payload = {
        "mode": "plan",
        "validation": "blocked",
        "selected_targets": ["skills", "codex"],
        "source_resources_considered": 2,
        "copied": ["/very/long/home/path/internal-one"],
        "skipped": ["skip-one"],
        "blocked": ["/very/long/home/path/internal-two"],
        "blocked_codes": ["target-exists-unmanaged"],
        "next_action": {
            "action": "resolve_blockers",
            "requires_explicit_approval": True,
        },
        "operations": [
            {
                "action": "copy",
                "path": "/very/long/home/path/internal-one",
                "resource_id": "internal-one",
                "reason": "verbose reason omitted from compact output",
            },
            {
                "action": "blocked",
                "path": "/very/long/home/path/internal-two",
                "resource_id": "internal-two",
                "code": "target-exists-unmanaged",
                "reason": "verbose reason omitted from compact output",
            },
        ],
    }

    compact = build_compact_install_output(payload)
    line = dump_compact_json(compact)

    assert "\n" not in line
    assert json.loads(line)["next"] == "resolve_blockers"
    assert compact["counts"]["blocked"] == 1
    assert compact["changes"] == [
        {"action": "copy", "resource": "internal-one"},
        {
            "action": "blocked",
            "code": "target-exists-unmanaged",
            "resource": "internal-two",
        },
    ]


def test_agents_md_source_blocker_has_specific_operator_guidance() -> None:
    report = render_doctor_report(
        {
            "selected_targets": ["agents.md"],
            "validation": "blocked",
            "checks": [],
            "blocked_codes": ["source-invalid-agents-md"],
            "next_action": {"action": "resolve_blockers"},
        }
    )

    assert "Root AGENTS.md cannot produce the portable global baseline." in report
    assert "Manual review required." not in report
