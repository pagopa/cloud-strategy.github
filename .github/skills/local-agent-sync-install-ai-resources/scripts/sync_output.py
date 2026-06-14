from __future__ import annotations

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
    "reverse-sync-blocked": "Reverse sync is blocked by policy.",
    "retire-target-overlap": "A target was selected as both active and retired.",
    "bisync-source-missing": "The source skills root is missing or unreadable.",
    "bisync-home-missing": "The home skills root is missing or unreadable.",
    "bisync-repo-dirty": "Repository has uncommitted or untracked changes.",
    "bisync-repo-git-failed": "The dirty repository preflight check failed.",
    "bisync-only-home": "A skill exists only in home and needs manual resolution.",
    "bisync-equal-mtime": "Hashes differ but timestamps are equal, so winner is ambiguous.",
    "bisync-verify-failed": "Post-copy hash verification failed.",
    "bisync-manifest-reconcile-failed": "Manifest reconciliation failed after a verified bisync copy.",
    "bisync-residual-drift": "Post-apply bisync still detected residual drift.",
}


def build_compact_install_output(payload: dict[str, object]) -> dict[str, object]:
    compact: dict[str, object] = {
        "mode": payload.get("mode"),
        "status": payload.get("validation", payload.get("status")),
        "blocked_codes": list(_as_iterable(payload.get("blocked_codes"))),
        "next_action": payload.get("next_action"),
        "next_step": payload.get("next_step"),
        "selected_targets_count": _count_value(payload.get("selected_targets")),
        "retired_targets_count": _count_value(payload.get("retired_targets")),
        "source_resources_considered": payload.get("source_resources_considered"),
        "copied_count": _count_value(payload.get("copied")),
        "skipped_count": _count_value(payload.get("skipped")),
        "blocked_count": _count_value(payload.get("blocked")),
        "conflict_count": _count_value(payload.get("conflicts")),
        "missing_dirs_count": _count_value(payload.get("missing_dirs")),
        "residual_drift_count": _count_value(payload.get("residual_drift")),
        "unsupported_families_count": _count_unsupported_families(
            payload.get("unsupported_families_by_target")
        ),
        "changed_resources": _install_change_evidence(payload),
    }
    _copy_if_present(compact, payload, "state_path")
    _copy_if_present(compact, payload, "manifest_path")
    _copy_if_present(compact, payload, "error")
    return compact


def build_compact_bisync_output(payload: dict[str, object]) -> dict[str, object]:
    verification = payload.get("verification")
    status = None
    if isinstance(verification, dict):
        status = verification.get("status")
    compact: dict[str, object] = {
        "mode": payload.get("mode"),
        "status": status if status is not None else payload.get("status"),
        "blocked_codes": list(_as_iterable(payload.get("blocked_codes"))),
        "next_action": payload.get("next_action"),
        "next_step": payload.get("next_step"),
        "drift_total": _count_value(payload.get("drifts")),
        "direction_counts": _direction_counts(payload.get("drifts")),
        "bucket_counts": _bucket_counts(payload.get("drifts")),
        "changed_resources": _bisync_change_evidence(payload.get("drifts")),
    }
    _copy_if_present(compact, payload, "state_path")
    _copy_if_present(compact, payload, "manifest_path")
    _copy_if_present(compact, payload, "error")
    if isinstance(verification, dict):
        _copy_if_present(compact, verification, "code")
    return compact


def _copy_if_present(
    target: dict[str, object],
    source: dict[str, object],
    key: str,
) -> None:
    if key in source:
        target[key] = source[key]


def _count_value(value: object) -> int:
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return len(list(value))
    return 0


def _as_iterable(value: object) -> Iterable[object]:
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return value
    return ()


def _count_unsupported_families(value: object) -> int:
    if not isinstance(value, dict):
        return 0
    count = 0
    for families in value.values():
        if isinstance(families, Iterable) and not isinstance(families, (str, bytes)):
            count += len(list(families))
    return count


