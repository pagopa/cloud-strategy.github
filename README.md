# cloud-strategy.github

Source repository for reusable GitHub Copilot governance and customization assets.

- Start with [AGENTS.md](AGENTS.md) for the repository-wide bridge and precedence model.
- Use [.github/README.md](.github/README.md) for catalog orientation.
- Use [.github/INVENTORY.md](.github/INVENTORY.md) for the exact live catalog.

## Validation

Run `make docs-lint` to validate repository Markdown. Run
`make github-catalog-validation` to validate the GitHub catalog.

No diagram is provided because this entry point routes readers to policy and
catalog documentation; current component and flow relationships belong in
[docs/architecture.md](docs/architecture.md).
