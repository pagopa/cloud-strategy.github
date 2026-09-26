---
name: internal-review-code
description: Use when reviewing a branch, pull request, work-in-progress diff, or code-focused change before merge or follow-up action.
---

# Internal Review Code

## When to use

Use when reviewing a code-focused branch, pull request, work-in-progress diff,
or explicit read-only code target before merge or a separately authorized
follow-up.

## Review engine

Use `/addyosmani-code-review-and-quality` as the complete and sole review
engine. The engine owns review reasoning, severity, and the substantive review
standard. This wrapper owns repository preflight, target boundaries, the
ordered repository review, escalation rules, the public chat projection, and
final validation. Do not restate the engine's review axes, procedure, approval
standard, or finding categories.

Security stays inside the engine's security axis for the whole review pass. A
readability or complexity correction may be proposed, but no separate
simplification runtime is loaded.

## Boundaries

- The review is report-only. During the review pass, do not edit files, apply
  fixes, or author plans. Planning, remediation, and other state-changing
  follow-ups require a separate explicit request outside the current review.
- Read the spec, task, and tests before implementation when those sources
  exist. Review only the requested code surface and immediate evidence.

## Review preflight

Before substantive review, resolve the concrete, non-empty diff or explicit
read-only code target and fully load the declared review engine from its
resolved source. Record the target identity, target fingerprint, engine
identity, and source.

If the target is empty or the engine identity or resolved source cannot be
confirmed, stop with `REVIEW BLOCKED` and name the missing evidence. When the
fixed point or other context is missing, state the evidence gap.

## Ordered repository review

Run this sequence after the review preflight:

1. Resolve the fixed point or explicit read-only target once. Fail on a bad
   reference or empty target, and record target identity.
2. Record the target fingerprint, commit list when applicable, requested code
   surface, and impacted-validation surface.
3. Discover repository Standards sources and the originating Spec sources or
   task source. Cite them or record `to confirm`.
4. Run the engine without restating its five review axes.
5. Compare the diff against missing/partial requirements, wrong
   implementation, and scope creep.
6. Derive concrete adversarial probes from the changed contracts, assumptions,
   boundaries, and observed evidence.
7. Apply green-test anchoring: treat green tests as evidence only and ask
   which defect classes they would fail to catch.
8. Run a final coverage counter-analysis before approval and project severity
   to `BLOCKER`, `IMPORTANT`, and `SUGGESTION`.

## GitHub Actions contributors

When the read-only target includes `.github/workflows/**` or
`.github/actions/**/action.y*ml`, invoke `/internal-github` with the minimal
envelope in
[the contributor protocol](references/actions-contributor-protocol.md). The
gateway selects `internal-github-actions` as the single domain contributor.
Do not invoke the specialist directly. Keep workflow and composite-action
observations scoped to the changed surfaces; unrelated code invokes no
contributor.

Contributors are bounded observers inside this review flow. They may return
domain observations, changed contract surfaces, execution-chain probes,
applicable validations, compatibility risks, and evidence gaps. Pass those
observations into the one engine review. The wrapper retains target preflight,
provenance, the differential sequence, coverage counter-analysis, severity
projection, and the exact public verdicts. Contributors do not emit a verdict,
severity, approval, merge decision, remediation plan, or replacement review
procedure.

For workflow and composite targets, inspect linked static evidence from the
event through the workflow, reusable workflow or job permissions/environment,
composite action, repository script, artifact, or external-system boundary
when those links are present. Static review does not establish live runner
health or runtime behavior; route that evidence to the appropriate operations
owner and record the gap.

For a separate non-review GitHub follow-up, invoke `/internal-github` with the
same envelope and the follow-up as `deliverable`. Keep that follow-up
report-only and separate from this review's verdict. The gateway owns
destination selection and parent exclusion; do not add a second routing table.

## Public projection

Start with exactly four fields in this order:

- `🔎`: localized verdict and counts by severity.
- `📌`: one sentence explaining why that verdict follows.
- `🧪`: reviewed scope, completed validation, and material evidence gaps.
- `👉`: one user action and the consequence of accepting it.

The verdict in `🔎` must be exactly one of:

- `MERGE READY` for an approval result.
- `CHANGES REQUIRED` when blocking findings remain.
- `REVIEW BLOCKED` when the preflight evidence is insufficient to conduct the
  review.

Map each engine category to a projection label with this table:

| Engine category | Projection label | Rule |
| --- | --- | --- |
| Critical | `BLOCKER` | Blocking finding. |
| Required change | `BLOCKER` | Blocking required change by default. |
| Optional / Consider | `SUGGESTION` | Non-blocking suggestion. |
| Nit | `SUGGESTION` | Non-blocking suggestion. |
| FYI | — | Omit unless it changes the verdict. |

Use `IMPORTANT` for a correction or follow-up that does not independently
block merge. It is not a third undefined severity scale.

This mapping depends on the imported engine's categories. After an engine
refresh, run `python3 scripts/check_engine_contract.py` from this bundle and
treat any reported drift as `REVIEW BLOCKED` until the mapping is realigned.

For each material finding:

- Preserve `Location`, `Evidence`, `Impact`, `Correction`, and
  `Expected verification` when closure is not obvious.
- Number public finding identifiers by label, such as `BLOCKER-1`,
  `IMPORTANT-1`, and `SUGGESTION-1`.
- Show every blocking and important finding, and consolidate equivalent
  findings.
- Mark uncertainty inline as `to confirm`.

Use this emoji-structured skeleton so the reader sees the report layout at a
glance. Omit empty severity sections; keep the label words, because an emoji
never carries meaning alone.

```markdown
🔎 **CHANGES REQUIRED** · 🚫 1 BLOCKER · ⚠️ 1 IMPORTANT · 💡 1 SUGGESTION
📌 <one sentence: why this verdict follows>
🧪 <reviewed scope, completed validation, material evidence gaps>
👉 <one user action and the consequence of accepting it>

## 🚫 Blockers

### BLOCKER-1: <short title>

- 📍 **Location:** `path:line`
- 🔬 **Evidence:** <observed fact or cited source>
- 💥 **Impact:** <consequence if merged as is>
- 🛠️ **Correction:** <smallest correct change, report-only>
- ✅ **Expected verification:** <closing check, when not obvious>

## ⚠️ Important

## 💡 Suggestions

ℹ️ No changes were applied.
```

Keep internal review details hidden unless they alter the verdict. State that
no changes were applied. For request-changes results, invite the user to
manually select named finding IDs for a separately authorized plan-only
follow-up. Approval results state that no user action is required.

## Completion criteria

Before reporting, verify that:

- The target is resolved and non-empty.
- The engine's categories are used without a second severity scale.
- Claims are source-backed or marked as explicit evidence gaps.
- Every blocking and important finding is preserved.
- The report stays within the target scope, the review escalation boundary,
  and the separate follow-up boundary.
- The report contains one boundary-safe next action.