def _direction_counts(drifts: object) -> dict[str, int]:
    counts = {"repo_to_home": 0, "home_to_repo": 0}
    if not isinstance(drifts, Iterable) or isinstance(drifts, (str, bytes, dict)):
        return counts
    for drift in drifts:
        if not isinstance(drift, dict):
            continue
        direction = drift.get("direction")
        if direction == "repo-to-home":
            counts["repo_to_home"] += 1
        elif direction == "home-to-repo":
            counts["home_to_repo"] += 1
        elif direction in counts:
            counts[str(direction)] += 1
    return counts


def _bucket_counts(drifts: object) -> dict[str, int]:
    counts = {"only_repo": 0, "only_home": 0, "equal_mtime": 0}
    if not isinstance(drifts, Iterable) or isinstance(drifts, (str, bytes, dict)):
        return counts
    for drift in drifts:
        if not isinstance(drift, dict):
            continue
        drift_type = drift.get("type")
        if drift_type == "only-repo":
            counts["only_repo"] += 1
        elif drift_type == "only-home":
            counts["only_home"] += 1
        elif drift_type == "equal-mtime":
            counts["equal_mtime"] += 1
    return counts


def _install_change_evidence(payload: dict[str, object], limit: int = 8) -> list[dict[str, object]]:
    operations = payload.get("operations")
    if not isinstance(operations, list):
        return []

    evidence: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    interesting_actions = {"copy", "blocked", "stale-managed", "mkdir", "delete"}
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        action = operation.get("action")
        if action not in interesting_actions:
            continue
        path = operation.get("path")
        if not isinstance(path, str) or not path:
            continue
        key = (str(action), path)
        if key in seen:
            continue
        seen.add(key)
        item: dict[str, object] = {"action": action, "path": path}
        for field in ("resource_id", "code", "reason"):
            value = operation.get(field)
            if isinstance(value, str) and value:
                item[field] = value
        evidence.append(item)
        if len(evidence) >= limit:
            break
    return evidence


def _bisync_change_evidence(drifts: object, limit: int = 8) -> list[dict[str, object]]:
    if not isinstance(drifts, Iterable) or isinstance(drifts, (str, bytes, dict)):
        return []

    evidence: list[dict[str, object]] = []
    for drift in drifts:
        if not isinstance(drift, dict):
            continue
        item: dict[str, object] = {}
        for field in ("skill", "direction", "type", "winner", "reason"):
            value = drift.get(field)
            if isinstance(value, str) and value:
                item[field] = value
        blocked_codes = drift.get("blocked_codes")
        if isinstance(blocked_codes, Iterable) and not isinstance(blocked_codes, (str, bytes, dict)):
            item["blocked_codes"] = list(blocked_codes)
        if item:
            evidence.append(item)
        if len(evidence) >= limit:
            break
    return evidence


