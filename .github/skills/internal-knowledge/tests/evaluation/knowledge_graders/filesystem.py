"""Filesystem policy graders for offline knowledge runs."""

from __future__ import annotations

import fnmatch

from .core import RunInput, Verdict, changed_paths, register


def _result(name: str, code: str | None = None, evidence: str = "") -> Verdict:
    return Verdict(name, "fail" if code else "pass", code, evidence or "checks satisfied")


def _matches(path: str, allowlist: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in allowlist)


@register("writes_within_allowlist")
def writes_within_allowlist(run: RunInput, gold: dict) -> Verdict:
    del gold
    outside = sorted(
        path
        for path in changed_paths(run.before, run.after)
        if not _matches(path, run.allowlist)
    )
    return _result(
        "writes_within_allowlist",
        "write-outside-allowlist" if outside else None,
        f"out-of-allowlist paths: {outside}" if outside else "all changed paths match allowlist",
    )


@register("no_code_edits")
def no_code_edits(run: RunInput, gold: dict) -> Verdict:
    del gold
    non_docs = sorted(
        path
        for path in changed_paths(run.before, run.after)
        if not path.lower().endswith((".md", ".markdown"))
    )
    return _result(
        "no_code_edits",
        "non-documentation-edit" if non_docs else None,
        f"non-documentation paths: {non_docs}" if non_docs else "changed paths are documentation",
    )


@register("protected_bytes")
def protected_bytes(run: RunInput, gold: dict) -> Verdict:
    changed = sorted(
        path
        for path in gold.get("protected_paths", [])
        if run.before.get(path) != run.after.get(path)
    )
    return _result(
        "protected_bytes",
        "protected-changed" if changed else None,
        f"protected paths changed or missing: {changed}" if changed else "protected bytes preserved",
    )


@register("idempotent")
def idempotent(run: RunInput, gold: dict) -> Verdict:
    del gold
    if run.second_after is None:
        return Verdict("idempotent", "blocked", "missing-second-run", "second run was not observed")
    if dict(run.second_after) != dict(run.after):
        return Verdict("idempotent", "fail", "not-idempotent", "second run changed the resulting tree")
    return _result("idempotent", evidence="second run matches the first result")
