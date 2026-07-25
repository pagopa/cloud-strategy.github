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
GATE_ROWS = (
    "bounded-evidence",
    "complexity-cost",
    "initial-idea-ordering",
    "clarification",
    "critical-challenge",
    "readiness-brief",
    "execution",
    "validation",
    "final-evidence",
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
            "method": "internal-tdd",
            "evidence": "Use internal-tdd to show the failing-then-passing seam, or state why it could not be run.",
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
    gate_parser.add_argument("--needs-clarification", action="store_true")
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


def build_gate_evidence(
    *,
    gate_outcome: str,
    validation_path: str,
    validation_gap: str,
    clarification_required: bool,
    stop_reasons: list[str],
) -> list[dict[str, object]]:
    validation_evidence = (
        validation_path
        or (f"State validation gap: {validation_gap}" if validation_gap else "Name the focused validation path.")
    )
    stop_reason_text = ", ".join(stop_reasons) if stop_reasons else "stop reason"

    if gate_outcome == "trivial-skip":
        required_rows = {"bounded-evidence", "validation", "final-evidence"}
        expected_by_gate = {
            "bounded-evidence": "Nearest local evidence proving the task stays tiny and local.",
            "complexity-cost": "Not required for trivial-skip.",
            "initial-idea-ordering": "Not required for trivial-skip.",
            "clarification": "Not required for trivial-skip.",
            "critical-challenge": "Not required for trivial-skip.",
            "readiness-brief": "Not required for trivial-skip.",
            "execution": "Not required for trivial-skip.",
            "validation": validation_evidence,
            "final-evidence": "Fresh evidence supporting the final claim or the exact remaining gap.",
        }
    elif gate_outcome == "stop-with-reason":
        required_rows = {"bounded-evidence", "complexity-cost"}
        expected_by_gate = {
            "bounded-evidence": "Nearest local evidence showing why the task cannot stay simple.",
            "complexity-cost": f"Blocked reason: {stop_reason_text}.",
            "initial-idea-ordering": "Not required after stop-with-reason.",
            "clarification": "Not required after stop-with-reason unless the stop reason is a missing answer.",
            "critical-challenge": "Not required after stop-with-reason.",
            "readiness-brief": "Not required after stop-with-reason.",
            "execution": "Not claimable after stop-with-reason; record the blocker instead.",
            "validation": validation_evidence,
            "final-evidence": "Not claimable after stop-with-reason; record the blocker instead.",
        }
    else:
        expected_by_gate = {
            "bounded-evidence": "Nearest local evidence proving the target, scope, and owner.",
            "complexity-cost": "Why the task still fits one bounded run.",
            "initial-idea-ordering": "Completed local ordering from original request through stop signal.",
            "clarification": "Explicit question and answer only if one bounded clarification was needed.",
            "critical-challenge": "Fresh challenge outcome recorded before non-trivial action.",
            "readiness-brief": "Concrete local readiness brief with scope, validation path, risk, and stop conditions.",
            "execution": "Files touched or actions taken, tied to the active lane.",
            "validation": validation_evidence,
            "final-evidence": "Fresh evidence supporting completion, readiness, passing, fixed, or no-gap claims.",
        }
        required_rows = set(GATE_ROWS)
        if not clarification_required:
            required_rows.remove("clarification")

    return [
        {
            "gate": gate,
            "required": gate in required_rows,
            "expected_evidence": expected_by_gate[gate],
        }
        for gate in GATE_ROWS
    ]


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
    needs_clarification: bool = False,
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
        "executable_behavior": "Load internal-tdd before implementation when executable or evaluable behavior changes and a useful seam exists.",
        "validation_path": focused_validation_path,
        "main_risk": main_risk,
        "stop_conditions": "Stop for complexity, cost, ambiguity, safety, approval, or validation gaps.",
        "approval": approval,
    }
    if gate_outcome == "trivial-skip":
        gate_evidence = {
            "validation": focused_validation_path,
            "final_evidence": "Fresh evidence supporting the trivial claim.",
        }
    else:
        gate_evidence = build_gate_evidence(
            gate_outcome=gate_outcome,
            validation_path=validation_path,
            validation_gap=validation_gap,
            clarification_required=needs_clarification,
            stop_reasons=stop_reasons,
        )

    return {
        "gate_outcome": gate_outcome,
        "next_action": "stop" if gate_outcome == "stop-with-reason" else "execute",
        "lane": resolved_lane,
        "reason_codes": stop_reasons,
        "needs_explicit_approval": gate_outcome != "trivial-skip",
        "readiness_brief": readiness_brief,
        "gate_evidence": gate_evidence,
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
    print("🧭 Quick plan")
    print(f"🎯 Goal: {brief['task']}")
    print(f"🛠️ Change: {brief['scope']} {brief['approach']}")
    print(f"🧪 Check: {brief['validation_path']}")

    if decision["next_action"] == "stop":
        print(
            f"⚠️ Blocked: {brief['main_risk']}. "
            "✈️ Action: choose how to resolve this before execution."
        )
    elif decision["needs_explicit_approval"]:
        print("✈️ Action: Confirm before non-trivial work starts.")


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
            needs_clarification=args.needs_clarification,
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
