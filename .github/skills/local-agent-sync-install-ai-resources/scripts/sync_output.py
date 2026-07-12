from __future__ import annotations

import json
from collections.abc import Iterable

BLOCKER_REASON_MAP: dict[str, str] = {
    "unknown-target": "The selected target is not supported.",
    "unsupported-family": "The selected resource family is not supported for this target.",
    "docs-unverified": "Runtime support is not documented enough for apply.",
    "missing-target-root": "A required target root directory is missing.",
    "needs-directory-create": "A target directory must be created with explicit approval.",
    "permission-denied": "Permissions are not sufficient for this operation.",
    "unsafe-home-path": "A resolved path escaped the allowed home root.",
    "symlink-not-allowed": "A disallowed symlink boundary was detected.",
    "manifest-missing": "Manifest state is missing for this mode.",
    "manifest-corrupt": "Manifest state is corrupt and cannot be trusted.",
    "target-exists-unmanaged": "Target content exists but is not manifest-managed.",
    "target-modified-managed": "Manifest-managed content diverged from the recorded hash.",
    "source-missing": "A catalog source path does not exist.",
    "source-invalid-skill": "A skill bundle is missing required files.",
    "stale-managed": "A previously managed resource is stale and pending prune review.",
    "prune-not-approved": "Prune was not approved for stale managed resources.",
    "stale-content-drifted": "A stale managed resource drifted and cannot be removed safely.",
    "stale-path-unresolvable": "A stale managed path cannot be resolved safely.",
    "symlink-unsupported": "The runtime cannot create symbolic links.",
    "link-target-missing": "A managed link target is missing or broken.",
    "link-target-mismatch": "A managed link points to a different checkout.",
    "retire-target-overlap": "A target was selected as both active and retired.",
}

REPORT_TABLE_ROW_LIMIT = 8
REPORT_SECTION_EMOJIS: dict[str, str] = {
    "Summary": "🧭",
    "Auto-applied": "🚀",
    "Planned changes": "📋",
    "Stopped on": "⛔",
    "Changes": "🛠️",
    "Completed": "✅",
    "Attention": "⚠️",
    "Validation": "🔎",
    "Readiness": "🩺",
    "Next": "➡️",
}


def dump_compact_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def build_compact_install_output(payload: dict[str, object]) -> dict[str, object]:
    next_action = payload.get("next_action")
    compact: dict[str, object] = {
        "mode": payload.get("mode"),
        "status": payload.get("validation", payload.get("status")),
        "targets": _as_string_list(payload.get("selected_targets")),
        "next": _next_action_name(next_action),
        "approval": _next_action_requires_approval(next_action),
        "counts": {
            "source": _count_value(payload.get("source_resources_considered")),
            "linked": _count_value(payload.get("linked")),
            "unlinked": _count_value(payload.get("unlinked")),
            "copy": _count_value(payload.get("copied")),
            "skip": _count_value(payload.get("skipped")),
            "blocked": _count_value(payload.get("blocked")),
            "conflict": _count_value(payload.get("conflicts")),
            "missing_dir": _count_value(payload.get("missing_dirs")),
            "residual": _count_value(payload.get("residual_drift")),
            "unsupported": _count_unsupported_families(
                payload.get("unsupported_families_by_target")
            ),
        },
    }
    blockers = _as_string_list(payload.get("blocked_codes"))
    if blockers:
        compact["blockers"] = blockers
    changes = _install_change_evidence(payload, limit=4)
    if changes:
        compact["changes"] = changes
    if isinstance(payload.get("error"), str):
        compact["error"] = payload["error"]
    return compact


def render_sync_report(payload: dict[str, object]) -> str:
    install_payload = payload.get("install")
    install = install_payload if isinstance(install_payload, dict) else payload
    status = str(payload.get("status") or install.get("validation") or "unknown")
    reason = str(payload.get("reason") or "")
    lines = [
        f"🚦 Status: sync | status={status} | targets={_join_or_none(_as_string_list(install.get('selected_targets')))} | reason={reason}",
        "",
        *_report_section("Summary"),
        *_bullet_lines(
            [
                f"Linked resources: {_count_value(install.get('linked'))}",
                f"Unlinked resources: {_count_value(install.get('unlinked'))}",
                f"Copied translated agents: {_count_value(install.get('copied'))}",
                f"Unchanged resources: {_count_value(install.get('skipped'))}",
                f"Blockers: {_count_value(install.get('blocked'))}",
            ]
        ),
        "",
        *_report_section("Validation"),
        *_table_lines(
            ["Check", "Result"],
            [["Install", status], ["Blockers", _join_or_none(_as_string_list(install.get("blocked_codes"))) or "none"]],
        ),
        "",
        *_report_section("Next"),
        *_table_lines([["Field", "Value"]][0], [["Action", _next_action_name(payload.get("next_action"))]]),
    ]
    return "\n".join(lines).strip() + "\n"


