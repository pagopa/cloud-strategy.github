#!/usr/bin/env python3
"""Deterministic gate and claim helper for internal-gateway-simple-task.

The helper is intentionally structured. It expects normalized facts that were
already recovered from the user prompt, local files, or validation output. It
does not replace local inspection, but it reduces repeated reasoning when the
simple-task bundle only needs a deterministic gate, readiness brief, or claim
gate answer.
"""

from __future__ import annotations

import argparse
import json
import re


DEPTH_KEYWORDS = ("full", "idea", "complete")
TRIVIAL_KINDS = ("local-answer", "tiny-edit", "focused-read", "validator-run")
LANES = ("answer", "edit", "diagnose", "validate", "execute", "plan", "unspecified")
MATERIAL_RISKS = (
    "contract",
    "routing",
    "security",
    "secret",
    "tenant",
    "governance",
    "rollout",
    "architecture",
    "cross-file",
    "user-visible",
)
CLAIMS = (
    "completion",
    "covered",
    "fixed",
    "no-code-findings",
    "no-systems-findings",
    "performance-improved",
    "pr-ready",
    "readiness",
    "validator-passes",
)

CLAIM_REQUIREMENTS = {
    "fixed": [
        {
            "owner": "internal-debugging",
            "evidence_gate": "Re-run the original loop, or state the blocker.",
        },
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Fresh validation evidence, not intent or stale output.",
        },
    ],
    "covered": [
        {
            "owner": "internal-tdd",
            "evidence_gate": "Show the failing-then-passing seam, or state why it could not be run.",
        },
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Fresh validation evidence, not intent or stale output.",
        },
    ],
    "performance-improved": [
        {
            "owner": "internal-performance-optimization",
            "evidence_gate": "Compare baseline and after evidence from the same measurement class.",
        },
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Fresh validation evidence, not intent or stale output.",
        },
    ],
    "pr-ready": [
        {
            "owner": "internal-github-pr",
            "evidence_gate": "Check PR lifecycle evidence before the claim.",
        },
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Fresh validation evidence, not intent or stale output.",
        },
    ],
    "no-code-findings": [
        {
            "owner": "internal-code-review",
            "evidence_gate": "Defect-first review evidence, or escalate to review mode.",
        },
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Fresh validation evidence, not intent or stale output.",
        },
    ],
    "no-systems-findings": [
        {
            "owner": "internal-high-level-review",
            "evidence_gate": "Systems review evidence, or escalate to review mode.",
        },
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Fresh validation evidence, not intent or stale output.",
        },
    ],
    "completion": [
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Fresh validation evidence, not intent or stale output.",
        }
    ],
    "readiness": [
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Fresh validation evidence, not intent or stale output.",
        }
    ],
    "validator-passes": [
        {
            "owner": "superpowers-verification-before-completion",
            "evidence_gate": "Re-run the validator and read fresh output before the claim.",
        }
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic gate and claim helper for internal-gateway-simple-task."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gate_parser = subparsers.add_parser(
        "gate", help="Classify the simple-task gate from normalized facts."
    )
    gate_parser.add_argument("--task", default="unspecified task")
    gate_parser.add_argument(
        "--lane", choices=LANES, default="unspecified", help="Active simple lane."
    )
    gate_parser.add_argument(
        "--trivial-kind",
        choices=TRIVIAL_KINDS,
        help="Normalized local task kind for trivial-skip checks.",
    )
    gate_parser.add_argument(
        "--prompt",
        default="",
        help="Optional prompt text used only for deterministic depth-keyword detection.",
    )
    gate_parser.add_argument(
        "--depth-keyword",
        action="append",
        choices=DEPTH_KEYWORDS,
        default=[],
        help="Known depth keyword. Repeatable.",
    )
    gate_parser.add_argument(
        "--risk",
        action="append",
        choices=MATERIAL_RISKS,
        default=[],
        help="Known material risk. Repeatable.",
    )
    gate_parser.add_argument("--needs-plan", action="store_true")
    gate_parser.add_argument("--needs-review", action="store_true")
    gate_parser.add_argument("--needs-critical", action="store_true")
    gate_parser.add_argument("--needs-retained-plan", action="store_true")
    gate_parser.add_argument(
        "--plan-mode",
        choices=("explicit", "implicit"),
        help="Plan mode trigger type. Explicit is mandatory from the user; implicit is a cost-signal proposal.",
    )
    gate_parser.add_argument("--owner-ambiguous", action="store_true")
    gate_parser.add_argument("--clarification-overflow", action="store_true")
    gate_parser.add_argument("--validation-obvious", action="store_true")
    gate_parser.add_argument(
        "--validation-path", default="", help="Focused validation command or check."
    )
    gate_parser.add_argument(
        "--validation-gap", default="", help="Exact validation gap when no check exists yet."
    )
    gate_parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="Output format."
    )

    claim_parser = subparsers.add_parser(
        "claim", help="Resolve required owners and evidence gates for status claims."
    )
    claim_parser.add_argument(
        "--claim",
        action="append",
        choices=CLAIMS,
        required=True,
        help="Status claim to evaluate. Repeatable.",
    )
    claim_parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="Output format."
    )

    return parser.parse_args()


