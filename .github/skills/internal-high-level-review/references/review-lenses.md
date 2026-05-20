# Review Lenses

Use this reference when review mode needs tiered lenses without creating new
persona agents. The wrapper stays thin; each lens maps to an existing skill.

## Source Patterns

- Comparative source: `tmp/external-comparison/compound-engineering-plugin/plugins/compound-engineering/skills/ce-code-review/SKILL.md`.
- Comparative source: `tmp/external-comparison/gstack/review/SKILL.md`.
- Adopt tiering and confidence calibration only. Reject persona-as-agent catalog
  expansion for this repository.

## Always-on Lenses

| Lens | Trigger | Owner skill | Output |
| --- | --- | --- | --- |
| Code defects | Any code, script, config, test, or policy diff under review. | `internal-code-review` | Defect-first findings with file evidence and fix route. |
| Systems fit | Any review that needs workflow, ownership, architecture, or blind-spot evidence. | `internal-high-level-review` | Systems findings, evidence gaps, scope drift, and residual risk. |

## Cross-cutting Lenses

| Lens | Trigger | Owner skill | Output |
| --- | --- | --- | --- |
| Delivery and operations | Workflows, release safety, operational readiness, incidents, rollout, or lifecycle changes. | `internal-devops-core-principles` | Delivery risk and readiness notes. |
| Performance | User reports slowness, the diff changes hot paths, unbounded loops, caching, batching, concurrency, or large data flow. | `internal-performance-optimization` | Measured or clearly evidenced performance risk. |
| Object collaboration | The diff changes class boundaries, construction logic, polymorphic behavior, or complex branching in object-oriented code. | `internal-oop-design-patterns` | Pattern-fit findings and simpler collaboration routes. |

## Stack-specific Lenses

| Trigger | Owner skill |
| --- | --- |
| `**/*.py` under reusable package or app code | `internal-project-python` |
| Standalone Python scripts, CLIs, or operator tools | `internal-script-python` |
| `**/*.js`, `**/*.cjs`, `**/*.mjs`, `**/*.ts`, `**/*.tsx`, `package.json`, or `tsconfig.json` | `internal-project-nodejs` |
| `**/*.java`, `pom.xml`, `build.gradle`, or `build.gradle.kts` | `internal-project-java` |
| `**/*.sh` standalone scripts | `internal-script-bash` |
| `**/*.tf` | `internal-terraform` |
| Dockerfiles, Compose files, or `.dockerignore` | `internal-docker` |
| Kubernetes manifests, Helm templates, or deployment YAML under Kubernetes paths | `internal-kubernetes` or `internal-kubernetes-deployment` |
| GitHub Actions workflows | `internal-github-actions` |
| Composite actions under `.github/actions/**/action.y*ml` | `internal-github-action-composite` |

## Confidence Calibration

Use severity and confidence together. Severity answers impact. Confidence answers
how strongly the evidence supports the finding.

| Severity | Meaning |
| --- | --- |
| `info` | Non-blocking context or evidence note. |
| `low` | Low-risk maintainability, clarity, or test gap. |
| `medium` | Plausible regression, contract weakness, or missing validation. |
| `high` | Likely user-visible break, broken owner contract, or serious validation gap. |
| `critical` | Security flaw, data loss, severe correctness failure, or unsafe automation. |

| Confidence | Meaning | Reporting rule |
| --- | --- | --- |
| `speculative` | The concern lacks direct evidence. | Report only as an evidence gap, not as an actionable finding. |
| `plausible` | The pattern is credible but still needs verification. | Include with caveat and route to verification. |
| `likely` | Evidence strongly supports the finding. | Include as a normal finding. |
| `verified` | File, line, diff, or validator evidence proves the issue. | Include and prioritize by severity. |

`critical` findings require `likely` or `verified` confidence and concrete file,
line, diff, or validator evidence.

## Finding Shape

Use this compact shape for every actionable finding:

```text
[severity=<info|low|medium|high|critical>] [confidence=<speculative|plausible|likely|verified>]
Evidence: <file, line, diff, command, or explicit gap>
Issue: <what is wrong>
Causal layer: <why it happens>
Route: <delivery, planning, critical, or defer with owner>
```

Do not use `internal-security-review` as an active owner until promotion creates
that skill. Route security-specific gaps through the closest existing owner and
state the promotion gap.