def render_install_report(payload: dict[str, object]) -> str:
    status = str(payload.get("validation") or payload.get("status") or "unknown")
    lines = [
        f"🚦 Status: install | status={status} | targets={_join_or_none(_as_string_list(payload.get('selected_targets')))}",
        "",
        *_report_section("Summary"),
        *_bullet_lines(
            [
                f"Linked resources: {_count_value(payload.get('linked'))}",
                f"Unlinked resources: {_count_value(payload.get('unlinked'))}",
                f"Copied translated agents: {_count_value(payload.get('copied'))}",
                f"Unchanged resources: {_count_value(payload.get('skipped'))}",
                f"Blockers: {_count_value(payload.get('blocked'))}",
            ]
        ),
        "",
    ]
    operations = payload.get("operations")
    rows = _operation_rows(operations)
    if rows:
        lines.extend(_report_section("Changes"))
        lines.extend(_table_lines(["Action", "Resource", "Reason"], _bounded_rows(rows)))
        lines.append("")
    blockers = _blocker_rows(payload)
    if blockers:
        lines.extend(_report_section("Attention"))
        lines.extend(_table_lines(["Code", "Meaning", "Next action"], blockers))
        lines.append("")
    lines.extend(_report_section("Validation"))
    lines.extend(_table_lines(["Check", "Result"], [["Install", status]]))
    lines.append("")
    lines.extend(_report_section("Next"))
    lines.extend(_table_lines(["Field", "Value"], [["Action", _next_action_name(payload.get("next_action"))]]))
    return "\n".join(lines).strip() + "\n"


def render_doctor_report(payload: dict[str, object]) -> str:
    status = str(payload.get("validation") or payload.get("status") or "unknown")
    lines = [
        f"🚦 Status: doctor | status={status} | targets={_join_or_none(_as_string_list(payload.get('selected_targets')))}",
        "",
        *_report_section("Summary"),
    ]
    checks = payload.get("checks")
    rows = []
    if isinstance(checks, Iterable) and not isinstance(checks, (str, bytes, dict)):
        for check in checks:
            if isinstance(check, dict):
                rows.append([str(check.get("name", "check")), str(check.get("status", "unknown"))])
    if rows:
        lines.extend(_table_lines(["Check", "Result"], rows))
    blocked = _as_string_list(payload.get("blocked_codes"))
    if blocked:
        lines.extend(("", *_report_section("Readiness")))
        lines.extend(_table_lines(["Code", "Meaning", "Next action"], [[code, _reason(code), "Resolve it, then rerun doctor."] for code in blocked]))
    lines.extend(("", *_report_section("Validation")))
    lines.extend(_table_lines(["Check", "Result"], [["Doctor", status]]))
    lines.extend(("", *_report_section("Next")))
    lines.extend(_table_lines(["Field", "Value"], [["Action", _next_action_name(payload.get("next_action"))]]))
    return "\n".join(lines).strip() + "\n"


def _install_change_evidence(payload: dict[str, object], limit: int = 8) -> list[dict[str, object]]:
    operations = payload.get("operations")
    if not isinstance(operations, list):
        return []
    evidence: list[dict[str, object]] = []
    for operation in operations:
        if not isinstance(operation, dict) or operation.get("action") not in {
            "link", "unlink", "copy", "delete", "blocked", "stale-managed", "mkdir"
        }:
            continue
        path = operation.get("path")
        if not isinstance(path, str) or not path:
            continue
        item: dict[str, object] = {
            "action": operation["action"],
            "resource": operation.get("resource_id") or _compact_path(path),
        }
        if isinstance(operation.get("code"), str) and operation["code"]:
            item["code"] = operation["code"]
        evidence.append(item)
        if len(evidence) >= limit:
            break
    return evidence


def _operation_rows(value: object) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    rows = []
    for operation in value:
        if not isinstance(operation, dict) or operation.get("action") == "skip":
            continue
        rows.append([
            str(operation.get("action", "unknown")),
            str(operation.get("resource_id") or _compact_path(str(operation.get("path", "")))),
            str(operation.get("reason", "")),
        ])
    return rows


def _blocker_rows(payload: dict[str, object]) -> list[list[str]]:
    return [
        [code, _reason(code), "Resolve the blocker, then rerun the same command."]
        for code in _as_string_list(payload.get("blocked_codes"))
    ]


def _reason(code: str) -> str:
    return BLOCKER_REASON_MAP.get(code, "Manual review required.")


def _count_value(value: object) -> int:
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return len(list(value))
    if isinstance(value, int):
        return value
    return 0


def _as_string_list(value: object) -> list[str]:
    if isinstance(value, dict):
        return [str(item) for item in value]
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    return []


def _count_unsupported_families(value: object) -> int:
    if not isinstance(value, dict):
        return 0
    return sum(_count_value(families) for families in value.values())


def _next_action_name(value: object) -> str:
    return str(value.get("action") or "unknown") if isinstance(value, dict) else "unknown"


def _next_action_requires_approval(value: object) -> bool:
    return bool(value.get("requires_explicit_approval")) if isinstance(value, dict) else False


def _install_lane_label() -> str:
    return "repo-to-home install"


def _join_or_none(values: list[str]) -> str:
    return ",".join(values) if values else "none"


def _compact_path(path: str) -> str:
    return path.rsplit("/", 1)[-1] or path


def _report_section(name: str) -> list[str]:
    return [f"## {REPORT_SECTION_EMOJIS.get(name, '')} {name}".rstrip()]


def _bullet_lines(values: list[str]) -> list[str]:
    return [f"- {value}" for value in values]


def _table_lines(headers: list[str], rows: list[list[str]]) -> list[str]:
    if not rows:
        return []
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def _bounded_rows(rows: list[list[str]], label: str = "row") -> list[list[str]]:
    if len(rows) <= REPORT_TABLE_ROW_LIMIT:
        return rows
    omitted = len(rows) - REPORT_TABLE_ROW_LIMIT
    return rows[:REPORT_TABLE_ROW_LIMIT] + [["...", f"{omitted} more {label}(s)", ""]]