def detect_depth_keywords(prompt: str, explicit_keywords: list[str]) -> list[str]:
    found = set(explicit_keywords)
    lowered_prompt = prompt.lower()

    for keyword in DEPTH_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", lowered_prompt):
            found.add(keyword)

    return sorted(found)


def infer_lane(lane: str, trivial_kind: str | None) -> str:
    if lane != "unspecified":
        return lane
    if trivial_kind == "local-answer":
        return "answer"
    if trivial_kind == "focused-read":
        return "answer"
    if trivial_kind == "tiny-edit":
        return "edit"
    if trivial_kind == "validator-run":
        return "validate"
    return "unspecified"


def determine_next_owner(
    *,
    needs_plan: bool,
    needs_review: bool,
    needs_critical: bool,
    needs_retained_plan: bool,
    plan_mode: str | None,
    owner_ambiguous: bool,
    clarification_overflow: bool,
) -> str:
    if needs_review:
        return "internal-gateway-review"
    if needs_critical:
        return "internal-gateway-critical-master"
    if plan_mode:
        return "internal-gateway-simple-task"
    if (
        needs_plan
        or needs_retained_plan
        or owner_ambiguous
        or clarification_overflow
    ):
        return "internal-gateway-idea-brainstorming"
    return "internal-gateway-simple-task"


def build_gate_decision(
    *,
    task: str,
    lane: str = "unspecified",
    trivial_kind: str | None = None,
    prompt: str = "",
    depth_keywords: list[str] | None = None,
    risks: list[str] | None = None,
    needs_plan: bool = False,
    needs_review: bool = False,
    needs_critical: bool = False,
    needs_retained_plan: bool = False,
    plan_mode: str | None = None,
    owner_ambiguous: bool = False,
    clarification_overflow: bool = False,
    validation_obvious: bool = False,
    validation_path: str = "",
    validation_gap: str = "",
) -> dict[str, object]:
    resolved_depth_keywords = detect_depth_keywords(prompt, depth_keywords or [])
    resolved_risks = sorted(set(risks or []))
    resolved_lane = infer_lane(lane, trivial_kind)
    next_owner = determine_next_owner(
        needs_plan=needs_plan,
        needs_review=needs_review,
        needs_critical=needs_critical,
        needs_retained_plan=needs_retained_plan,
        plan_mode=plan_mode,
        owner_ambiguous=owner_ambiguous,
        clarification_overflow=clarification_overflow,
    )
    reasons: list[str] = []

    if needs_review:
        reasons.append("needs-review")
    if needs_critical:
        reasons.append("needs-critical")
    if needs_plan:
        reasons.append("needs-plan")
    if needs_retained_plan:
        reasons.append("needs-retained-plan")
    if plan_mode:
        reasons.append(f"plan-mode:{plan_mode}")
    if owner_ambiguous:
        reasons.append("owner-ambiguous")
    if clarification_overflow:
        reasons.append("clarification-overflow")
    for keyword in resolved_depth_keywords:
        reasons.append(f"depth-keyword:{keyword}")
    for risk in resolved_risks:
        reasons.append(f"material-risk:{risk}")

    if next_owner != "internal-gateway-simple-task":
        gate_outcome = "escalate"
    elif plan_mode:
        gate_outcome = "plan-mode"
    elif (
        trivial_kind in TRIVIAL_KINDS
        and not resolved_depth_keywords
        and not resolved_risks
        and (validation_obvious or bool(validation_path) or bool(validation_gap))
    ):
        gate_outcome = "trivial-skip"
        reasons.append(f"trivial-kind:{trivial_kind}")
    else:
        gate_outcome = "full-gate"

    if validation_path:
        focused_validation_path = validation_path
    elif validation_gap:
        focused_validation_path = f"Validation gap: {validation_gap}"
    elif validation_obvious:
        focused_validation_path = "Validation is obvious but not yet named."
    else:
        focused_validation_path = "Validation path not yet identified."

    if resolved_risks:
        primary_assumption_or_risk = "Material risk: " + ", ".join(resolved_risks)
    elif resolved_depth_keywords:
        primary_assumption_or_risk = "Depth keyword present: " + ", ".join(
            resolved_depth_keywords
        )
    elif gate_outcome == "trivial-skip":
        primary_assumption_or_risk = (
            "Task stays local and validation is already obvious or explicitly bounded."
        )
    else:
        primary_assumption_or_risk = (
            "Task still fits one quick lane but needs the full gate before action."
        )

    if plan_mode == "implicit":
        approval_checkpoint = (
            "explicit user approval before writing the retained plan "
            "(implicit cost-signal proposal)"
        )
    elif plan_mode == "explicit":
        approval_checkpoint = (
            "plan mode requested by user; confirm profile and proceed to retained-plan authoring"
        )
    else:
        approval_checkpoint = "explicit user approval before operational work"

    readiness_brief = {
        "task": task,
        "lane_owner": next_owner,
        "primary_assumption_or_risk": primary_assumption_or_risk,
        "focused_validation_path": focused_validation_path,
        "gate_outcome": gate_outcome,
        "approval_checkpoint": approval_checkpoint,
    }

    return {
        "gate_outcome": gate_outcome,
        "lane": resolved_lane,
        "next_owner": next_owner,
        "depth_keywords": resolved_depth_keywords,
        "reason_codes": reasons,
        "needs_explicit_approval": next_owner == "internal-gateway-simple-task",
        "readiness_brief": readiness_brief,
    }


