# Repository Knowledge Documents

This directory holds consumer-local repository knowledge for humans and AI
agents. The files are descriptive and evidence-based. They do not override
binding policy in `AGENTS.md`, `.github/copilot-instructions.md`,
`.github/instructions/copilot-code-review.instructions.md`, skills,
agents, validators, or owned files.

## Required Documents

| File | Primary function | Must not become |
| --- | --- | --- |
| `docs/repository-context.md` | Repository purpose, responsibilities, stakeholders, goals, and vocabulary. | An architecture spec, technology inventory, or policy owner. |
| `docs/architecture.md` | Current boundaries, components, interfaces, flows, and risks. | Proposed architecture presented as current state or a policy file. |
| `docs/tech.md` | Runtimes, tooling, dependencies, and technical constraints. | A lockfile mirror or universal technical policy owner. |
| `docs/structure.md` | Top-level layout, path responsibilities, and generated vs authored boundaries. | A complete inventory dump or architecture narrative. |

## Diagram Standard

When a diagram clarifies relationships that prose alone does not, use Mermaid.
Keep diagrams small and directly tied to current repository evidence.

## Question Routing

- What does this repository do and why: `docs/repository-context.md`
- How components and flows are organized: `docs/architecture.md`
- Which technologies and validators are in use: `docs/tech.md`
- Where content belongs in the tree: `docs/structure.md`

## Maintenance Expectations

- Update the smallest valid document when repository evidence changes.
- Keep unknown facts explicit as `Unknown / To verify`.
- Link to canonical owners instead of duplicating binding policy.