def render_install_report(payload: dict[str, object]) -> str:
    mode = str(payload.get("mode") or "plan")
    targets = _as_string_list(payload.get("selected_targets"))
    blocked_codes = _as_string_list(payload.get("blocked_codes"))
    status = str(payload.get("validation") or payload.get("status") or "unknown")

    lines: list[str] = []
    lines.append(
        f"Status: mode={mode}; targets={_join_or_none(targets)}; status={status}; blockers={len(blocked_codes)}"
    )
    lines.append("")

    lines.extend(_report_section("Current State"))
    lines.extend(
        _table_lines(
            ["Field", "Value"],
            [
                ["Mode", mode],
                ["Selected targets", _join_or_none(targets)],
                ["Retired targets", _join_or_none(_as_string_list(payload.get("retired_targets")))],
                ["Source resources considered", str(payload.get("source_resources_considered") or 0)],
                ["Blocked code count", str(len(blocked_codes))],
            ],
        )
    )
    lines.append("")

    planned_rows = _install_planned_rows(payload)
    lines.extend(_report_section("Differences Or Planned Work"))
    lines.extend(
        _table_lines(
            ["Resource or path", "Lane", "Planned action", "Why this will change", "Evidence or winner"],
            planned_rows,
            none_row=["none", "install", "no-op", "No planned changes.", "none"],
        )
    )
    lines.append("")

    completed_rows = _install_completed_rows(payload)
    lines.extend(_report_section("Actions Completed"))
    lines.extend(
        _table_lines(
            ["Resource or path", "Action performed", "Why it was done", "Result", "Verification"],
            completed_rows,
            none_row=["none", "no-op", "No actions completed.", "none", "none"],
        )
    )
    lines.append("")

    blocker_rows = _install_blocker_rows(payload)
    lines.extend(_report_section("Blockers And Skips"))
    lines.extend(
        _table_lines(
            ["Code or status", "Resource or path", "Why blocked or skipped", "Required user action"],
            blocker_rows,
            none_row=["none", "none", "No blockers or skips.", "none"],
        )
    )
    lines.append("")

    lines.extend(_report_section("Validation"))
    validation_rows = [["Validation status", status]]
    state_path = payload.get("state_path")
    if isinstance(state_path, str) and state_path:
        validation_rows.append(["State path", state_path])
    manifest_path = payload.get("manifest_path")
    if isinstance(manifest_path, str) and manifest_path:
        validation_rows.append(["Manifest path", manifest_path])
    lines.extend(_table_lines(["Check", "Result"], validation_rows))
    lines.append("")

    lines.extend(_report_section("Remaining Work"))
    remaining_rows = _remaining_work_rows(payload)
    lines.extend(
        _table_lines(
            ["Item", "Why it remains", "Required follow-up"],
            remaining_rows,
            none_row=["none", "No remaining work.", "none"],
        )
    )
    lines.append("")

    lines.extend(_report_section("Next Action"))
    lines.extend(_next_action_table(payload.get("next_action"), payload.get("next_step")))
    return "\n".join(lines).strip() + "\n"


def render_bisync_report(payload: dict[str, object]) -> str:
    mode = str(payload.get("mode") or "plan")
    blocked_codes = _as_string_list(payload.get("blocked_codes"))
    drifts = payload.get("drifts")
    drift_total = _count_value(drifts)
    verification = payload.get("verification")
    status = "unknown"
    if isinstance(verification, dict):
        status = str(verification.get("status") or status)

    lines: list[str] = []
    lines.append(
        f"Status: mode={mode}; lane=bisync; status={status}; drift_total={drift_total}; blockers={len(blocked_codes)}"
    )
    lines.append("")

    lines.extend(_report_section("Current State"))
    lines.extend(
        _table_lines(
            ["Field", "Value"],
            [
                ["Mode", mode],
                ["Drift total", str(drift_total)],
                ["Blocked code count", str(len(blocked_codes))],
                ["Verification status", status],
            ],
        )
    )
    lines.append("")

    lines.extend(_report_section("Differences Or Planned Work"))
    lines.extend(
        _table_lines(
            ["Resource or path", "Lane", "Planned action", "Why this will change", "Evidence or winner"],
            _bisync_planned_rows(payload),
            none_row=["none", "bisync", "no-op", "No drift detected.", "none"],
        )
    )
    lines.append("")

    lines.extend(_report_section("Actions Completed"))
    lines.extend(
        _table_lines(
            ["Resource or path", "Action performed", "Why it was done", "Result", "Verification"],
            _bisync_completed_rows(payload),
            none_row=["none", "no-op", "No actions completed.", "none", "none"],
        )
    )
    lines.append("")

    lines.extend(_report_section("Blockers And Skips"))
    lines.extend(
        _table_lines(
            ["Code or status", "Resource or path", "Why blocked or skipped", "Required user action"],
            _bisync_blocker_rows(payload),
            none_row=["none", "none", "No blockers or skips.", "none"],
        )
    )
    lines.append("")

    lines.extend(_report_section("Validation"))
    verification_rows = [["Verification status", status]]
    if isinstance(verification, dict):
        reason = verification.get("reason")
        if isinstance(reason, str) and reason:
            verification_rows.append(["Reason", reason])
        code = verification.get("code")
        if isinstance(code, str) and code:
            verification_rows.append(["Code", code])
    lines.extend(_table_lines(["Check", "Result"], verification_rows))
    lines.append("")

    lines.extend(_report_section("Remaining Work"))
    lines.extend(
        _table_lines(
            ["Item", "Why it remains", "Required follow-up"],
            _remaining_work_rows(payload),
            none_row=["none", "No remaining work.", "none"],
        )
    )
    lines.append("")

    lines.extend(_report_section("Next Action"))
    lines.extend(_next_action_table(payload.get("next_action"), payload.get("next_step")))
    return "\n".join(lines).strip() + "\n"


