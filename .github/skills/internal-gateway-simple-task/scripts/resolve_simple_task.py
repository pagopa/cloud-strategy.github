#!/usr/bin/env python3
"""Deterministic gate and claim helper for internal-gateway-simple-task."""

from __future__ import annotations

import argparse
import json
import re


DEPTH_KEYWORDS = ("full", "idea", "complete")
TRIVIAL_KINDS = ("local-answer", "tiny-edit", "focused-read", "validator-run")
LANES = ("answer", "edit", "diagnose", "validate", "unspecified")
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
    "no-gap",
    "performance-improved",
    "readiness",
    "validator-passes",
)

CLAIM_REQUIREMENTS = {
    "fixed": [
        {
            "method": "reproduce-loop",
            "evidence": "Re-run the original loop, or state the exact blocker.",
        },
        {
            "method": "scope-check",
            "evidence": "Confirm every in-scope item is closed or explicitly deferred.",
        },
        {
            "method": "superpowers-verification-before-completion",
            "evidence": "Use fresh validation evidence, not intent or stale output.",
        },
    ],
    "covered": [
        {
            "method": "test-first",
            "evidence": "Show the failing-then-passing seam, or state why it could not be run.",
        },
        {
            "method": "scope-check",
            "evidence": "Confirm the changed behavior and in-scope files are fully covered.",
        },
        {
            "method": "superpowers-verification-before-completion",
            "evidence": "Use fresh validation evidence, not intent or stale output.",
        },
    ],
    "performance-improved": [
        {
            "method": "measurement-compare",
            "evidence": "Compare baseline and after evidence from the same measurement class.",
        },
        {
            "method": "scope-check",
            "evidence": "Confirm no unverified tradeoff remains inside the touched scope.",
        },
        {
            "method": "superpowers-verification-before-completion",
            "evidence": "Use fresh validation evidence, not intent or stale output.",
        },
    ],
    "completion": [
        {
            "method": "scope-check",
            "evidence": "Confirm every in-scope source item is closed with observable evidence.",
        },
        {
            "method": "superpowers-verification-before-completion",
            "evidence": "Use fresh validation evidence before the completion claim.",
        },
    ],
    "readiness": [
        {
            "method": "scope-check",
            "evidence": "Confirm all required work is closed and no stop condition remains open.",
        },
        {
            "method": "superpowers-verification-before-completion",
            "evidence": "Use fresh validation evidence before the readiness claim.",
        },
    ],
    "validator-passes": [
        {
            "method": "rerun-validator",
            "evidence": "Re-run the validator and read fresh output before the claim.",
        },
        {
            "method": "superpowers-verification-before-completion",
            "evidence": "Use fresh validation evidence before the passing claim.",
        },
    ],
    "no-gap": [
        {
            "method": "scope-check",
            "evidence": "Confirm no in-scope item, validation gap, or stop condition remains open.",
        },
        {
            "method": "superpowers-verification-before-completion",
            "evidence": "Use fresh validation evidence before the no-gap claim.",
        },
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic gate and claim helper for internal-gateway-simple-task."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gate_parser = subparsers.add_parser("gate", help="Classify the gate from normalized facts.")
    gate_parser.add_argument("--task", default="unspecified task")
    gate_parser.add_argument("--lane", choices=LANES, default="unspecified")
    gate_parser.add_argument("--trivial-kind", choices=TRIVIAL_KINDS)
    gate_parser.add_argument("--prompt", default="")
    gate_parser.add_argument(
        "--depth-keyword",
        action="append",
        choices=DEPTH_KEYWORDS,
        default=[],
    )
    gate_parser.add_argument(
        "--risk",
        action="append",
        choices=MATERIAL_RISKS,
        default=[],
    )
    gate_parser.add_argument("--needs-plan", action="store_true")
    gate_parser.add_argument("--needs-review", action="store_true")
    gate_parser.add_argument("--needs-critical", action="store_true")
    gate_parser.add_argument("--owner-ambiguous", action="store_true")
    gate_parser.add_argument("--clarification-overflow", action="store_true")
    gate_parser.add_argument("--validation-obvious", action="store_true")
    gate_parser.add_argument("--validation-path", default="")
    gate_parser.add_argument("--validation-gap", default="")
    gate_parser.add_argument("--format", choices=("text", "json"), default="text")

    claim_parser = subparsers.add_parser(
        "claim", help="Resolve evidence gates for strong status claims."
    )
    claim_parser.add_argument(
        "--claim",
        action="append",
        choices=CLAIMS,
        required=True,
    )
    claim_parser.add_argument("--format", choices=("text", "json"), default="text")
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
    mapping = {
        "local-answer": "answer",
        "focused-read": "answer",
        "tiny-edit": "edit",
        "validator-run": "validate",
    }
    return mapping.get(trivial_kind or "", "unspecified")


def build_gate_decision(
    *,
    task: str,
    lane: str,
    trivial_kind: str | None,
    prompt: str,
    depth_keywords: list[str],
    risks: list[str],
    needs_plan: bool,
    needs_review: bool,
    needs_critical: bool,
    owner_ambiguous: bool,
    clarification_overflow: bool,
    validation_obvious: bool,
    validation_path: str,
    validation_gap: str,
) -> dict[str, object]:
    resolved_depth_keywords = detect_depth_keywords(prompt, depth_keywords)
    resolved_risks = sorted(set(risks))
    resolved_lane = infer_lane(lane, trivial_kind)
    stop_reasons: list[str] = []
    stop_for_material_boundary = bool(validation_gap) and any(
        risk in {"architecture", "cross-file", "governance", "rollout"}
        for risk in resolved_risks
    )

    if needs_plan:
        stop_reasons.append("plan-recommended")
    if needs_review:
        stop_reasons.append("review-shaped")
    if needs_critical:
        stop_reasons.append("critical-challenge-needed")
    if owner_ambiguous:
        stop_reasons.append("owner-ambiguous")
    if clarification_overflow:
        stop_reasons.append("clarification-overflow")
    for keyword in resolved_depth_keywords:
        stop_reasons.append(f"depth-keyword:{keyword}")
    for risk in resolved_risks:
        stop_reasons.append(f"material-risk:{risk}")
    if stop_for_material_boundary:
        stop_reasons.append("material-boundary-break")

    if (
        needs_plan
        or needs_review
        or owner_ambiguous
        or clarification_overflow
        or stop_for_material_boundary
    ):
        gate_outcome = "stop-with-reason"
    elif (
        trivial_kind in TRIVIAL_KINDS
        and not resolved_depth_keywords
        and not resolved_risks
        and not needs_critical
        and (validation_obvious or bool(validation_path) or bool(validation_gap))
    ):
        gate_outcome = "trivial-skip"
        stop_reasons.append(f"trivial-kind:{trivial_kind}")
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

    if gate_outcome == "trivial-skip":
        main_risk = "Task stays local and validation is already bounded."
    elif resolved_risks:
        main_risk = "Material risk: " + ", ".join(resolved_risks)
    elif resolved_depth_keywords:
        main_risk = "Depth keyword present: " + ", ".join(resolved_depth_keywords)
    elif needs_critical:
        main_risk = "Non-trivial work needs critical challenge before action."
    else:
        main_risk = "Task still fits one bounded run but needs the full gate before action."

    if gate_outcome == "stop-with-reason":
        approval = "do not execute; wait for a user decision after reporting the stop reason"
    else:
        approval = "explicit user approval before non-trivial operational work"

    readiness_brief = {
        "task": task,
        "goal": "Complete the current bounded task in one run when safe.",
        "scope": f"Single-lane {resolved_lane} work." if resolved_lane != "unspecified" else "Single-lane work.",
        "anti_scope": "No staged workflow expansion, no hidden delegation, no speculative side work.",
        "files_expected": "Name only the files proven by local evidence.",
        "approach": "Use the smallest coherent move that preserves validation coverage.",
        "executable_behavior": "Use the generic test-first loop when behavior changes and a useful seam exists.",
        "validation_path": focused_validation_path,
        "main_risk": main_risk,
        "stop_conditions": "Stop for complexity, cost, ambiguity, safety, approval, or validation gaps.",
        "approval": approval,
    }

    return {
        "gate_outcome": gate_outcome,
        "next_action": "stop" if gate_outcome == "stop-with-reason" else "execute",
        "lane": resolved_lane,
        "reason_codes": stop_reasons,
        "needs_explicit_approval": gate_outcome != "trivial-skip",
        "readiness_brief": readiness_brief,
    }


def resolve_claim_requirements(claims: list[str]) -> list[dict[str, str]]:
    ordered: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for claim in claims:
        for requirement in CLAIM_REQUIREMENTS[claim]:
            key = (requirement["method"], requirement["evidence"])
            if key in seen:
                continue
            seen.add(key)
            ordered.append(requirement)
    return ordered


def render_gate_text(decision: dict[str, object]) -> None:
    brief = decision["readiness_brief"]
    print(f"Gate outcome: {decision['gate_outcome']}")
    print(f"Next action: {decision['next_action']}")
    print(f"Lane: {decision['lane']}")
    if decision["reason_codes"]:
        print("Reason codes:")
        for reason in decision["reason_codes"]:
            print(f"- {reason}")
    print("Readiness Brief:")
    print(f"- Task: {brief['task']}")
    print(f"- Goal: {brief['goal']}")
    print(f"- Scope: {brief['scope']}")
    print(f"- Anti-scope: {brief['anti_scope']}")
    print(f"- Files expected: {brief['files_expected']}")
    print(f"- Approach: {brief['approach']}")
    print(f"- Executable behavior: {brief['executable_behavior']}")
    print(f"- Validation path: {brief['validation_path']}")
    print(f"- Main risk: {brief['main_risk']}")
    print(f"- Stop conditions: {brief['stop_conditions']}")
    print(f"- Approval: {brief['approval']}")


def render_claim_text(claims: list[str], requirements: list[dict[str, str]]) -> None:
    print("Claims: " + ", ".join(claims))
    for requirement in requirements:
        print(f"- {requirement['method']}: {requirement['evidence']}")


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
