---
description: Baseline standards for GitHub Actions workflows and composite actions with SHA pinning, least privilege, and deterministic execution.
applyTo: "**/workflows/**,**/actions/**/action.y*ml"
---

# GitHub Actions Instructions

## Security baseline
- Prefer OIDC over long-lived secrets.
- Pin actions to full-length commit SHAs with adjacent release comments and upstream release URLs.
- Pin `docker://` references and workflow container images by digest.
- When an image is pinned by digest, keep the human-readable tag or version in an adjacent comment or nearby reference.
- Keep `permissions` minimal.
- Start with `contents: read` and add write scopes only when the job requires them.
- Avoid `pull_request_target` for untrusted code.
- Pass secrets only through `secrets.*` or protected environments; never hardcode them in `env`.

## Family baseline
- Use clear English step names and deterministic outputs.
- Set explicit `timeout-minutes` for workflows that could otherwise hang.
- Set `concurrency` when jobs can conflict on a shared target.
- Prefer reusable workflows (`workflow_call`) for repeated job orchestration inside one repository.
- Prefer smaller jobs with explicit `needs` over monolithic workflows when phases are logically separate.
- Use `if` conditions deliberately for branch, event, and environment-specific execution.
- Keep cache and artifact usage explicit, deterministic, and scoped to real reuse.
- Use self-hosted runners only for justified hardware, network, or cost reasons, and note the security and maintenance tradeoff.

## Use the skill for deeper guidance
- Load `.github/skills/internal-github-actions/SKILL.md` for workflow-vs-reusable-vs-composite decisions, reusable workflow patterns, and examples.
- Keep this instruction as the auto-loaded baseline; keep authoring depth and examples in the skill.