def _report_section(name: str) -> list[str]:
    return [f"## {name}"]


def _table_lines(
    headers: list[str],
    rows: list[list[str]],
    *,
    none_row: list[str] | None = None,
) -> list[str]:
    output = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    if not rows and none_row is not None:
        rows = [none_row]
    for row in rows:
        padded = row + [""] * (len(headers) - len(row))
        output.append("| " + " | ".join(padded[: len(headers)]) + " |")
    return output


def _join_or_none(values: list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


def _as_string_list(value: object) -> list[str]:
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes, dict)):
        return []
    return [str(item) for item in value]


def _install_planned_rows(payload: dict[str, object]) -> list[list[str]]:
    rows: list[list[str]] = []
    operations = payload.get("operations")
    if not isinstance(operations, list):
        return rows
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        action = str(operation.get("action") or "")
        if action not in {"copy", "mkdir", "delete", "stale-managed"}:
            continue
        path = str(operation.get("path") or operation.get("resource_id") or "unknown")
        reason = str(operation.get("reason") or "policy decision")
        winner = str(operation.get("code") or operation.get("target") or "n/a")
        planned = "copy" if action == "copy" else action
        rows.append([path, "install", planned, reason, winner])
    return rows


def _install_completed_rows(payload: dict[str, object]) -> list[list[str]]:
    rows: list[list[str]] = []
    if str(payload.get("mode") or "") != "apply":
        return rows
    operations = payload.get("operations")
    if not isinstance(operations, list):
        return rows
    for operation in operations:
        if not isinstance(operation, dict):
            continue
        action = str(operation.get("action") or "")
        if action not in {"copy", "delete", "skip", "mkdir"}:
            continue
        path = str(operation.get("path") or operation.get("resource_id") or "unknown")
        reason = str(operation.get("reason") or "applied by plan")
        result = "ok" if action != "skip" else "skipped"
        verification = "hash-match" if action in {"copy", "delete"} else "n/a"
        rows.append([path, action, reason, result, verification])
    return rows


def _install_blocker_rows(payload: dict[str, object]) -> list[list[str]]:
    rows: list[list[str]] = []
    operations = payload.get("operations")
    if isinstance(operations, list):
        for operation in operations:
            if not isinstance(operation, dict):
                continue
            action = str(operation.get("action") or "")
            if action not in {"blocked", "skip"}:
                continue
            code = str(operation.get("code") or ("skipped" if action == "skip" else "unknown"))
            path = str(operation.get("path") or operation.get("resource_id") or "unknown")
            reason = str(operation.get("reason") or _reason_for_code(code))
            follow_up = "Resolve blocker and rerun plan." if action == "blocked" else "Review skip reason."
            rows.append([code, path, reason, follow_up])
    for code in _as_string_list(payload.get("blocked_codes")):
        if any(existing[0] == code for existing in rows):
            continue
        rows.append([code, "n/a", _reason_for_code(code), "Resolve blocker and rerun plan."])
    return rows


def _bisync_planned_rows(payload: dict[str, object]) -> list[list[str]]:
    rows: list[list[str]] = []
    drifts = payload.get("drifts")
    if not isinstance(drifts, list):
        return rows
    for drift in drifts:
        if not isinstance(drift, dict):
            continue
        dtype = str(drift.get("type") or "drift")
        direction = str(drift.get("direction") or "manual")
        skill = str(drift.get("skill") or "unknown")
        planned_action = "copy" if direction in {"repo-to-home", "home-to-repo"} else "manual-review"
        reason = _bisync_reason(dtype, direction)
        evidence = direction if direction != "manual" else dtype
        rows.append([skill, "bisync", planned_action, reason, evidence])
    return rows