def resolve_claim_requirements(claims: list[str]) -> list[dict[str, str]]:
    ordered: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for claim in claims:
        for requirement in CLAIM_REQUIREMENTS[claim]:
            key = (requirement["owner"], requirement["evidence_gate"])
            if key in seen:
                continue
            seen.add(key)
            ordered.append(requirement)

    return ordered


def render_gate_text(decision: dict[str, object]) -> None:
    readiness_brief = decision["readiness_brief"]
    print(f"Gate outcome: {decision['gate_outcome']}")
    print(f"Lane: {decision['lane']}")
    print(f"Next owner: {decision['next_owner']}")
    if decision["depth_keywords"]:
        print("Depth keywords: " + ", ".join(decision["depth_keywords"]))
    if decision["reason_codes"]:
        print("Reason codes:")
        for reason in decision["reason_codes"]:
            print(f"- {reason}")
    print("Readiness Brief:")
    print(f"- task: {readiness_brief['task']}")
    print(f"- lane-owner: {readiness_brief['lane_owner']}")
    print(
        "- primary assumption or risk: "
        f"{readiness_brief['primary_assumption_or_risk']}"
    )
    print(
        "- focused validation path: "
        f"{readiness_brief['focused_validation_path']}"
    )
    print(f"- gate outcome: {readiness_brief['gate_outcome']}")
    print(f"- approval checkpoint: {readiness_brief['approval_checkpoint']}")


def render_claim_text(claims: list[str], requirements: list[dict[str, str]]) -> None:
    print("Claims: " + ", ".join(claims))
    for requirement in requirements:
        print(f"- {requirement['owner']}: {requirement['evidence_gate']}")


def main() -> int:
    args = parse_args()

    if args.command == "gate":
        decision = build_gate_decision(
            task=args.task,
            lane=args.lane,
            trivial_kind=args.trivial_kind,
            prompt=args.prompt,
            depth_keywords=args.depth_keyword,
            risks=args.risk,
            needs_plan=args.needs_plan,
            needs_review=args.needs_review,
            needs_critical=args.needs_critical,
            needs_retained_plan=args.needs_retained_plan,
            plan_mode=args.plan_mode,
            owner_ambiguous=args.owner_ambiguous,
            clarification_overflow=args.clarification_overflow,
            validation_obvious=args.validation_obvious,
            validation_path=args.validation_path,
            validation_gap=args.validation_gap,
        )
        if args.format == "json":
            print(json.dumps(decision, indent=2))
        else:
            render_gate_text(decision)
        return 0

    requirements = resolve_claim_requirements(args.claim)
    if args.format == "json":
        print(json.dumps({"claims": args.claim, "requirements": requirements}, indent=2))
    else:
        render_claim_text(args.claim, requirements)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
