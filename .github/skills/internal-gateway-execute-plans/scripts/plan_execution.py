#!/usr/bin/env python3
"""Read-only, stdlib-only plan execution validator CLI."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    severity: Literal["blocking", "notice"] = "blocking"


CloseoutRoute = Literal[
    "continue-execution",
    "continue-recovery",
    "DONE",
    "PARTIAL",
    "BLOCKED",
    "NEEDS_REVIEW",
]

CLOSEOUT_OUTCOMES = frozenset(
    {"exact-pass", "equivalent-pass", "warning", "unresolved", "regression"}
)
CLOSEOUT_REQUIRED_FIELDS = frozenset(
    {
        "tasks_complete",
        "tasks_remaining",
        "human_review_required",
        "fatal_conditions",
        "validations",
    }
)
CLOSEOUT_OPTIONAL_FIELDS = frozenset({"pause_requested", "exhaustion_evidence"})
EQUIVALENCE_FIELDS = frozenset(
    {"target_did_not_start", "same_checks", "same_inputs", "runtime_not_material"}
)


@dataclass(frozen=True)
class ValidationEquivalence:
    target_did_not_start: bool
    same_checks: bool
    same_inputs: bool
    runtime_not_material: bool

    @property
    def admissible(self) -> bool:
        return all(
            (
                self.target_did_not_start,
                self.same_checks,
                self.same_inputs,
                self.runtime_not_material,
            )
        )


@dataclass(frozen=True)
class ValidationObligation:
    name: str
    required: bool
    outcome: str
    recovery_candidates: tuple[str, ...]
    equivalence: ValidationEquivalence | None = None


@dataclass(frozen=True)
class CloseoutEvidence:
    tasks_complete: bool
    tasks_remaining: tuple[str, ...]
    human_review_required: bool
    fatal_conditions: tuple[str, ...]
    validations: tuple[ValidationObligation, ...]
    pause_requested: bool = False
    exhaustion_evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class CloseoutDecision:
    route: CloseoutRoute
    reasons: tuple[str, ...]
    next_action: str

    def as_dict(self) -> dict[str, object]:
        return {
            "route": self.route,
            "reason_codes": list(self.reasons),
            "next_action": self.next_action,
        }


ALLOWED_STATUSES = frozenset({"DONE", "PARTIAL", "BLOCKED", "NEEDS_REVIEW"})

STATUS_FILENAME_RE = re.compile(
    r"^(?P<basename>.+)\.(?P<status>DONE|PARTIAL|BLOCKED|NEEDS_REVIEW)\.md$"
)

REQUIRED_PLAN_HEADINGS = (
    "Goal",
    "Global Constraints",
)

PLAN_NOTICE_CODES = frozenset({"missing-heading", "missing-execution-field"})

TASK_HEADING_RE = re.compile(
    r"(?im)^#{2,6}\s+Task(?:\s+\d+)?(?:\s*:|\b)"
)
UNCHECKED_TASK_RE = re.compile(r"(?m)^\s*[-*]\s+\[\s\]\s+\S")

PLAN_HEADING_ALIASES = {
    "Repository Preflight": (
        "Repository Preflight",
        "Preflight",
        "Preflight Gate",
    ),
}

REQUIRED_EXECUTION_FIELDS = (
    "Baseline Validation",
    "Recovery Policy",
    "Escalation Conditions",
    "User-Facing Report",
)

REQUIRED_STATUS_HEADINGS = (
    "Status",
    "Plan",
    "Plan Fingerprint",
    "Completed",
    "Remaining",
    "Validation",
    "Next",
)


def _closeout_mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _closeout_bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean")
    return value


def _closeout_strings(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValueError(f"{label} must be a list of non-empty strings")
    return tuple(item.strip() for item in value)


def _parse_equivalence(value: object, label: str) -> ValidationEquivalence:
    mapping = _closeout_mapping(value, label)
    unknown = set(mapping) - EQUIVALENCE_FIELDS
    missing = EQUIVALENCE_FIELDS - set(mapping)
    if unknown or missing:
        details = []
        if unknown:
            details.append(f"unknown fields: {sorted(unknown)}")
        if missing:
            details.append(f"missing fields: {sorted(missing)}")
        raise ValueError(f"{label} is malformed ({'; '.join(details)})")
    return ValidationEquivalence(
        target_did_not_start=_closeout_bool(
            mapping["target_did_not_start"], f"{label}.target_did_not_start"
        ),
        same_checks=_closeout_bool(mapping["same_checks"], f"{label}.same_checks"),
        same_inputs=_closeout_bool(mapping["same_inputs"], f"{label}.same_inputs"),
        runtime_not_material=_closeout_bool(
            mapping["runtime_not_material"], f"{label}.runtime_not_material"
        ),
    )


def parse_closeout_evidence(payload: Mapping[str, object]) -> CloseoutEvidence:
    mapping = _closeout_mapping(payload, "closeout evidence")
    unknown = set(mapping) - CLOSEOUT_REQUIRED_FIELDS - CLOSEOUT_OPTIONAL_FIELDS
    missing = CLOSEOUT_REQUIRED_FIELDS - set(mapping)
    if unknown or missing:
        details = []
        if unknown:
            details.append(f"unknown fields: {sorted(unknown)}")
        if missing:
            details.append(f"missing fields: {sorted(missing)}")
        raise ValueError(f"closeout evidence is malformed ({'; '.join(details)})")

    raw_validations = mapping["validations"]
    if not isinstance(raw_validations, list) or not raw_validations:
        raise ValueError("validations must be a non-empty list")

    validations: list[ValidationObligation] = []
    for index, raw_validation in enumerate(raw_validations):
        label = f"validations[{index}]"
        validation = _closeout_mapping(raw_validation, label)
        allowed = {"name", "required", "outcome", "recovery_candidates", "equivalence"}
        unknown_validation = set(validation) - allowed
        missing_validation = {
            "name",
            "required",
            "outcome",
            "recovery_candidates",
        } - set(validation)
        if unknown_validation or missing_validation:
            details = []
            if unknown_validation:
                details.append(f"unknown fields: {sorted(unknown_validation)}")
            if missing_validation:
                details.append(f"missing fields: {sorted(missing_validation)}")
            raise ValueError(f"{label} is malformed ({'; '.join(details)})")

        name = validation["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{label}.name must be a non-empty string")
        required = _closeout_bool(validation["required"], f"{label}.required")
        outcome = validation["outcome"]
        if not isinstance(outcome, str) or outcome not in CLOSEOUT_OUTCOMES:
            raise ValueError(
                f"{label}.outcome must be one of {sorted(CLOSEOUT_OUTCOMES)}"
            )
        recovery_candidates = _closeout_strings(
            validation["recovery_candidates"], f"{label}.recovery_candidates"
        )
        equivalence = None
        if "equivalence" in validation:
            equivalence = _parse_equivalence(
                validation["equivalence"], f"{label}.equivalence"
            )
        if outcome == "equivalent-pass" and equivalence is None:
            raise ValueError(
                f"{label}.equivalence is required for equivalent-pass"
            )
        validations.append(
            ValidationObligation(
                name=name.strip(),
                required=required,
                outcome=outcome,
                recovery_candidates=recovery_candidates,
                equivalence=equivalence,
            )
        )

    return CloseoutEvidence(
        tasks_complete=_closeout_bool(mapping["tasks_complete"], "tasks_complete"),
        tasks_remaining=_closeout_strings(
            mapping["tasks_remaining"], "tasks_remaining"
        ),
        human_review_required=_closeout_bool(
            mapping["human_review_required"], "human_review_required"
        ),
        fatal_conditions=_closeout_strings(
            mapping["fatal_conditions"], "fatal_conditions"
        ),
        validations=tuple(validations),
        pause_requested=_closeout_bool(
            mapping.get("pause_requested", False), "pause_requested"
        ),
        exhaustion_evidence=_closeout_strings(
            mapping.get("exhaustion_evidence", []), "exhaustion_evidence"
        ),
    )


def _closeout_decision(
    route: CloseoutRoute, reasons: list[str], next_action: str
) -> CloseoutDecision:
    return CloseoutDecision(route, tuple(reasons[:4]), next_action)


def classify_closeout(
    evidence: CloseoutEvidence | Mapping[str, object],
) -> CloseoutDecision:
    if not isinstance(evidence, CloseoutEvidence):
        evidence = parse_closeout_evidence(evidence)

    if evidence.fatal_conditions:
        reasons = ["fatal-condition-exhausted"]
        if any(
            "unknown" in condition.lower() for condition in evidence.fatal_conditions
        ):
            reasons.append("unknown-fatal-condition")
        if any(
            "task-local regression" in condition.lower()
            for condition in evidence.fatal_conditions
        ):
            reasons.append("task-local-regression")
        return _closeout_decision(
            "BLOCKED",
            reasons,
            "Resolve the fatal condition before resuming execution.",
        )

    if not evidence.tasks_complete or evidence.tasks_remaining:
        if evidence.pause_requested:
            return _closeout_decision(
                "PARTIAL",
                ["pause-requested", "unfinished-tasks"],
                "Resume the first remaining executable task.",
            )
        return _closeout_decision(
            "continue-execution",
            ["unfinished-tasks"],
            "Continue execution with the first remaining task.",
        )

    recovery_obligations = [
        validation
        for validation in evidence.validations
        if validation.outcome in {"unresolved", "regression"}
        or (
            validation.outcome == "equivalent-pass"
            and validation.equivalence is not None
            and not validation.equivalence.admissible
        )
    ]
    candidate_obligations = [
        validation for validation in recovery_obligations if validation.recovery_candidates
    ]
    if candidate_obligations:
        candidate = candidate_obligations[0].recovery_candidates[0]
        names = ", ".join(validation.name for validation in candidate_obligations)
        return _closeout_decision(
            "continue-recovery",
            ["recovery-candidate-available", f"validation:{candidate_obligations[0].name}"],
            f"Run {names} using recovery candidate: {candidate}.",
        )

    invalid_or_unresolved = [
        validation
        for validation in evidence.validations
        if validation.outcome in {"unresolved", "regression"}
        or (
            validation.outcome == "equivalent-pass"
            and validation.equivalence is not None
            and not validation.equivalence.admissible
        )
        or (validation.outcome == "warning" and validation.required)
    ]
    if invalid_or_unresolved:
        reasons = ["validation-not-admissible"]
        if evidence.human_review_required:
            reasons.append("human-review-required")
        if evidence.exhaustion_evidence:
            reasons.append("recovery-exhausted")
        if evidence.human_review_required or evidence.exhaustion_evidence:
            return _closeout_decision(
                "NEEDS_REVIEW",
                reasons,
                "Obtain required human or external verification, then rerun closeout-check.",
            )
        return _closeout_decision(
            "BLOCKED",
            reasons,
            "Record recovery exhaustion or establish a safe candidate before continuing.",
        )

    if evidence.human_review_required:
        return _closeout_decision(
            "NEEDS_REVIEW",
            ["human-review-required"],
            "Obtain the required human verification, then rerun closeout-check.",
        )

    return _closeout_decision(
        "DONE",
        ["all-required-validations-passed"],
        "No further execution is required.",
    )


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return f"sha256:{h.hexdigest()}"


def _extract_headings(text: str) -> list[str]:
    return [
        line.lstrip("#").strip()
        for line in text.splitlines()
        if line.startswith("#")
    ]


def _parse_status_from_filename(path: Path) -> str | None:
    m = STATUS_FILENAME_RE.match(path.name)
    if m:
        return m.group("status")
    return None


def _parse_status_from_content(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip().strip("`")
        if stripped in ALLOWED_STATUSES:
            return stripped
    return None


def _has_named_field(text: str, name: str) -> bool:
    escaped = re.escape(name)
    patterns = (
        rf"(?im)^#+\s*{escaped}\s*$",
        rf"(?im)^\s*[-*]\s+\*\*{escaped}:\*\*",
        rf"(?im)^\s*[-*]\s+{escaped}:",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _plan_finding(code: str, message: str) -> Finding:
    severity = "notice" if code in PLAN_NOTICE_CODES else "blocking"
    return Finding(code, message, severity)


def _extract_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    collecting = False
    collected: list[str] = []
    for line in lines:
        if line.strip() == f"## {heading}":
            collecting = True
            continue
        if collecting and line.startswith("## "):
            break
        if collecting:
            collected.append(line)
    return "\n".join(collected).strip()


def _extract_plan_reference(text: str) -> str | None:
    section = _extract_section(text, "Plan")
    for line in section.splitlines():
        value = line.strip().strip("`").strip()
        if value:
            return value
    return None


def _plan_reference_matches(
    plan_path: Path,
    status_path: Path,
    declared_reference: str,
    repo_root: Path,
) -> bool:
    declared_path = Path(declared_reference)
    candidates: set[Path] = set()
    if declared_path.is_absolute():
        candidates.add(declared_path.resolve())
    else:
        candidates.add((status_path.parent / declared_path).resolve())
        candidates.add((plan_path.parent / declared_path).resolve())
        candidates.add((repo_root / declared_path).resolve())
    return plan_path.resolve() in candidates


def _validate_status_evidence(text: str, status: str | None) -> list[Finding]:
    findings: list[Finding] = []
    baseline = _extract_section(text, "Baseline Validation")
    final = _extract_section(text, "Validation")
    recovery = _extract_section(text, "Recovery Attempts")
    closeout_decision = _extract_section(text, "Closeout Decision")
    recovery_exhaustion = _extract_section(text, "Recovery Exhaustion")
    classification = _extract_section(text, "Failure Classification")

    baseline_commands = set(re.findall(r"`([^`\n]+)`", baseline))
    final_commands = set(re.findall(r"`([^`\n]+)`", final))
    if baseline and final and (
        not baseline_commands
        or not final_commands
        or not baseline_commands.intersection(final_commands)
    ):
        findings.append(
            Finding(
                "validation-delta-mismatch",
                "Baseline and final validation must include at least one identical command",
            )
        )

    if recovery and recovery.strip().lower() in {"tbd", "todo", "pending"}:
        findings.append(
            Finding(
                "invalid-recovery-evidence",
                "Recovery Attempts must record actions or explicitly state none",
            )
        )

    if closeout_decision and closeout_decision.strip().lower() in {
        "tbd",
        "todo",
        "pending",
    }:
        findings.append(
            Finding(
                "invalid-closeout-decision",
                "Closeout Decision must record a route or explicitly state none",
            )
        )

    if recovery_exhaustion and recovery_exhaustion.strip().lower() in {
        "tbd",
        "todo",
        "pending",
    }:
        findings.append(
            Finding(
                "invalid-recovery-exhaustion",
                "Recovery Exhaustion must record evidence or explicitly state none",
            )
        )

    classification_lower = classification.lower()
    allowed_classifications = (
        "none",
        "task-local regression",
        "pre-existing",
        "unrelated",
        "external",
        "environmental",
        "unknown",
    )
    if classification and not any(
        marker in classification_lower for marker in allowed_classifications
    ):
        findings.append(
            Finding(
                "invalid-failure-classification",
                "Failure Classification must use a contract classification or none",
            )
        )

    if status == "NEEDS_REVIEW" and classification and not any(
        marker in classification_lower
        for marker in (
            "pre-existing",
            "unrelated",
            "external",
            "environmental",
            "human",
        )
    ):
        findings.append(
            Finding(
                "needs-review-classification",
                "NEEDS_REVIEW requires human, pre-existing, unrelated, external, or environmental classification evidence",
            )
        )
    if status == "BLOCKED" and classification and all(
        marker not in classification_lower
        for marker in ("task-local regression", "environmental", "unknown", "fatal")
    ):
        findings.append(
            Finding(
                "blocked-without-fatal-condition",
                "BLOCKED requires evidence of a fatal execution condition",
            )
        )
    return findings


def validate_plan(path: Path, repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not path.is_file():
        findings.append(Finding("plan-not-found", f"Plan file not found: {path}"))
        return findings

    retained_dir = repo_root / "tmp" / "superpowers" / "plans"
    try:
        path.resolve().relative_to(retained_dir.resolve())
    except ValueError:
        findings.append(
            Finding(
                "plan-outside-retained-directory",
                f"Plan must be under {retained_dir}",
            )
        )

    try:
        text = path.read_text()
    except (OSError, UnicodeError) as exc:
        findings.append(Finding("plan-unreadable", f"Plan content is unreadable: {exc}"))
        return findings
    headings = _extract_headings(text)
    heading_set = set(headings)

    for required in REQUIRED_PLAN_HEADINGS:
        if required not in heading_set:
            inline_pattern = f"**{required}:**"
            if inline_pattern not in text:
                findings.append(
                    _plan_finding(
                        "missing-heading", f"Plan missing required heading: {required}"
                    )
                )

    for canonical, aliases in PLAN_HEADING_ALIASES.items():
        if not any(alias in heading_set for alias in aliases):
                findings.append(
                    _plan_finding(
                        "missing-heading", f"Plan missing required heading: {canonical}"
                    )
                )

    for required in REQUIRED_EXECUTION_FIELDS:
        if not _has_named_field(text, required):
                findings.append(
                    _plan_finding(
                        "missing-execution-field",
                        f"Plan missing required execution field: {required}",
                    )
                )

    if not (TASK_HEADING_RE.search(text) or UNCHECKED_TASK_RE.search(text)):
        findings.append(
            Finding("missing-task", "Plan must contain at least one task heading")
        )

    return findings


def validate_status(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not path.is_file():
        findings.append(
            Finding("status-not-found", f"Status file not found: {path}")
        )
        return findings

    text = path.read_text()
    headings = _extract_headings(text)
    heading_set = set(headings)

    status_from_file = _parse_status_from_filename(path)
    status_from_content = _parse_status_from_content(text)

    if status_from_file is None:
        findings.append(
            Finding(
                "unknown-status",
                f"Status filename must match <basename>.<STATUS>.md with STATUS in {sorted(ALLOWED_STATUSES)}",
            )
        )
    elif status_from_content is not None and status_from_file != status_from_content:
        findings.append(
            Finding(
                "status-mismatch",
                f"Filename status {status_from_file} != content status {status_from_content}",
            )
        )

    for required in REQUIRED_STATUS_HEADINGS:
        if required not in heading_set:
            findings.append(
                Finding(
                    "missing-heading",
                    f"Status missing required heading: {required}",
                )
            )

    findings.extend(_validate_status_evidence(text, status_from_file))

    return findings


def validate_resume(plan_path: Path, status_path: Path, repo_root: Path | None = None) -> list[Finding]:
    findings: list[Finding] = []
    effective_root = repo_root or _find_repo_root(plan_path)
    findings.extend(validate_plan(plan_path, repo_root=effective_root))
    findings.extend(validate_status(status_path))

    if any(f.severity == "blocking" for f in findings):
        return findings

    plan_fingerprint = compute_sha256(plan_path)
    status_text = status_path.read_text()

    declared_plan = _extract_plan_reference(status_text)
    if declared_plan is None:
        findings.append(
            Finding(
                "missing-plan-binding",
                "Status must declare the plan path under the Plan heading",
            )
        )
    elif not _plan_reference_matches(
        plan_path,
        status_path,
        declared_plan,
        effective_root,
    ):
        findings.append(
            Finding(
                "plan-binding-mismatch",
                f"Status plan reference does not match the validated plan: {declared_plan}",
            )
        )

    recorded_fingerprint = None
    for line in status_text.splitlines():
        stripped = line.strip().strip("`")
        if stripped.startswith("sha256:"):
            recorded_fingerprint = stripped
            break

    if recorded_fingerprint is None:
        findings.append(
            Finding(
                "missing-fingerprint",
                "Status file must contain a Plan Fingerprint heading with sha256: value",
            )
        )
    elif recorded_fingerprint != plan_fingerprint:
        findings.append(
            Finding(
                "plan-fingerprint-drift",
                f"Plan changed after approval: recorded {recorded_fingerprint} != computed {plan_fingerprint}",
            )
        )

    return findings


def validate_completion(plan_path: Path, status_path: Path, repo_root: Path | None = None) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(validate_resume(plan_path, status_path, repo_root=repo_root))

    if any(f.severity == "blocking" for f in findings):
        return findings

    status_from_file = _parse_status_from_filename(status_path)
    if status_from_file != "DONE":
        findings.append(
            Finding(
                "not-done",
                f"Completion requires DONE status, got {status_from_file}",
            )
        )

    status_text = status_path.read_text()
    headings = _extract_headings(status_text)
    if "Remaining" in headings:
        idx = headings.index("Remaining")
        lines = status_text.splitlines()
        remaining_lines = []
        collecting = False
        for line in lines:
            if line.strip() == "## Remaining":
                collecting = True
                continue
            if collecting and line.startswith("## "):
                break
            if collecting and line.strip():
                remaining_lines.append(line.strip())

        has_real_items = any(
            item for item in remaining_lines if item.lower() not in ("none", "- none")
        )
        if has_real_items:
            findings.append(
                Finding(
                    "remaining-items",
                    "DONE status requires no remaining items",
                )
            )

    return findings


def build_compact_payload(findings: list[Finding]) -> dict[str, object]:
    blocking = [f for f in findings if f.severity == "blocking"]
    notice = [f for f in findings if f.severity == "notice"]
    sample = [
        {"code": f.code, "severity": f.severity} for f in findings[:10]
    ]
    return {
        "status": "passed" if not blocking else "failed",
        "finding_counts": {
            "total": len(findings),
            "blocking": len(blocking),
            "notice": len(notice),
        },
        "finding_sample": sample,
        "next_action": (
            "All checks passed."
            if not blocking
            else "Resolve blocking plan execution findings."
        ),
    }


def _format_text(findings: list[Finding]) -> str:
    if not findings:
        return "OK: all checks passed."
    lines = []
    for f in findings:
        lines.append(f"[{f.severity.upper()}] {f.code}: {f.message}")
    return "\n".join(lines)


def _format_json(findings: list[Finding]) -> str:
    blocking = any(f.severity == "blocking" for f in findings)
    return json.dumps(
        {
            "status": "failed" if blocking else "passed",
            "findings": [
                {"code": f.code, "message": f.message, "severity": f.severity}
                for f in findings
            ],
        },
        indent=2,
    )


def _format_closeout_text(decision: CloseoutDecision) -> str:
    return (
        f"Route: {decision.route}\n"
        f"Reason codes: {', '.join(decision.reasons)}\n"
        f"Next action: {decision.next_action}"
    )


def _format_closeout_json(decision: CloseoutDecision) -> str:
    return json.dumps(decision.as_dict(), indent=2)


def _format_closeout_compact(decision: CloseoutDecision) -> str:
    return json.dumps(decision.as_dict())


def _find_repo_root(start: Path) -> Path:
    for parent in start.resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / ".github").exists():
            return parent
    return start.resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only plan execution validator"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight", help="Validate a plan file")
    preflight.add_argument("plan", type=Path)
    preflight.add_argument("--repo-root", type=Path, default=None)
    preflight.add_argument(
        "--format", choices=("text", "json", "compact"), default="text"
    )

    status_check = subparsers.add_parser("status-check", help="Validate a status file")
    status_check.add_argument("status", type=Path)
    status_check.add_argument(
        "--format", choices=("text", "json", "compact"), default="text"
    )

    resume_check = subparsers.add_parser(
        "resume-check", help="Validate resume safety"
    )
    resume_check.add_argument("plan", type=Path)
    resume_check.add_argument("status", type=Path)
    resume_check.add_argument("--repo-root", type=Path, default=None)
    resume_check.add_argument(
        "--format", choices=("text", "json", "compact"), default="text"
    )

    completion_check = subparsers.add_parser(
        "completion-check", help="Validate completion readiness"
    )
    completion_check.add_argument("plan", type=Path)
    completion_check.add_argument("status", type=Path)
    completion_check.add_argument("--repo-root", type=Path, default=None)
    completion_check.add_argument(
        "--format", choices=("text", "json", "compact"), default="text"
    )

    closeout_check = subparsers.add_parser(
        "closeout-check", help="Classify closeout evidence"
    )
    closeout_check.add_argument("evidence", type=Path)
    closeout_check.add_argument(
        "--format", choices=("text", "json", "compact"), default="text"
    )

    args = parser.parse_args(argv)

    if args.command == "closeout-check":
        try:
            payload = json.loads(args.evidence.read_text())
            decision = classify_closeout(payload)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            sys.stderr.write(f"Invalid closeout evidence: {exc}\n")
            return 1
        fmt = getattr(args, "format", "text")
        if fmt == "compact":
            output = _format_closeout_compact(decision)
        elif fmt == "json":
            output = _format_closeout_json(decision)
        else:
            output = _format_closeout_text(decision)
        sys.stdout.write(output + "\n")
        return 0

    if args.command == "preflight":
        repo_root = args.repo_root or _find_repo_root(args.plan)
        findings = validate_plan(args.plan, repo_root=repo_root)
    elif args.command == "status-check":
        findings = validate_status(args.status)
    elif args.command == "resume-check":
        findings = validate_resume(args.plan, args.status, repo_root=args.repo_root)
    elif args.command == "completion-check":
        findings = validate_completion(args.plan, args.status, repo_root=args.repo_root)
    else:
        parser.print_help(sys.stderr)
        return 2

    fmt = getattr(args, "format", "text")
    if fmt == "compact":
        output = json.dumps(build_compact_payload(findings))
    elif fmt == "json":
        output = _format_json(findings)
    else:
        output = _format_text(findings)

    sys.stdout.write(output + "\n")

    blocking = any(f.severity == "blocking" for f in findings)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