def _bisync_completed_rows(payload: dict[str, object]) -> list[list[str]]:
    if str(payload.get("mode") or "") != "apply":
        return []
    verification = payload.get("verification")
    status = "unknown"
    if isinstance(verification, dict):
        status = str(verification.get("status") or status)
    if status != "converged":
        return []
    drifts = payload.get("drifts")
    if not isinstance(drifts, list):
        return []
    rows: list[list[str]] = []
    for drift in drifts:
        if not isinstance(drift, dict):
            continue
        direction = str(drift.get("direction") or "")
        if direction not in {"repo-to-home", "home-to-repo"}:
            continue
        skill = str(drift.get("skill") or "unknown")
        rows.append([skill, "copied", f"Applied {direction} winner.", "ok", "post-apply plan clean"])
    return rows


def _bisync_blocker_rows(payload: dict[str, object]) -> list[list[str]]:
    rows: list[list[str]] = []
    drifts = payload.get("drifts")
    if isinstance(drifts, list):
        for drift in drifts:
            if not isinstance(drift, dict):
                continue
            codes = drift.get("blocked_codes")
            if not isinstance(codes, list):
                continue
            skill = str(drift.get("skill") or "unknown")
            for code in codes:
                code_str = str(code)
                rows.append([code_str, skill, _reason_for_code(code_str), "Resolve manually before apply."])
    for code in _as_string_list(payload.get("blocked_codes")):
        if any(existing[0] == code for existing in rows):
            continue
        rows.append([code, "n/a", _reason_for_code(code), "Resolve manually before apply."])
    return rows


def _remaining_work_rows(payload: dict[str, object]) -> list[list[str]]:
    rows: list[list[str]] = []
    for code in _as_string_list(payload.get("blocked_codes")):
        rows.append([code, _reason_for_code(code), "Resolve blocker and rerun."])
    residual = payload.get("residual_drift")
    if isinstance(residual, list) and residual:
        rows.append(["residual_drift", "Residual drift remains after apply.", "Run plan and resolve residual entries."])
    verification = payload.get("verification")
    if isinstance(verification, dict):
        residual_drifts = verification.get("residual_drifts")
        if isinstance(residual_drifts, list) and residual_drifts:
            rows.append(["bisync_residual", "Bisync verification reported residual drift.", "Resolve residual drifts and rerun bisync plan."])
    return rows


def _next_action_table(next_action: object, next_step: object) -> list[str]:
    if not isinstance(next_action, dict):
        rows = [["Action", "unknown"], ["Reason", str(next_step or "none")]]
        return _table_lines(["Field", "Value"], rows)
    rows = [
        ["Action", str(next_action.get("action") or "unknown")],
        ["Allowed", str(bool(next_action.get("allowed", False))).lower()],
        [
            "Requires explicit approval",
            str(bool(next_action.get("requires_explicit_approval", False))).lower(),
        ],
        ["Command", str(next_action.get("command") or "") or "none"],
        ["Reason", str(next_action.get("reason") or next_step or "none")],
    ]
    return _table_lines(["Field", "Value"], rows)


def _reason_for_code(code: str) -> str:
    return BLOCKER_REASON_MAP.get(code, "Manual review required.")


def _bisync_reason(drift_type: str, direction: str) -> str:
    if drift_type == "only-repo":
        return "Skill exists only in repository and can be created in home during explicit apply."
    if drift_type == "only-home":
        return "Skill exists only in home and requires manual decision."
    if drift_type == "equal-mtime":
        return "Hashes differ with equal timestamps, so winner is ambiguous."
    if direction == "repo-to-home":
        return "Repository bundle timestamp is newer than home bundle."
    if direction == "home-to-repo":
        return "Home bundle timestamp is newer than repository bundle."
    return "Drift detected and requires review."
