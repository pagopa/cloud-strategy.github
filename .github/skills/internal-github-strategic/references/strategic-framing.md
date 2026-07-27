# GitHub Strategic Framing Reference

Use this reference when a GitHub decision needs worked lens combinations,
decision-note depth, or a comparison shape.

## Common lens combinations

| Situation | Start with | Add only if needed |
| --- | --- | --- |
| Enterprise or repo-model choice | governance, maintainability | FinOps, BC/DR |
| Automation or integration choice | security, governance | runner model, blast radius |
| Copilot rollout or licensing choice | Copilot, FinOps | governance, compliance |
| Runner-platform decision | runner model, operations | FinOps, BC/DR |
| High-risk workflow or release change | rollout and rollback, blast radius | operations, governance |

## Signals for another lens

- Spend or licensing could change the recommendation: add `FinOps`.
- Permissions, Apps, rulesets, OIDC, or environments change: add `governance`.
- Runner, audit, or validation burden changes: add `operations`.
- Delivery continuity or recovery posture changes: add `BC/DR`.
- Developer workflow or repository shape changes: add `maintainability`.

## Worked decision shapes

### Enterprise or repo-model choice

| Situation | Lenses | Recommendation shape |
| --- | --- | --- |
| Team is choosing mono-repo versus multi-repo | maintainability, governance | Compare developer workflow, ruleset scope, and ownership blast radius. |
| Organization layout or repository ownership is unclear | governance, blast radius | Compare centralized and delegated ownership; name the smallest safe rollout unit. |
| Enterprise-level rollout is still forming | governance, FinOps | Compare entitlement, operating boundaries, and support model before implementation detail. |

### Apps, automation trust, or runner choice

| Situation | Lenses | Recommendation shape |
| --- | --- | --- |
| Automation could use a GitHub App, Actions token, or external integration | security, governance | Compare trust boundary, permission surface, and audit burden. |
| Runner platform is undecided | runner model, operations | Compare managed convenience against fleet ownership and continuity expectations. |
| OIDC is considered mainly to remove secrets | security, governance | Keep trust design, scope, and rollout risk explicit. |

### Copilot rollout or licensing choice

| Situation | Lenses | Recommendation shape |
| --- | --- | --- |
| Copilot rollout is limited by budget or policy | Copilot, FinOps | Compare broad rollout against staged enablement and governance implications. |
| A team wants a narrower Copilot pilot | Copilot, governance | Keep policy, visibility, and exception handling explicit. |
| Enterprise enablement direction is forming | Copilot, compliance | Separate entitlement decisions from repository-permission design. |

## Decision note pattern

1. Decision statement: what GitHub choice is being made.
2. Assumptions: what organization model, runner posture, compliance needs, or
   licensing limits matter.
3. Viable options: two or three realistic GitHub-local paths.
4. Recommendation: which option wins and why.
5. Tradeoffs and blast radius: what improves, what gets harder, and what is
   difficult to reverse.
6. Validation need: which current fact, proof, or test remains before action.

## Depth control

- Stay in `Quick answer` when one option is clearly better and downside is
  local.
- Use `Decision note` when at least two viable options remain or the choice
  changes trust, continuity, repository shape, or licensing posture.
- Use `Deep analysis` when explicitly requested or when the risk profile makes
  a short comparison unsafe.
