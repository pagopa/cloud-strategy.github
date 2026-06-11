from __future__ import annotations

from collections.abc import Iterable


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
        if direction in counts:
            counts[direction] += 1
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
